from fastapi import APIRouter, HTTPException, UploadFile, File
from core.ollama_client import OllamaSession, get_ollama_client
from services.other.file_service import FileService
import subprocess
import tempfile
import os
import re
import json
import shutil
import asyncio
from pathlib import Path
from io import BytesIO

router = APIRouter()
VISION_MODEL = "qwen2.5vl:7b"
TEXT_MODEL = "llama3.1:8b"  # hoặc "qwen2.5:7b" nếu muốn tiếng Việt tốt hơn
_ffmpeg_exe = None
_moderation_semaphore = asyncio.Semaphore(1)

# ==================== FFMPEG helpers ====================
def get_ffmpeg_exe():
    global _ffmpeg_exe
    if _ffmpeg_exe:
        return _ffmpeg_exe
    try:
        import imageio_ffmpeg
        _ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        print(f"[FFMPEG] Found: {_ffmpeg_exe}")
        return _ffmpeg_exe
    except ImportError:
        pass
    _ffmpeg_exe = shutil.which("ffmpeg")
    if _ffmpeg_exe:
        print(f"[FFMPEG] Found in PATH: {_ffmpeg_exe}")
        return _ffmpeg_exe
    raise FileNotFoundError("ffmpeg not found")

def get_video_duration(file_path: str) -> float:
    ffmpeg = get_ffmpeg_exe()
    cmd = [ffmpeg, "-i", file_path]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    output = result.stderr + result.stdout
    match = re.search(r"Duration: (\d{2}):(\d{2}):(\d{2}\.\d+)", output)
    if match:
        h, m, s = match.groups()
        return int(h)*3600 + int(m)*60 + float(s)
    raise ValueError("Cannot parse duration")

def extract_text_from_file(file_path: str, file_ext: str) -> str:
    text = ""
    try:
        if file_ext == '.txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
        elif file_ext == '.docx':
            from docx import Document
            doc = Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs])
        elif file_ext == '.pdf':
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
        text = ""
    return text[:5000]

# ==================== MODERATION TEXT (đã cải tiến prompt) ====================
async def _moderate_text_file(file_path: str, filename: str) -> dict:
    ext = os.path.splitext(filename)[1].lower()
    content = extract_text_from_file(file_path, ext)
    if not content.strip():
        return {"approved": True, "reason": "", "scores": {}, "violated_categories": [], "confidence": 0.0}

    async with _moderation_semaphore:
        for attempt in range(2):
            try:
                client = get_ollama_client(model=TEXT_MODEL, timeout=120)
                # PROMPT TỐI ƯU: CHỈ REJECT KHI THỰC SỰ VI PHẠM
                prompt = """Bạn là hệ thống kiểm duyệt nội dung văn bản cho diễn đàn sinh viên.
NHIỆM VỤ: Đánh giá văn bản dưới đây và trả về JSON (duy nhất, không markdown) theo cấu trúc sau:

{
  "approved": true|false,
  "scores": {
    "toxicity": 0.0,
    "hate_speech": 0.0,
    "violence": 0.0,
    "sexual_content": 0.0,
    "harassment": 0.0
  },
  "violated_categories": [],
  "reason": "Lý do ngắn gọn nếu bị từ chối, nếu không thì để trống",
  "confidence": 0.95
}

QUY TẮC CHẤM ĐIỂM:
- toxicity: Nội dung thô tục, chửi thề, xúc phạm (>=0.65 thì REJECT)
- hate_speech: Kích động thù địch, phân biệt chủng tộc, tôn giáo, vùng miền (>=0.65 thì REJECT)
- violence: Đe dọa bạo lực, khuyến khích hành vi bạo lực (>=0.65 thì REJECT)
- sexual_content: Mô tả tường minh hành vi tình dục, ấn dụ khiêu dâm (>=0.65 thì REJECT)
- harassment: Quấy rối, đe dọa cá nhân, bắt nạt (>=0.65 thì REJECT)

QUAN TRỌNG: 
- Các nội dung sau đây KHÔNG được coi là vi phạm: 
  * Danh sách công việc, kế hoạch, task list, ghi chú cá nhân
  * Nội dung học tập, thảo luận về công nghệ, lập trình, khoa học
  * Phân tích, so sánh, đánh giá sản phẩm/dịch vụ (không có lời lẽ tấn công)
  * Tin tức, bài báo, tài liệu tham khảo
  * Câu hỏi, hướng dẫn, giải thích kỹ thuật
- Nếu văn bản không chứa bất kỳ yếu tố nào trong các mục trên với điểm số >=0.65, thì tất cả các điểm số phải là 0.0 và approved = true.
- Hãy phân tích một cách khách quan, không phán xét nội dung bình thường.

VĂN BẢN CẦN KIỂM DUYỆT:
""" + content[:4000]  # giới hạn thêm cho an toàn

                async with OllamaSession(client) as c:
                    response = await c.generate(prompt=prompt, system=prompt, temperature=0.1, num_predict=300)
                print(f"[TEXT_MOD] AI response: {response}")
                result = _parse_moderation_json(response, is_text=True)
                # Nếu parse ra approved = False mà không có scores vi phạm, in cảnh báo
                if not result["approved"] and all(score < 0.65 for score in result["scores"].values()):
                    print(f"[TEXT_MOD] Warning: Rejected but no high scores. Reason: {result['reason']}")
                return result
            except Exception as e:
                print(f"[TEXT_MOD] Attempt {attempt+1} failed: {e}")
                if attempt == 0:
                    await asyncio.sleep(2)
                else:
                    # Fallback: cho phép upload (vì không muốn chặn oan)
                    return {"approved": True, "reason": f"Moderation unavailable: {str(e)}", "scores": {}, "violated_categories": [], "confidence": 0.0}

