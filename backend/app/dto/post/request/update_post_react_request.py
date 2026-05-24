from pydantic import BaseModel
from typing import Optional
from models.post_model import React

class UpdatePostReactRequest(BaseModel):
    id: str
    react: Optional[React] = None
