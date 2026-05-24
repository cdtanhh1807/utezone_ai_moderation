from pydantic import BaseModel

class UpdateAccountTResponse(BaseModel):
    message: str
    success: bool = True