# ==================== MODERATION IMAGE (giữ nguyên) ====================
async def _moderate_image_file(file_path: str, filename: str) -> dict:
    async with _moderation_semaphore:
        for attempt in range(2):
            try:
                client = get_ollama_client(vision_model=VISION_MODEL, timeout=120)
                prompt = """Bạn là hệ thống kiểm duyệt hình ảnh. Trả về DUY NHẤT JSON (không markdown) theo cấu trúc:
{
  "approved": true|false,
  "scores": {"nudity":0.0,"violence":0.0,"hate_symbols":0.0,"drugs":0.0,"text_in_image":0.0,"gore":0.0},
  "violated_categories": [],
  "reason": "",
  "confidence": 0.92
}
Quy tắc: nudity>=0.6, violence>=0.6, gore>=0.6, hate_symbols>=0.6 -> REJECT; drugs>=0.7 -> REJECT; text_in_image>=0.65 -> REJECT."""
                async with OllamaSession(client) as c:
                    response = await c.generate_with_image(prompt, [file_path], prompt, 0.1, 300)
                return _parse_moderation_json(response)
            except Exception as e:
                print(f"[IMAGE_MOD] Attempt {attempt+1} failed: {e}")
                if attempt == 0:
                    await asyncio.sleep(2)
                else:
                    return {"approved": True, "reason": f"Moderation unavailable: {str(e)}", "scores": {}, "violated_categories": [], "confidence": 0.0}

