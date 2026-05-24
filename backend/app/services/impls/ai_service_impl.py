import json
import re
import asyncio
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from services.interfaces.ai_service_interface import IAIService
from dto.ai.request.summarize_post_request import SummarizePostRequest
from dto.ai.response.summarize_post_response import SummarizePostResponse
from dto.ai.request.moderate_content_request import ModerateContentRequest
from dto.ai.response.moderate_content_response import ModerateContentResponse, ModerationScores
from repositories.post_repository import PostRepository
from core.database import db
from core.ollama_client import get_ollama_client, OllamaSession
from services.other.file_service import FileService
import logging

logger = logging.getLogger(__name__)

class AIServiceImpl(IAIService):
    MODEL = "llama3.1:8b"
    VISION_MODEL = "qwen2.5vl:7b"
    TEMPERATURE = 0.3
    MAX_TOKENS = 500
    TIMEOUT = 120

    MODERATION_MODEL = "llama3.1:8b"
    MODERATION_TEMPERATURE = 0.05
    MODERATION_MAX_TOKENS = 300

    THRESHOLD_REJECT = 0.65
    THRESHOLD_SPAM = 0.70
    THRESHOLD_SEXUAL = 0.70
    THRESHOLD_VIOLENCE = 0.60

    SYSTEM_PROMPT_SUMMARY = """Bạn là trợ lý AI cho diễn đàn sinh viên Trường Đại học Sư phạm Kỹ thuật Thành phố Hồ Chí Minh (hcmute). 
Tóm tắt bài đăng ngắn gọn, súc tích bằng tiếng Việt trong tối đa 5 câu."""

    SYSTEM_PROMPT_VISION = """Bạn là trợ lý AI cho diễn đàn sinh viên HCMUTE. 
Hãy phân tích bài đăng dựa trên:
1. Tiêu đề và nội dung văn bản
2. Nội dung hình ảnh đính kèm (nếu có)
Tóm tắt ngắn gọn, súc tích bằng tiếng Việt, tối đa 5 câu."""

    SYSTEM_PROMPT_MODERATION = """Bạn là hệ thống kiểm duyệt nội dung AI cho diễn đàn sinh viên HCMUTE.
Nhiệm vụ: Phân tích nội dung và đánh giá các khía cạnh sau theo thang điểm 0.00 - 1.00:
- toxicity: Ngôn từ độc hại, thô tục, xúc phạm
- insult: Lăng mạ, chửi rủa cá nhân/tập thể
- hate_speech: Phát ngôn thù địch, phân biệt đối xử
- harassment: Quấy rối, bắt nạt, đe dọa
- spam: Quảng cáo trái phép, spam link, lặp lại vô nghĩa
- sexual_content: Nội dung tình dục, khiêu dâm
- violence: Bạo lực, đe dọa gây hại thể chất

QUY TẮC NGHIÊM NGẶT:
1. Nếu toxicity >= 0.65 HOẶC insult >= 0.65 HOẶC hate_speech >= 0.60 → REJECTED
2. Nếu harassment >= 0.60 HOẶC violence >= 0.60 → REJECTED
3. Nếu spam >= 0.70 → REJECTED
4. Nếu sexual_content >= 0.70 → REJECTED
5. Các trường hợp còn lại → APPROVED

BẮT BUỘC trả về JSON chính xác (không có text nào khác ngoài JSON):
{
  "approved": true|false,
  "scores": {
    "toxicity": 0.0,
    "insult": 0.0,
    "hate_speech": 0.0,
    "harassment": 0.0,
    "spam": 0.0,
    "sexual_content": 0.0,
    "violence": 0.0
  },
  "violated_categories": ["toxicity"],
  "reason": "Giải thích ngắn gọn bằng tiếng Việt",
  "confidence": 0.95
}"""

    MODERATION_PROMPT = """KIỂM DUYỆT NỘI DUNG:

LOẠI: {content_type}
NỘI DUNG: {content}

Phân tích và trả về JSON theo format đã hướng dẫn. KHÔNG thêm bất kỳ text nào khác ngoài JSON."""

    def __init__(self):
        self.ollama = get_ollama_client(
            model=self.MODEL,
            vision_model=self.VISION_MODEL,
            timeout=self.TIMEOUT
        )

    # ==================== SUMMARIZATION ====================
    async def summarize_post(self, req: SummarizePostRequest) -> SummarizePostResponse:
        try:
            try:
                obj_id = ObjectId(req.post_id)
            except:
                return self._error_response(req.post_id, "Invalid post_id format")

            post = await PostRepository.find_by_id(req.post_id)
            if not post:
                return self._error_response(req.post_id, "Post not found")

            title = post.get("title", "")
            content = post.get("content", "")
            media_files = post.get("thumbnails", [])

            if not req.force_refresh and post.get("ai_summary"):
                return SummarizePostResponse(
                    success=True,
                    post_id=req.post_id,
                    title=title,
                    summary=post["ai_summary"],
                    original_content=content,
                    generated_at=str(post.get("ai_summary_generated_at", "")),
                    cached=True
                )

            if media_files and len(media_files) > 0:
                summary = await self._call_ollama_with_vision(title, content, media_files)
            else:
                text_to_summarize = content if content else title
                if len(text_to_summarize) < 30:
                    summary = text_to_summarize if text_to_summarize else "Không có nội dung"
                else:
                    summary = await self._call_ollama_text(title, content)

            await db.post.update_one(
                {"_id": obj_id},
                {
                    "$set": {
                        "ai_summary": summary,
                        "ai_summary_generated_at": datetime.utcnow(),
                        "ai_summary_model": self.MODEL,
                        "ai_summary_has_vision": bool(media_files)
                    }
                }
            )

            return SummarizePostResponse(
                success=True,
                post_id=req.post_id,
                title=title,
                summary=summary,
                original_content=content,
                generated_at=datetime.utcnow().isoformat(),
                cached=False
            )

        except Exception as e:
            return self._error_response(req.post_id, str(e))

    async def get_existing_summary(self, post_id: str) -> Optional[SummarizePostResponse]:
        try:
            post = await PostRepository.find_by_id(post_id)
            if not post or not post.get("ai_summary"):
                return None

            return SummarizePostResponse(
                success=True,
                post_id=post_id,
                title=post.get("title", ""),
                summary=post["ai_summary"],
                original_content=post.get("content", ""),
                generated_at=str(post.get("ai_summary_generated_at", "")),
                cached=True
            )
        except:
            return None

    # ==================== MODERATION ====================
    async def moderate_content(self, req: ModerateContentRequest) -> ModerateContentResponse:
        content = req.content.strip()
        logger.info(f"[MOD] Received content: {content[:100]}... (length={len(content)})")
        if len(content) < 3:
            logger.info(f"[MOD] Short content, auto-approved")
            return ModerateContentResponse(
                success=True,
                content_type=req.content_type,
                approved=True,
                reason="Nội dung quá ngắn, bỏ qua kiểm duyệt",
                confidence=1.0
            )
        
        truncated = content[:2000] + "..." if len(content) > 2000 else content
        prompt = self.MODERATION_PROMPT.format(
            content_type=req.content_type,
            content=truncated
        )

        for attempt in range(2):
            try:
                async with OllamaSession(self.ollama) as client:
                    raw_response = await client.generate(
                        prompt=prompt,
                        system=self.SYSTEM_PROMPT_MODERATION,
                        temperature=self.MODERATION_TEMPERATURE,
                        num_predict=self.MODERATION_MAX_TOKENS
                    )
                logger.info(f"[MOD] Raw response (attempt {attempt+1}): {raw_response[:300]}")
                result = self._parse_moderation_response(raw_response)
                result = self._apply_thresholds(result)
                logger.info(f"[MOD] Final: approved={result['approved']}, reason={result['reason']}")
                return ModerateContentResponse(
                    success=True,
                    content_type=req.content_type,
                    approved=result["approved"],
                    scores=ModerationScores(**result["scores"]),
                    violated_categories=result["violated_categories"],
                    reason=result["reason"],
                    confidence=result["confidence"]
                )
            except Exception as e:
                logger.error(f"[MOD] Attempt {attempt+1} failed: {e}")
                if attempt == 0:
                    await asyncio.sleep(1)
                else:
                    return ModerateContentResponse(
                        success=True,
                        content_type=req.content_type,
                        approved=False,
                        reason=f"Hệ thống kiểm duyệt tạm thời không khả dụng. Vui lòng thử lại sau. ({str(e)})",
                        confidence=0.0
                    )

    async def batch_moderate(self, contents: List[ModerateContentRequest]) -> List[ModerateContentResponse]:
        tasks = [self.moderate_content(req) for req in contents]
        return await asyncio.gather(*tasks, return_exceptions=True)

    def _parse_moderation_response(self, raw: str) -> dict:
        # Loại bỏ markdown
        raw = re.sub(r'^```json\s*', '', raw.strip())
        raw = re.sub(r'\s*```$', '', raw)
        
        # Tìm JSON object
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                if "scores" in data and isinstance(data["scores"], dict):
                    scores_keys = ["toxicity", "insult", "hate_speech", "harassment", "spam", "sexual_content", "violence"]
                    for k in scores_keys:
                        if k not in data["scores"]:
                            data["scores"][k] = 0.0
                    return {
                        "approved": bool(data.get("approved", False)),
                        "scores": {k: float(data["scores"].get(k, 0)) for k in scores_keys},
                        "violated_categories": data.get("violated_categories", []),
                        "reason": data.get("reason", ""),
                        "confidence": float(data.get("confidence", 0.5))
                    }
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"[MOD] JSON decode error: {e}")
        
        # Nếu là list, xử lý label
        try:
            arr = json.loads(raw)
            if isinstance(arr, list) and len(arr) > 0:
                if "label" in arr[0]:
                    label = arr[0]["label"].lower()
                    if any(kw in label for kw in ["không có nội dung xấu", "an toàn", "phù hợp"]):
                        return {
                            "approved": True,
                            "scores": {k: 0.0 for k in ["toxicity", "insult", "hate_speech", "harassment", "spam", "sexual_content", "violence"]},
                            "violated_categories": [],
                            "reason": "",
                            "confidence": 0.8
                        }
                    else:
                        return {
                            "approved": False,
                            "scores": {k: 0.0 for k in ["toxicity", "insult", "hate_speech", "harassment", "spam", "sexual_content", "violence"]},
                            "violated_categories": ["general"],
                            "reason": label,
                            "confidence": 0.7
                        }
        except:
            pass
        
        # Không parse được -> REJECT
        logger.warning(f"[MOD] Cannot parse response, rejecting: {raw[:200]}")
        return {
            "approved": False,
            "scores": {k: 0.0 for k in ["toxicity", "insult", "hate_speech", "harassment", "spam", "sexual_content", "violence"]},
            "violated_categories": ["parse_error"],
            "reason": "Hệ thống kiểm duyệt không thể xử lý nội dung này. Vui lòng thử lại.",
            "confidence": 0.0
        }

    def _apply_thresholds(self, result: dict) -> dict:
        scores = result["scores"]
        violated = []
        reasons = []

        if scores["toxicity"] >= self.THRESHOLD_REJECT:
            violated.append("toxicity")
            reasons.append("chứa ngôn từ độc hại, thô tục")
        if scores["insult"] >= self.THRESHOLD_REJECT:
            violated.append("insult")
            reasons.append("xúc phạm, lăng mạ người khác")
        if scores["hate_speech"] >= self.THRESHOLD_REJECT:
            violated.append("hate_speech")
            reasons.append("phát ngôn thù địch, phân biệt đối xử")
        if scores["harassment"] >= self.THRESHOLD_REJECT:
            violated.append("harassment")
            reasons.append("quấy rối, đe dọa")
        if scores["spam"] >= self.THRESHOLD_SPAM:
            violated.append("spam")
            reasons.append("spam, quảng cáo trái phép")
        if scores["sexual_content"] >= self.THRESHOLD_SEXUAL:
            violated.append("sexual_content")
            reasons.append("nội dung tình dục, khiêu dâm")
        if scores["violence"] >= self.THRESHOLD_VIOLENCE:
            violated.append("violence")
            reasons.append("bạo lực, đe dọa gây hại")

        if violated:
            result["approved"] = False
            result["violated_categories"] = violated
            result["reason"] = "Nội dung " + ", ".join(reasons) + ". Vui lòng chỉnh sửa và thử lại."
            result["confidence"] = max(result["confidence"], 0.75)
        else:
            result["approved"] = True
            result["violated_categories"] = []
            result["reason"] = ""
            result["confidence"] = max(result["confidence"], 0.6)

        return result

    # ==================== PRIVATE HELPERS ====================
    async def _call_ollama_text(self, title: str, content: str) -> str:
        truncated = content[:1500] + "..." if len(content) > 1500 else content
        prompt = f"Tóm tắt bài đăng sau:\n\nTIÊU ĐỀ: {title}\nNỘI DUNG: {truncated}\n\nTÓM TẮT (tối đa 5 câu):"
        async with OllamaSession(self.ollama) as client:
            try:
                response = await client.generate(
                    prompt=prompt,
                    system=self.SYSTEM_PROMPT_SUMMARY,
                    temperature=self.TEMPERATURE,
                    num_predict=self.MAX_TOKENS
                )
                summary = response.strip()
                if len(summary) > 500:
                    summary = summary[:497] + "..."
                return summary if summary else "Không thể tóm tắt bài viết này"
            except Exception as e:
                print(f"Ollama error: {e}")
                return f"{content[:100]}..." if len(content) > 100 else content

    async def _call_ollama_with_vision(self, title: str, content: str, media_files: List[str]) -> str:
        image_urls = []
        for file_id in media_files[:3]:
            try:
                url = FileService.get_file_url(file_id, expires_seconds=300)
                image_urls.append(url)
            except Exception as e:
                print(f"Error getting URL for {file_id}: {e}")

        if not image_urls:
            return await self._call_ollama_text(title, content)

        truncated = content[:1000] + "..." if len(content) > 1000 else content
        image_context = f"Có {len(image_urls)} hình ảnh đính kèm trong bài đăng."
        prompt = f"""Phân tích bài đăng sau:

TIÊU ĐỀ: {title}

NỘI DUNG: {truncated}

{image_context}

Hãy tóm tắt nội dung chính, kết hợp thông tin từ văn bản và hình ảnh (nếu có).

TÓM TẮT (tối đa 5 câu):"""
        async with OllamaSession(self.ollama) as client:
            try:
                response = await client.generate_with_image(
                    prompt=prompt,
                    image_urls=image_urls,
                    system=self.SYSTEM_PROMPT_VISION,
                    temperature=self.TEMPERATURE,
                    num_predict=self.MAX_TOKENS
                )
                summary = response.strip()
                if len(summary) > 800:
                    summary = summary[:797] + "..."
                return summary if summary else "Không thể phân tích bài viết này"
            except Exception as e:
                print(f"Ollama vision error: {e}")
                return await self._call_ollama_text(title, content)

    def _error_response(self, post_id: str, error: str) -> SummarizePostResponse:
        return SummarizePostResponse(
            success=False,
            post_id=post_id,
            title="",
            summary="",
            original_content="",
            error_message=error
        )