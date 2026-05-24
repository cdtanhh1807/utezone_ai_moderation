# meeting/services/moderation_service.py
import json
import os
import asyncio
import subprocess
import re
import shutil
from typing import List, Optional

import httpx
from meeting.services.channel_service import channel_service
from meeting.websocket.manager import ws_manager

# ==================== CONFIGURATION ====================
OPENROUTER_API_KEY = ""
TEXT_MODEL = "z-ai/glm-4.5-air:free"
VISION_MODEL = "google/gemma-4-31b-it:free"

_moderation_semaphore = asyncio.Semaphore(1)

# ==================== HELPER FUNCTIONS ====================
def _get_ffmpeg_exe():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        pass
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return ffmpeg
    raise FileNotFoundError("ffmpeg not found")

def _get_video_duration(file_path: str) -> float:
    ffmpeg = _get_ffmpeg_exe()
    cmd = [ffmpeg, "-i", file_path]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    output = result.stderr + result.stdout
    match = re.search(r"Duration: (\d{2}):(\d{2}):(\d{2}\.\d+)", output)
    if match:
        h, m, s = match.groups()
        return int(h)*3600 + int(m)*60 + float(s)
    raise ValueError("Cannot parse duration")

def _extract_frames(file_path: str, num_frames: int = 3) -> List[str]:
    ffmpeg = _get_ffmpeg_exe()
    duration = _get_video_duration(file_path)
    positions = [duration * (i+1) / (num_frames+1) for i in range(num_frames)]
    frame_paths = []
    for idx, pos in enumerate(positions):
        frame_path = f"{file_path}_frame_{idx}.jpg"
        cmd = [ffmpeg, '-y', '-ss', str(pos), '-i', file_path,
               '-vframes', '1', '-q:v', '2', '-vf', 'scale=640:-1', frame_path]
        subprocess.run(cmd, capture_output=True, timeout=30)
        if os.path.exists(frame_path) and os.path.getsize(frame_path) > 100:
            frame_paths.append(frame_path)
    return frame_paths

def _extract_text_from_file(file_path: str, filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    text = ""
    try:
        if ext == '.txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
        elif ext == '.docx':
            from docx import Document
            doc = Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs])
        elif ext == '.pdf':
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ""
        else:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
    except Exception as e:
        print(f"[EXTRACT] Error: {e}")
    return text[:5000]

