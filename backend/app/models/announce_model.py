from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models.base_model import PyObjectId
from bson import ObjectId


class Announce(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    receiverEmail: str
    senderEmail: str
    type: str           # "comment" | "report" | "complaint" | "account" 
    contentAnnounce: str
    isRead: bool
    createdAt: datetime
    contentId: Optional[str] = None
    contentParentId: Optional[str] = None
    path: Optional[str] = None
    content: Optional[str] = None
    policyName: Optional[str] = None
    policyId: Optional[str] = None

    approveBy: Optional[str] = None
    approveAt: Optional[datetime] = None
    
    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        extra = "allow"
