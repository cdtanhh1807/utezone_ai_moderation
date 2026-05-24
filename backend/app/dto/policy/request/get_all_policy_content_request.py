from pydantic import BaseModel


class GetAllPolicyContentRequest(BaseModel):
    content: str


