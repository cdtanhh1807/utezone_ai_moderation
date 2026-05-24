import uuid
from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import datetime
from models.base_model import PyObjectId
from bson import ObjectId
from models.violation_model import Detail

class GetMyReportResponse(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    policyId: str
    violatorEmail: str
    violatorName: str
    annunciatorEmail: str 
    typeContent: str
    contentId: Optional[str] = None
    contentParentId: Optional[str] = None
    path: Optional[str] = None
    content: Optional[str] = None
    description: str
    reportedAt: datetime
    check: bool
    approveBy: Optional[str] = None
    approveAt: Optional[datetime] = None
    status: Optional[str] = None
    
    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        extra = "allow"
