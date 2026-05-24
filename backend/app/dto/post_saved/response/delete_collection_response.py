from typing import Optional
from pydantic import BaseModel
from models.post_saved_model import PostSaved


class DeleteCollectionResponse(BaseModel):
    post_saved: Optional[PostSaved]