from pydantic import BaseModel, Field
from typing import Optional, Union
from datetime import datetime
from models.base_model import PyObjectId
from bson import ObjectId


class Report(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    policyId: str
    violatorEmail: str
    annunciatorEmail: str 
    typeContent: str
    contentId: Optional[str] = None
    contentParentId: Optional[str] = None
    path: Optional[str] = None
    content: Optional[str] = None
    description: str
    reportedAt: datetime
    approveBy: Optional[str] = None
    approveAt: Optional[datetime] = None
    status: Optional[str] = None
    # verifyStatus: bool

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        extra = "allow"
