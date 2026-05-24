from pydantic import BaseModel


class GetComplaintOfDayResponse(BaseModel):
    success: bool
    data: int
    

