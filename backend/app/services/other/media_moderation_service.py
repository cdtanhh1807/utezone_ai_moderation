import os
import tempfile
import subprocess
from typing import List, Optional, Dict
from pathlib import Path

from core.ollama_client import get_ollama_client, OllamaSession
from services.other.file_service import FileService


class MediaModerationService:
    """
    Service kiểm duyệt media đính kèm.
    - Ảnh: Gửi trực tiếp qua vision model (qwen2.5vl:7b)
    - Video: Trích xuất 3 frame (đầu, giữa, cuối) -> gửi vision model
    - File khác: Kiểm tra metadata (đuôi file, kích thước)
    """
    
    VISION_MODEL = "qwen2.5vl:7b"
    TEMPERATURE = 0.1
    MAX_TOKENS = 300
    
    SYSTEM_PROMPT_VISION_MODERATION = """Bạn là hệ thống kiểm duyệt hình ảnh cho diễn đàn sinh viên HCMUTE.
Nhiệm vụ: Phân tích hình ảnh/video frame và đánh giá các khía cạnh sau theo thang điểm 0.00 - 1.00:
- nudity: Ảnh khỏa thân, nội dung tình dục (0-1)
- violence: Bạo lực, máu me, vũ khí, hành hung (0-1)
- hate_symbols: Biểu tượng thù địch, cờ/biểu ngữ phân biệt đối xử (0-1)
- drugs: Chất cấm, ma túy, thuốc lá lá (0-1)
- text_in_image: Text trong ảnh có toxic không (0-1)
- gore: Máu me, thi thể, tai nạn kinh hoàng (0-1)

QUY TẮC NGHIÊM NGẶT:
1. Nudity >= 0.60 HOẶC sexual_content >= 0.60 -> REJECTED
2. Violence >= 0.60 HOẶC gore >= 0.60 -> REJECTED
3. Hate_symbols >= 0.60 -> REJECTED
4. Drugs >= 0.70 -> REJECTED
5. Text_in_image >= 0.65 -> REJECTED (nếu text trong ảnh chứa ngôn từ độc hại)
6. Còn lại -> APPROVED

BẮT BUỘC trả về JSON:
{
  "approved": true|false,
  "scores": {
    "nudity": 0.0,
    "violence": 0.0,
    "hate_symbols": 0.0,
    "drugs": 0.0,
    "text_in_image": 0.0,
    "gore": 0.0
  },
  "violated_categories": ["violence"],
  "reason": "Giải thích ngắn gọn bằng tiếng Việt",
  "confidence": 0.92
}"""

    VISION_PROMPT = """KIỂM DUYỆT HÌNH ẢNH/VIDEO:

Đây là {media_type} đính kèm trong bài đăng trên diễn đàn sinh viên HCMUTE.

Hãy phân tích kỹ và trả về JSON theo format đã hướng dẫn.
Nhớ: chỉ có APPROVED hoặc REJECTED. Không có pending."""

    BLOCKED_EXTENSIONS = {
        '.exe', '.bat', '.cmd', '.sh', '.dll', '.bin',
        '.scr', '.msi', '.vbs', '.js', '.jar', '.apk'
    }
    
    MAX_FILE_SIZE_MB = 50
    
    def __init__(self):
        self.ollama = get_ollama_client(
            vision_model=self.VISION_MODEL,
            timeout=120
        )
    
    async def moderate_media(
        self,
        media_files: List[str],
        media_types: Optional[List[str]] = None
    ) -> Dict:
        """
        Kiểm duyệt list media files.
        
        Returns:
            {
                "approved": bool,
                "results": [
                    {"file_id": "...", "approved": bool, "reason": "...", "scores": {...}}
                ],
                "overall_reason": "..."
            }
        """
        if not media_files:
            return {"approved": True, "results": [], "overall_reason": "Không có file đính kèm"}
        
        results = []
        any_rejected = False
        
        for idx, file_id in enumerate(media_files):
            media_type = self._detect_media_type(file_id, media_types[idx] if media_types and idx < len(media_types) else None)
            
            # Kiểm tra metadata trước
            meta_check = self._check_metadata(file_id)
            if not meta_check["approved"]:
                results.append({
                    "file_id": file_id,
                    "approved": False,
                    "reason": meta_check["reason"],
                    "scores": {},
                    "media_type": media_type
                })
                any_rejected = True
                continue
            
            # Kiểm tra nội dung theo loại
            if media_type == "image":
                result = await self._moderate_image(file_id)
            elif media_type == "video":
                result = await self._moderate_video(file_id)
            else:
                result = {
                    "file_id": file_id,
                    "approved": True,
                    "reason": "File đính kèm (không kiểm tra nội dung AI)",
                    "scores": {},
                    "media_type": media_type
                }
            
            results.append(result)
            if not result["approved"]:
                any_rejected = True
        
        rejected_items = [r for r in results if not r["approved"]]
        if rejected_items:
            reasons = [f"{r['file_id']}: {r['reason']}" for r in rejected_items]
            overall_reason = "Phát hiện vi phạm trong file đính kèm: " + "; ".join(reasons)
        else:
            overall_reason = "Tất cả file đính kèm đạt yêu cầu"
        
        return {
            "approved": not any_rejected,
            "results": results,
            "overall_reason": overall_reason
        }
    
    def _detect_media_type(self, file_id: str, explicit_type: Optional[str] = None) -> str:
        if explicit_type:
            return explicit_type.lower()
        
        ext = Path(file_id).suffix.lower()
        image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'}
        video_exts = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm'}
        
        if ext in image_exts:
            return "image"
        elif ext in video_exts:
            return "video"
        else:
            return "file"
    
    def _check_metadata(self, file_id: str) -> Dict:
        ext = Path(file_id).suffix.lower()
        
        if ext in self.BLOCKED_EXTENSIONS:
            return {
                "approved": False,
                "reason": f"Định dạng file {ext} không được phép (nguy cơ bảo mật)"
            }
        
        return {"approved": True, "reason": ""}
    
    async def _moderate_image(self, file_id: str) -> Dict:
        try:
            image_url = FileService.get_file_url(file_id, expires_seconds=300)
            
            prompt = self.VISION_PROMPT.format(media_type="hình ảnh")
            
            async with OllamaSession(self.ollama) as client:
                response = await client.generate_with_image(
                    prompt=prompt,
                    image_urls=[image_url],
                    system=self.SYSTEM_PROMPT_VISION_MODERATION,
                    temperature=self.TEMPERATURE,
                    num_predict=self.MAX_TOKENS
                )
            
            result = self._parse_vision_response(response)
            result["file_id"] = file_id
            result["media_type"] = "image"
            return result
            
        except Exception as e:
            return {
                "file_id": file_id,
                "approved": False,
                "reason": f"Không thể phân tích ảnh: {str(e)}",
                "scores": {},
                "media_type": "image",
                "confidence": 0.0
            }
    
    async def _moderate_video(self, file_id: str) -> Dict:
        try:
            video_url = FileService.get_file_url(file_id, expires_seconds=300)
            
            # Trích xuất frame -> local paths
            frame_paths = await self._extract_video_frames(video_url)
            
            if not frame_paths:
                return {
                    "file_id": file_id,
                    "approved": False,
                    "reason": "Không thể trích xuất frame từ video",
                    "scores": {},
                    "media_type": "video"
                }
            
            prompt = self.VISION_PROMPT.format(media_type="video (các frame trích xuất)")
            
            async with OllamaSession(self.ollama) as client:
                response = await client.generate_with_image(
                    prompt=prompt,
                    image_urls=frame_paths,  # Local paths - OllamaClient v2 hỗ trợ
                    system=self.SYSTEM_PROMPT_VISION_MODERATION,
                    temperature=self.TEMPERATURE,
                    num_predict=self.MAX_TOKENS
                )
            
            result = self._parse_vision_response(response)
            result["file_id"] = file_id
            result["media_type"] = "video"
            
            # Cleanup temp frames
            for fp in frame_paths:
                try:
                    if os.path.exists(fp):
                        os.unlink(fp)
                except:
                    pass
            
            return result
            
        except Exception as e:
            return {
                "file_id": file_id,
                "approved": False,
                "reason": f"Không thể phân tích video: {str(e)}",
                "scores": {},
                "media_type": "video",
                "confidence": 0.0
            }
    
    async def _extract_video_frames(self, video_url: str, num_frames: int = 3) -> List[str]:
        """
        Trích xuất frame từ video URL.
        Yêu cầu ffmpeg được cài đặt trên server.
        
        Returns:
            List các local file path của frame đã trích xuất.
        """
        import aiohttp
        
        frames = []
        tmp_video_path = None
        
        try:
            # Tải video tạm
            async with aiohttp.ClientSession() as session:
                async with session.get(video_url, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                    if resp.status != 200:
                        return frames
                    
                    video_bytes = await resp.read()
                    
                    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_video:
                        tmp_video.write(video_bytes)
                        tmp_video_path = tmp_video.name
            
            # Lấy duration
            duration_cmd = [
                'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', tmp_video_path
            ]
            
            try:
                result = subprocess.run(duration_cmd, capture_output=True, text=True, timeout=10)
                duration = float(result.stdout.strip())
            except:
                duration = 10
            
            # Trích xuất frame tại 10%, 50%, 90%
            positions = [duration * 0.1, duration * 0.5, duration * 0.9]
            
            for i, pos in enumerate(positions):
                frame_path = f"{tmp_video_path}_frame_{i}.jpg"
                cmd = [
                    'ffmpeg', '-y', '-ss', str(pos), '-i', tmp_video_path,
                    '-vframes', '1', '-q:v', '2', frame_path
                ]
                
                try:
                    subprocess.run(cmd, capture_output=True, timeout=15)
                    if os.path.exists(frame_path) and os.path.getsize(frame_path) > 0:
                        frames.append(frame_path)
                except Exception as e:
                    print(f"Frame extraction error at {pos}s: {e}")
                    continue
            
        except Exception as e:
            print(f"Video frame extraction failed: {e}")
        
        finally:
            # Cleanup video temp
            if tmp_video_path and os.path.exists(tmp_video_path):
                try:
                    os.unlink(tmp_video_path)
                except:
                    pass
        
        return frames
    
    def _parse_vision_response(self, raw: str) -> Dict:
        import json, re
        
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                approved = bool(data.get("approved", False))
                scores = data.get("scores", {})
                violated = data.get("violated_categories", [])
                reason = data.get("reason", "")
                confidence = float(data.get("confidence", 0.5))
                
                # Áp ngưỡng cứng
                if scores.get("nudity", 0) >= 0.60 or scores.get("sexual_content", 0) >= 0.60:
                    approved = False
                    if "nudity" not in violated and "sexual_content" not in violated:
                        violated.append("nudity/sexual_content")
                if scores.get("violence", 0) >= 0.60 or scores.get("gore", 0) >= 0.60:
                    approved = False
                    if "violence" not in violated:
                        violated.append("violence")
                if scores.get("hate_symbols", 0) >= 0.60:
                    approved = False
                    if "hate_symbols" not in violated:
                        violated.append("hate_symbols")
                if scores.get("drugs", 0) >= 0.70:
                    approved = False
                    if "drugs" not in violated:
                        violated.append("drugs")
                if scores.get("text_in_image", 0) >= 0.65:
                    approved = False
                    if "text_in_image" not in violated:
                        violated.append("text_in_image")
                
                if not approved and not reason:
                    reason = "Phát hiện nội dung không phù hợp trong hình ảnh/video"
                
                return {
                    "approved": approved,
                    "scores": scores,
                    "violated_categories": violated,
                    "reason": reason if not approved else "",
                    "confidence": confidence
                }
            except:
                pass
        
        raw_lower = raw.lower()
        approved = not any(word in raw_lower for word in ["reject", "từ chối", "vi phạm", "cấm", "không phù hợp"])
        return {
            "approved": approved,
            "scores": {},
            "violated_categories": [],
            "reason": "" if approved else "Phát hiện nội dung đáng ngờ trong hình ảnh",
            "confidence": 0.3
        }


# Singleton
_media_service = None

def get_media_moderation_service() -> MediaModerationService:
    global _media_service
    if _media_service is None:
        _media_service = MediaModerationService()
    return _media_service
