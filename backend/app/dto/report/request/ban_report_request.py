from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from bson import ObjectId


class BanReportRequest(BaseModel):
    element: Optional[str] = None
    elementId: Optional[str] = None
    policyId: Optional[str] = None

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        extra = "allow"

