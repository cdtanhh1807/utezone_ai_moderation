from pydantic import BaseModel


class ApproveReportResponse(BaseModel):
    message: str
    success: bool