# ==================== MODERATION VIDEO (giữ nguyên) ====================
async def _moderate_video_file(file_path: str, filename: str) -> dict:
    print(f"[VIDEO_MOD] Start {filename}")
    frame_paths = []
    try:
        duration = get_video_duration(file_path)
        ffmpeg = get_ffmpeg_exe()
        positions = [duration*0.1, duration*0.5, duration*0.9]
        for i, pos in enumerate(positions):
            frame_path = f"{file_path}_frame_{i}.jpg"
            cmd = [ffmpeg, '-y', '-ss', str(pos), '-i', file_path,
                   '-vframes', '1', '-q:v', '2', '-vf', 'scale=640:-1', frame_path]
            await asyncio.to_thread(subprocess.run, cmd, capture_output=True, timeout=30)
            if os.path.exists(frame_path) and os.path.getsize(frame_path) > 100:
                frame_paths.append(frame_path)
                print(f"[VIDEO_MOD] Frame {i+1} OK")
            else:
                print(f"[VIDEO_MOD] Frame {i+1} FAILED")
        if not frame_paths:
            return {"approved": False, "reason": "No frames", "scores": {}, "violated_categories": [], "confidence": 0.0}
        async with _moderation_semaphore:
            for attempt in range(2):
                try:
                    client = get_ollama_client(vision_model=VISION_MODEL, timeout=120)
                    prompt = """Bạn là hệ thống kiểm duyệt video. Xem xét các frame, lấy nội dung xấu nhất. Trả về DUY NHẤT JSON (không markdown) theo cấu trúc giống ảnh."""
                    async with OllamaSession(client) as c:
                        response = await c.generate_with_image(prompt, frame_paths, prompt, 0.1, 300)
                    result = _parse_moderation_json(response)
                    for p in frame_paths:
                        try: os.unlink(p)
                        except: pass
                    return result
                except Exception as e:
                    print(f"[VIDEO_MOD] Attempt {attempt+1} failed: {e}")
                    if attempt == 0:
                        await asyncio.sleep(2)
                    else:
                        for p in frame_paths:
                            try: os.unlink(p)
                            except: pass
                        return {"approved": True, "reason": f"Moderation unavailable: {str(e)}", "scores": {}, "violated_categories": [], "confidence": 0.0}
    except Exception as e:
        for p in frame_paths:
            try: os.unlink(p)
            except: pass
        return {"approved": False, "reason": f"Lỗi: {str(e)}", "scores": {}, "violated_categories": [], "confidence": 0.0}

# ==================== PARSE JSON (có cải thiện) ====================
def _parse_moderation_json(response: str, is_text: bool = False) -> dict:
    response = re.sub(r'^```json\s*', '', response.strip())
    response = re.sub(r'\s*```$', '', response)
    data = None
    try:
        data = json.loads(response)
    except:
        pass
    if isinstance(data, list):
        if not data:
            return {"approved": True, "reason": "No content", "scores": {}, "violated_categories": [], "confidence": 0.5}
        item = data[0]
        if "label" in item:
            label = item["label"].lower()
            safe_keywords = ["không có nội dung xấu", "an toàn", "không vi phạm", "safe", "bình thường"]
            if any(kw in label for kw in safe_keywords):
                return {"approved": True, "reason": "", "scores": {}, "violated_categories": [], "confidence": 0.9}
            else:
                return {"approved": False, "reason": label, "scores": {}, "violated_categories": ["general"], "confidence": 0.8}
        if "scores" in item or "approved" in item:
            data = item
        else:
            return {"approved": True, "reason": "Unknown format, allowed", "scores": {}, "violated_categories": [], "confidence": 0.5}
    if isinstance(data, dict):
        approved = data.get("approved", False)
        scores = data.get("scores", {})
        violated = data.get("violated_categories", [])
        reason = data.get("reason", "")
        if is_text:
            # Kiểm tra ngưỡng dựa trên scores
            for cat in ["toxicity", "hate_speech", "violence", "sexual_content", "harassment"]:
                if scores.get(cat, 0) >= 0.65:
                    approved = False
                    if cat not in violated: violated.append(cat)
        else:
            if scores.get("nudity", 0) >= 0.6: approved = False; violated.append("nudity")
            if scores.get("violence", 0) >= 0.6 or scores.get("gore", 0) >= 0.6: approved = False; violated.append("violence")
            if scores.get("hate_symbols", 0) >= 0.6: approved = False; violated.append("hate_symbols")
            if scores.get("drugs", 0) >= 0.7: approved = False; violated.append("drugs")
            if scores.get("text_in_image", 0) >= 0.65: approved = False; violated.append("text_in_image")
        # Nếu approved=False nhưng tất cả scores < ngưỡng, ưu tiên approve (tránh lỗi AI)
        if not approved and is_text:
            high_scores = [scores.get(cat, 0) for cat in ["toxicity", "hate_speech", "violence", "sexual_content", "harassment"]]
            if max(high_scores) < 0.65:
                approved = True
                violated = []
                reason = ""
        if not approved and not reason:
            reason = "Nội dung vi phạm quy định"
        return {
            "approved": approved,
            "scores": scores,
            "violated_categories": violated,
            "reason": reason if not approved else "",
            "confidence": data.get("confidence", 0.5)
        }
    # Fallback: nếu không parse được JSON, dùng từ khóa an toàn (chỉ để tránh chặn oan)
    lower_resp = response.lower()
    if any(kw in lower_resp for kw in ["không vi phạm", "nội dung phù hợp", "an toàn", "approved"]):
        return {"approved": True, "reason": "Fallback: nội dung an toàn", "scores": {}, "violated_categories": [], "confidence": 0.6}
    return {"approved": False, "reason": "AI không trả về kết quả đánh giá", "scores": {}, "violated_categories": [], "confidence": 0.0}

