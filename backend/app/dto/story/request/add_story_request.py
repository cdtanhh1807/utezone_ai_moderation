from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from models.story_model import TextLayer, Music, React, VideoTrim


class AddStoryRequest(BaseModel):
    createdBy: str
    createdAt: datetime
    mediaType: str
    expiresAt: datetime

    mediaUrls: List[str]
    thumbnails: List[str] = []

    textLayers: List[TextLayer] = []
    videoTrim: Optional[VideoTrim] = None
    music: Optional[Music] = None

    status: str = "active"
    viewedBy: List[str] = []

    react: Optional[React] = None