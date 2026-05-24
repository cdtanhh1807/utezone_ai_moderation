from pydantic import BaseModel
from typing import Any, Optional

class AddStoryResponse(BaseModel):
    success: bool
    message: str
    story: Optional[Any] = None
