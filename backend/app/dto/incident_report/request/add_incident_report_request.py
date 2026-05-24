from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from bson import ObjectId


class AddIncidentReportRequest(BaseModel):
    email: Optional[str] = None 
    content: str
    reportedAt: Optional[datetime] = None
    status: Optional[bool] = None
