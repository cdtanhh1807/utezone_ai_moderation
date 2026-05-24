from pydantic import BaseModel

class OTPResponse(BaseModel):
    message: str
