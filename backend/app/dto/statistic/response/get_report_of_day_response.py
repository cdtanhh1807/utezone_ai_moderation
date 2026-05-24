from pydantic import BaseModel


class GetReportOfDayResponse(BaseModel):
    success: bool
    data: int
    

