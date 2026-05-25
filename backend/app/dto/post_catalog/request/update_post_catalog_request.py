from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from bson import ObjectId
from models.post_model import React
from models.post_model import PollData
from models.post_model import HistoryEdit
from models.post_model import Comment


class UpdatePostCatalogRequest(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    post_id: Optional[str] = None
    begin_at: Optional[datetime] = Field(default_factory=datetime.now)
    end_at: Optional[datetime] = None

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


