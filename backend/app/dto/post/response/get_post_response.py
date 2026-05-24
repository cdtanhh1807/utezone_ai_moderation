from models.post_model import Post
from pydantic import BaseModel


class GetPostResponse(BaseModel):
    post: Post

    