from pydantic import BaseModel
from typing import List
from models.story_model import Story


class GetAllStoryResponse(BaseModel):
    story_list: List[Story]