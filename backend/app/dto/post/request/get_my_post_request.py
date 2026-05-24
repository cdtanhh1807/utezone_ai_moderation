from pydantic import BaseModel


class GetMyPostRequest(BaseModel):
    email: str


