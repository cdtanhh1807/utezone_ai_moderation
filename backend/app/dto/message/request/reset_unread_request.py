from pydantic import BaseModel, EmailStr

class ResetUnreadRequest(BaseModel):
    other_email: EmailStr