def _detect_media_type(filename: str, content_type: str) -> str:
    ext = Path(filename).suffix.lower()
    if content_type:
        if content_type.startswith("image/"): return "image"
        if content_type.startswith("video/"): return "video"
    if ext in {'.jpg','.jpeg','.png','.gif','.bmp','.webp'}: return "image"
    if ext in {'.mp4','.avi','.mov','.mkv','.webm'}: return "video"
    if ext in {'.txt','.docx','.pdf','.md','.rtf'}: return "document"
    return "other"

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename or ""
    content_type = file.content_type or ""
    media_type = _detect_media_type(filename, content_type)
    print(f"[UPLOAD] {filename} -> {media_type}")

    file_content = await file.read()
    if len(file_content) == 0:
        raise HTTPException(400, "File rỗng")

    ext = os.path.splitext(filename)[1].lower()
    fd, tmp_path = tempfile.mkstemp(suffix=ext)
    try:
        with os.fdopen(fd, 'wb') as tmp:
            tmp.write(file_content)
            tmp.flush()
            os.fsync(fd)

        if media_type == "image":
            result = await _moderate_image_file(tmp_path, filename)
        elif media_type == "video":
            result = await _moderate_video_file(tmp_path, filename)
        elif media_type == "document":
            result = await _moderate_text_file(tmp_path, filename)
        else:
            result = {"approved": True, "reason": "", "scores": {}, "violated_categories": [], "confidence": 0.0}

        print(f"[UPLOAD] Result: approved={result['approved']}, reason={result['reason']}")

        if not result["approved"]:
            raise HTTPException(400, detail={
                "error": "File không được phép upload",
                "reason": result["reason"],
                "violated_categories": result["violated_categories"]
            })
    finally:
        try:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        except: pass

    file.file = BytesIO(file_content)
    file.size = len(file_content)
    file_id = await FileService.upload_file(file)
    return {"file_id": file_id, "url": FileService.get_file_url(file_id)}

@router.post("/upload/batch")
async def upload_batch(files: list[UploadFile] = File(...)):
    print(f"[BATCH] Processing {len(files)} files")
    results = []
    for idx, f in enumerate(files):
        if idx > 0:
            await asyncio.sleep(1)
        try:
            r = await upload_file(f)
            results.append({"success": True, "data": r})
        except HTTPException as e:
            detail = e.detail if isinstance(e.detail, str) else e.detail.get("reason", str(e.detail))
            results.append({"success": False, "filename": f.filename, "error": detail})
        except Exception as e:
            results.append({"success": False, "filename": f.filename, "error": f"System: {str(e)}"})
    return {
        "success": all(r["success"] for r in results),
        "total": len(files),
        "passed": sum(r["success"] for r in results),
        "rejected": sum(not r["success"] for r in results),
        "results": results
    }

@router.get("/file/{file_id}")
async def get_file(file_id: str):
    return {"url": FileService.get_file_url(file_id)}