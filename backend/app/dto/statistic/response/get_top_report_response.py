from typing import List, Optional
from pydantic import BaseModel

class TopReport(BaseModel):
    typeContent: str
    contentId: Optional[str] = None
    content: Optional[str] = None
    violatorEmail: str
    contentParentId: Optional[str] = None
    path: Optional[str] = None

class GetTopReportReponse(BaseModel):
    success: bool
    data: Optional[List[TopReport]] = None
    

