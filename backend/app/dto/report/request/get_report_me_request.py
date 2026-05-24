from pydantic import BaseModel


class GetReportMeRequest(BaseModel):
    email: str


