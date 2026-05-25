from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class AddPostCatalogRequest(BaseModel):
    name: str
    post_id: str
    email: Optional[str] = None
    begin_at: Optional[datetime] = Field(default_factory=datetime.now)
    end_at: datetime

