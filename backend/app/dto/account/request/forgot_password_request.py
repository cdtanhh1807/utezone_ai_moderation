from pydantic import BaseModel

class ForgotPasswordRequest(BaseModel):
    email: str
    otp: str
    new_password: str


