from typing import List, Optional
import uuid
from pydantic import BaseModel, Field
from datetime import datetime
from models.base_model import PyObjectId
from bson import ObjectId

class GetAllHistoryApproveResponse(BaseModel):
    policyId: str
    policyName: str
    violatorEmail: str
    violatorName: str
    typeContent: str
    contentId: Optional[str] = None
    contentParentId: Optional[str] = None
    path: Optional[str] = None
    content: Optional[str] = None
    approveBy: str
    approveAt: datetime
    violation: Optional[List[datetime]] = None
    
    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        extra = "allow"