# ==================== OPENROUTER CALLS ====================
async def _call_openrouter(prompt: str, model: str, images: Optional[List[str]] = None) -> str:
    """Gọi OpenRouter với text hoặc text+image, trả về raw response text.

    Moderation phải fail-closed: nếu không gọi được AI, bị 429, thiếu API key,
    hoặc response lỗi thì trả approved=false để backend chặn nội dung.
    """
    if not OPENROUTER_API_KEY:
        print("[OpenRouter] Missing OPENROUTER_API_KEY")
        return json.dumps({
            "approved": False,
            "reason": "Thiếu OPENROUTER_API_KEY cho hệ thống kiểm duyệt"
        }, ensure_ascii=False)

    async with _moderation_semaphore:
        last_error = "Service unavailable"

        for attempt in range(4):
            try:
                content = []

                if images:
                    import base64
                    for img_path in images:
                        with open(img_path, "rb") as f:
                            base64_img = base64.b64encode(f.read()).decode()
                            content.append({
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}
                            })

                content.append({"type": "text", "text": prompt})
                messages = [{"role": "user", "content": content}]

                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": model,
                            "messages": messages,
                            "temperature": 0.1,
                            "max_tokens": 500
                        }
                    )

                if response.status_code == 200:
                    data = response.json()
                    result = data["choices"][0]["message"].get("content")
                    print(f"[OpenRouter] Response: {result}")

                    if result is None or not str(result).strip():
                        return json.dumps({
                            "approved": False,
                            "reason": "AI moderation service unavailable: empty response"
                        }, ensure_ascii=False)

                    return result

                if response.status_code == 429:
                    retry_after = 5
                    try:
                        err_data = response.json()
                        retry_after = err_data.get("metadata", {}).get("retry_after_seconds", 5)
                    except Exception:
                        pass

                    last_error = "AI moderation service rate limited"
                    print(f"[OpenRouter] Rate limited, waiting {retry_after}s (attempt {attempt + 1}/4)")
                    await asyncio.sleep(float(retry_after) + 2)
                    continue

                last_error = f"OpenRouter HTTP {response.status_code}"
                print(f"[OpenRouter] HTTP {response.status_code}: {response.text}")
                await asyncio.sleep(2)

            except Exception as e:
                last_error = str(e)
                print(f"[OpenRouter] Attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(2)

        return json.dumps({
            "approved": False,
            "reason": f"AI moderation service unavailable or rate limited: {last_error}"
        }, ensure_ascii=False)

async def _moderate_text_with_llama(content: str, rules_text: str) -> dict:
    prompt = f"""
Bạn là hệ thống kiểm duyệt nội dung văn bản.
Quy tắc của channel: {rules_text}
Hãy đánh giá nội dung sau và trả về JSON duy nhất (không markdown):
{{ "approved": true/false, "reason": "lý do ngắn gọn nếu vi phạm" }}
Nội dung: {content[:4000]}
"""
    response = await _call_openrouter(prompt, TEXT_MODEL)
    print(f"[TEXT_MOD] Raw response: {response}")
    return _parse_moderation_json(response)

async def _moderate_image_with_vision(file_path: str, rules_text: str) -> dict:
    prompt = f"""
Bạn là hệ thống kiểm duyệt hình ảnh. Quy tắc channel: {rules_text}
Đánh giá ảnh này, trả về JSON duy nhất:
{{ "approved": true/false, "reason": "lý do nếu vi phạm" }}
"""
    response = await _call_openrouter(prompt, VISION_MODEL, images=[file_path])
    return _parse_moderation_json(response)

async def _moderate_video_with_vision(file_path: str, rules_text: str) -> dict:
    frames = _extract_frames(file_path, num_frames=3)
    if not frames:
        return {"approved": False, "reason": "AI moderation service unavailable: cannot extract video frames"}
    try:
        prompt = f"""
Bạn là hệ thống kiểm duyệt video. Xem xét các frame (lấy nội dung xấu nhất). Quy tắc: {rules_text}
Trả về JSON duy nhất:
{{ "approved": true/false, "reason": "lý do nếu vi phạm" }}
"""
        response = await _call_openrouter(prompt, VISION_MODEL, images=frames)
        return _parse_moderation_json(response)
    finally:
        for f in frames:
            try: os.unlink(f)
            except: pass

async def _moderate_document_with_vision(file_path: str, filename: str, rules_text: str) -> dict:
    text = _extract_text_from_file(file_path, filename)
    if not text.strip():
        return {"approved": True, "reason": "No text content"}
    return await _moderate_text_with_llama(text, rules_text)

def _parse_moderation_json(response: str) -> dict:
    """Parse JSON moderation từ model.

    Fail-closed: nếu model trả None, markdown lỗi, JSON lỗi, thiếu field approved,
    hoặc định dạng không hợp lệ thì coi là không được duyệt. Các lỗi dạng này
    được gắn reason `AI moderation service unavailable: ...` để controller trả 503,
    không nhầm với nội dung vi phạm thật.
    """
    if response is None or not str(response).strip():
        return {
            "approved": False,
            "reason": "AI moderation service unavailable: empty response"
        }

    response = str(response).strip()
    response = re.sub(r'^```json\s*', '', response)
    response = re.sub(r'^```\s*', '', response)
    response = re.sub(r'\s*```$', '', response)

    try:
        data = json.loads(response)
    except Exception as e:
        print(f"[MOD_PARSE] Parse error: {e}, response={response}")
        return {
            "approved": False,
            "reason": "AI moderation service unavailable: invalid response"
        }

    if isinstance(data, list) and data:
        data = data[0]

    if not isinstance(data, dict):
        return {
            "approved": False,
            "reason": "AI moderation service unavailable: unexpected response format"
        }

    if "approved" not in data:
        return {
            "approved": False,
            "reason": "AI moderation service unavailable: missing approved field"
        }

    approved = data.get("approved")
    if not isinstance(approved, bool):
        return {
            "approved": False,
            "reason": "AI moderation service unavailable: approved field is not boolean"
        }

    reason = data.get("reason") or "Nội dung vi phạm quy tắc channel"

    return {
        "approved": approved,
        "reason": "" if approved else reason
    }

# ==================== MAIN MODERATION ENTRYPOINT ====================
async def moderate_file(
    channel_id: str,
    file_path: str,
    filename: str,
    media_type: str,
    sender_email: str,
    room_id: str,
    message_id: Optional[str] = None
) -> dict:
    rules_obj = await channel_service.get_channel_rules(channel_id)
    if not rules_obj or not rules_obj.enabled:
        return {"approved": True, "reason": "Moderation disabled"}
    if media_type == "image" and "image" not in rules_obj.enabled_types:
        return {"approved": True, "reason": "Image moderation disabled"}
    if media_type == "video" and "video" not in rules_obj.enabled_types:
        return {"approved": True, "reason": "Video moderation disabled"}
    if media_type == "document" and "file" not in rules_obj.enabled_types:
        return {"approved": True, "reason": "File moderation disabled"}
    if media_type == "other":
        return {"approved": True, "reason": "Unsupported media type"}

    rules_text = rules_obj.rules_text
    if not rules_text.strip():
        return {"approved": True, "reason": "No rules defined"}

    try:
        if media_type == "image":
            result = await _moderate_image_with_vision(file_path, rules_text)
        elif media_type == "video":
            result = await _moderate_video_with_vision(file_path, rules_text)
        elif media_type == "document":
            result = await _moderate_document_with_vision(file_path, filename, rules_text)
        else:
            result = {"approved": False, "reason": "Unsupported media type"}

        if not isinstance(result, dict):
            return {"approved": False, "reason": "Kết quả kiểm duyệt không hợp lệ"}

        return {
            "approved": bool(result.get("approved", False)),
            "reason": result.get("reason", "")
        }

    except Exception as e:
        print(f"[FILE_MODERATION_ERROR] {filename}: {e}")
        return {
            "approved": False,
            "reason": f"AI moderation service unavailable: file moderation error: {e}"
        }

async def moderate_text_message(
    channel_id: str,
    message_id: str,
    content: str,
    sender_email: str,
    room_id: str
):
    rules_obj = await channel_service.get_channel_rules(channel_id)
    if not rules_obj or not rules_obj.enabled:
        return
    if "text" not in rules_obj.enabled_types:
        return
    rules_text = rules_obj.rules_text
    if not rules_text.strip():
        return
    moderation = await _moderate_text_with_llama(content, rules_text)
    print(f"[MODERATION] Result: {moderation}")
    if moderation.get("approved", False):
        return
    await channel_service.delete_message(message_id, channel_id)

# Báo cho tất cả client trong channel gỡ message khỏi UI
    await ws_manager.broadcast(channel_id, {
        "type": "message_removed",
        "message_id": message_id,
        "room_id": room_id,
        "user_email": sender_email,
        "reason": moderation.get("reason", "Nội dung vi phạm")
    })
    rule = rules_obj
    violation_count = await channel_service.add_violation(sender_email, channel_id, "text")
    if violation_count >= rule.max_violations:
        action = rule.action
        if action == "kick":
            channel = await channel_service.get_channel(channel_id)
            if channel:
                await channel_service.kick_member(channel_id, channel.owner_email, sender_email)
        elif action == "ban":
            channel = await channel_service.get_channel(channel_id)
            if channel:
                await channel_service.kick_member(channel_id, channel.owner_email, sender_email)
        elif action == "mute" and rule.penalty_time:
            await channel_service.mute_user(sender_email, channel_id, rule.penalty_time)
        await ws_manager.broadcast(channel_id, {
            "type": "user_violation",
            "user_email": sender_email,
            "action": action,
            "reason": moderation.get("reason", "Nội dung vi phạm"),
            "message_id": message_id
        })
    else:
        await ws_manager.broadcast(channel_id, {
            "type": "user_warning",
            "user_email": sender_email,
            "reason": moderation.get("reason", "Nội dung vi phạm"),
            "remaining": rule.max_violations - violation_count,
            "action": rule.action,
            "message_id": message_id
        })