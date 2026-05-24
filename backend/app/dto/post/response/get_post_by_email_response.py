# dto/post/response/get_post_by_email_response.py
from pydantic import BaseModel
from typing import List
from models.post_model import Post

class GetPostByEmailResponse(BaseModel):
    post_list: List[Post] = []
