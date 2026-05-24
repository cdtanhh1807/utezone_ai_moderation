from typing import List
from models.post_model import Post
from pydantic import BaseModel


class GetPostSuggestResponse(BaseModel):
    list_post: List[Post]

    