from pydantic import BaseModel


class RejectReportResponse(BaseModel):
    message: str
    success: bool