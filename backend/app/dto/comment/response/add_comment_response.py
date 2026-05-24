from pydantic import BaseModel
from typing import Optional, Dict


class AddCommentResponse(BaseModel):
    success: bool
    message: str
    comment: Optional[Dict] = None
