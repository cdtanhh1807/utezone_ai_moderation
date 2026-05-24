from pydantic import BaseModel
from typing import List, Optional

class GetRelationResponse(BaseModel):
    followers: Optional[List[str]] = []
    followed: Optional[List[str]] = []
    blocks: Optional[List[str]] = []