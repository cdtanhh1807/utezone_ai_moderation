from typing import List, Optional
from pydantic import BaseModel

class TopPost(BaseModel):
    postId: str
    title: str
    createdBy: str
    interactions: int

class GetTopInteractedPostReponse(BaseModel):
    success: bool
    data: Optional[List[TopPost]] = None
    

