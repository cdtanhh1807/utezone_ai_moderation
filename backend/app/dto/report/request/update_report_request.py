from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from bson import ObjectId


class UpdateReportRequest(BaseModel):
    id: Optional[str] = None
    verifyStatus: Optional[bool] = None

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        extra = "allow"

