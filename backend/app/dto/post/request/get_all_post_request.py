from pydantic import BaseModel


class GetAllPostRequest(BaseModel):
    email: str


