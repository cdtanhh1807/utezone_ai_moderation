from abc import ABC, abstractmethod
from typing import Optional
from dto.ai.request.moderate_content_request import ModerateContentRequest
from dto.ai.request.summarize_post_request import SummarizePostRequest
from dto.ai.response.moderate_content_response import ModerateContentResponse
from dto.ai.response.summarize_post_response import SummarizePostResponse


class IAIService(ABC):

    @abstractmethod
    async def summarize_post(self, req: SummarizePostRequest) -> SummarizePostResponse:
        pass

    @abstractmethod
    async def get_existing_summary(self, post_id: str) -> Optional[SummarizePostResponse]:
        pass

    @abstractmethod
    async def moderate_content(self, req: ModerateContentRequest) -> ModerateContentResponse:
        pass

    @abstractmethod
    async def batch_moderate(self, contents: list[ModerateContentRequest]) -> list[ModerateContentResponse]:
        pass