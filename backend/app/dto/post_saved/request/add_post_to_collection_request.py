from typing import Optional

from pydantic import BaseModel

class AddPostToCollectionRequest(BaseModel):
    email: Optional[str] = None
    collection_name: Optional[str] = None
    post_id: Optional[str] = None