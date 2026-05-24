from pydantic import BaseModel


class SendReportResponse(BaseModel):
    message: str
    success: bool