from pydantic import BaseModel, Field
from typing import Optional, Union
from datetime import datetime
from models.base_model import PyObjectId
from bson import ObjectId


class Complaint(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    policyId: str
    complainantEmail: str
    typeContent: str
    contentId: Optional[str] = None
    contentParentId: Optional[str] = None
    path: Optional[str] = None
    content: Optional[str] = None
    description: str
    complaintAt: datetime
    approveBy: Optional[str] = None
    approveAt: Optional[datetime] = None
    verify: Optional[bool] = None

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        extra = "allow"
