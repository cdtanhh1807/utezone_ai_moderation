from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional
from models.base_model import PyObjectId

class BanDetail(BaseModel):
    policyName: Optional[str] = None
    action: Optional[str] = None
    beginAt: Optional[datetime] = None
    endAt: Optional[datetime] = None

class GetAllBanResponse(BaseModel):
    id: Optional[str] = None
    violatorEmail: Optional[str] = None
    violatorRole: Optional[str] = None
    detail: Optional[List[BanDetail]] = None


