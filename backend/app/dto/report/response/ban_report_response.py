from pydantic import BaseModel


class BanReportResponse(BaseModel):
    message: str
    success: bool