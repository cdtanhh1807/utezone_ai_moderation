from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from bson import ObjectId

from models.base_model import PyObjectId


class ActionComplaintRequest(BaseModel):
    id: Optional[str] = None
    actionBy: Optional[str] = None

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        extra = "allow"

