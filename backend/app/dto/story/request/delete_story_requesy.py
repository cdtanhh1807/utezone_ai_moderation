from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from models.story_model import TextLayer, Music, React, VideoTrim


class DeleteStoryRequest(BaseModel):
    id: Optional[str] = None