from pydantic import BaseModel


class ActionComplaintResponse(BaseModel):
    message: str
    success: bool