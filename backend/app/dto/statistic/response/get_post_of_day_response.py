from pydantic import BaseModel


class GetPostOfDayResponse(BaseModel):
    success: bool
    data: int
    

