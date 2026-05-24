from pydantic import BaseModel
from typing import Optional
from models.post_model import React

class UpdatePostReactResponse(BaseModel):
    message: str
    react: Optional[React] = None
