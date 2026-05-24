from pydantic import BaseModel
from typing import List, Optional
from models.story_model import Story

class UserStoryGroup(BaseModel):
    userId: str
    stories: List[Story]
    latestStoryAt: Optional[str]

class GetTodayStoryResponse(BaseModel):
    success: bool
    data: List[UserStoryGroup]
    message: str = ""
