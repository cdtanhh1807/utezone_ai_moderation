from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models.base_model import PyObjectId
from bson import ObjectId


class IncidentReport(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None) 
    email: str 
    content: Optional[str] = None
    reportedAt: datetime
    status: Optional[bool] = None

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        extra = "allow"
