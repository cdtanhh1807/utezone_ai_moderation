from typing import Optional

from pydantic import BaseModel
from models.post_saved_model import PostSaved

class UpdateStatusCollectionResponse(BaseModel):
    post_saved: Optional[PostSaved] = None
    error: Optional[str] = None