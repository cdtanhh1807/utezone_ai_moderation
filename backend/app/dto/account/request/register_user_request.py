from pydantic import BaseModel


class RegisterUserRequest(BaseModel):
    type: str = "internal"
    email: str
    password: str
    role: str = "user"
    status: str = "active"


