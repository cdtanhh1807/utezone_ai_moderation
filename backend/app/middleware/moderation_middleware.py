from dto.ai.request.moderate_content_request import ModerateContentRequest
from dto.ai.response.moderate_content_response import ModerateContentResponse
from services.interfaces.ai_service_interface import IAIService
from services.impls.ai_service_impl import AIServiceImpl
from fastapi import HTTPException


class ModerationMiddleware:
    """
    Middleware kiểm duyệt nội dung tự động - Binary mode.
    Chỉ có 2 kết quả: publish ngay hoặc reject + báo lý do.
    """

    def __init__(self):
        self._service = None

    async def _get_service(self) -> IAIService:
        if self._service is None:
            self._service = AIServiceImpl()
        return self._service

    async def check_and_enforce(
        self, 
        content: str, 
        content_type: str = "post",
        author_id: str = None,
        skip_short_content: bool = True
    ) -> ModerateContentResponse:
        """
        Kiểm tra nội dung. Nếu REJECTED → raise HTTPException 400 với lý do cụ thể.
        Nếu APPROVED → trả về response bình thường.

        Args:
            content: Nội dung cần kiểm tra (title + content nếu là post)
            content_type: "post" hoặc "comment"
            author_id: ID người đăng
            skip_short_content: Bỏ qua nếu < 3 ký tự
        """
        if skip_short_content and len(content.strip()) < 3:
            return ModerateContentResponse(
                success=True,
                content_type=content_type,
                approved=True,
                reason="Nội dung quá ngắn",
                confidence=1.0
            )

        service = await self._get_service()
        request = ModerateContentRequest(
            content=content,
            content_type=content_type,
            author_id=author_id
        )

        result = await service.moderate_content(request)

        if not result.approved:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Nội dung không được phép đăng",
                    "reason": result.reason,
                    "violated_categories": result.violated_categories,
                    "scores": result.scores.model_dump() if result.scores else {},
                    "suggestion": "Vui lòng chỉnh sửa nội dung theo hướng dẫn và thử lại."
                }
            )

        return result

    async def check_only(
        self,
        content: str,
        content_type: str = "post"
    ) -> ModerateContentResponse:
        """
        Kiểm tra nhưng KHÔNG raise exception. Trả về kết quả để caller tự xử lý.
        Hữu ích khi cần lưu kết quả moderation vào DB mà không block flow.
        """
        if len(content.strip()) < 3:
            return ModerateContentResponse(
                success=True,
                content_type=content_type,
                approved=True,
                reason="Nội dung quá ngắn",
                confidence=1.0
            )
        
        service = await self._get_service()
        request = ModerateContentRequest(
            content=content,
            content_type=content_type
        )
        return await service.moderate_content(request)


# Singleton
_moderation_instance = None

def get_moderation_middleware() -> ModerationMiddleware:
    global _moderation_instance
    if _moderation_instance is None:
        _moderation_instance = ModerationMiddleware()
    return _moderation_instance
