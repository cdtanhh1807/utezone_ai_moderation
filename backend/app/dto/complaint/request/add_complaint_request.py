from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from models.post_model import CommentReact


class AddComplaintRequest(BaseModel):
    policyId: Optional[str] = None
    complainantEmail: Optional[str] = None
    typeContent: Optional[str] = None
    contentId: Optional[str] = None
    contentParentId: Optional[str] = None
    path: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None
    complaintAt: datetime = Field(default_factory=datetime.now)
    approveBy: Optional[str] = None
    approveAt: Optional[datetime] = None