from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from bson import ObjectId
from models.post_model import React
from models.post_model import PollData
from models.post_model import HistoryEdit
from models.post_model import Comment


class UpdatePostRequest(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    createdAt: Optional[datetime] = None
    postType: Optional[str] = None
    visibility: Optional[str] = None
    status: Optional[str] = None
    createdBy: Optional[str] = None
    category: Optional[List[str]] = None
    views: Optional[int] = None
    react: Optional[React] = None
    pollData: Optional[PollData] = None
    historyEdits: Optional[List[HistoryEdit]] = None
    comments: Optional[List[Comment]] = None
    lastEdited: Optional[datetime] = None


    thumbnails: Optional[List[str]] = None

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


