from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from bson import ObjectId


class SendReportRequest(BaseModel):
    policyId: Optional[str] = None
    violatorEmail: Optional[str] = None
    annunciatorEmail: Optional[str] = None
    typeContent: Optional[str] = None
    contentId: Optional[str] = None
    contentParentId: Optional[str] = None
    path: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None
    reportedAt: datetime = datetime.now()
    check: bool = False

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        extra = "allow"

