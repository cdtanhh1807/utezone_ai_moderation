from typing import Optional
from pydantic import BaseModel
from models.post_saved_model import PostSaved


class RemovePostFromCollectionResponse(BaseModel):
    post_saved: Optional[PostSaved]