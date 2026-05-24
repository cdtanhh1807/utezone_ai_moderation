from pydantic import BaseModel 


class ForgotPasswordResponse(BaseModel):
    message: str
    success: bool
