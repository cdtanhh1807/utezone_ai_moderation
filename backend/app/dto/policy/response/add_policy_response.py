from pydantic import BaseModel


class AddPolicyResponse(BaseModel):
    success: bool
    message: str
