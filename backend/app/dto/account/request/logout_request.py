from pydantic import BaseModel

class LogoutRequest(BaseModel):
    token: str