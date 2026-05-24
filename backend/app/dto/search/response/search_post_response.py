from pydantic import BaseModel
from typing import List
from models.post_model import Post


class SearchPostResponse(BaseModel):
    post_list: List[Post]


