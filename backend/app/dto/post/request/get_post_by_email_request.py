# dto/post/request/get_post_by_email_request.py
from pydantic import BaseModel

class GetPostByEmailRequest(BaseModel):
    email: str
    ownerEmail: str
