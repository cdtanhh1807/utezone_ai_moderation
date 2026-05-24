from models.post_model import Post
from pydantic import BaseModel


class UpdatePostResponse(BaseModel):
    post: Post