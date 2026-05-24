from pydantic import BaseModel
from typing import List
from models.post_model import Post


class GetAllPostResponse(BaseModel):
    post_list: List[Post]


