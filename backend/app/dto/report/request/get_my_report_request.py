from pydantic import BaseModel


class GetMyReportRequest(BaseModel):
    email: str


