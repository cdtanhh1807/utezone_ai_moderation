from abc import ABC, abstractmethod
from typing import Optional, List

from dto.story.request.delete_story_requesy import DeleteStoryRequest
from dto.story.response.delete_story_response import DeleteStoryResponse

class IStoryService(ABC):

    @abstractmethod
    async def add(self, story_data: dict):
        pass

    @abstractmethod
    async def find_by_user(self, user_id: str) -> Optional[list]:
        pass

    @abstractmethod
    async def find_all_active(self) -> list:
        pass

    @abstractmethod
    async def get_today_stories(self, email: str) -> list:
        pass

    @abstractmethod
    async def delete(self, story_id: DeleteStoryRequest) -> Optional[DeleteStoryResponse]:
        pass
