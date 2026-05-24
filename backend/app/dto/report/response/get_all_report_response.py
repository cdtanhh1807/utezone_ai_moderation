import uuid
from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import datetime
from models.base_model import PyObjectId
from bson import ObjectId
from models.violation_model import Detail

class GetAllReport(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    policyId: str
    policyName: str
    violatorEmail: str
    violatorName: str
    annunciatorEmail: str 
    annunciatorName: str 
    typeContent: str
    contentId: Optional[str] = None
    contentParentId: Optional[str] = None
    path: Optional[str] = None
    content: Optional[str] = None
    description: str
    reportedAt: datetime
    # verifyStatus: bool
    violation: Optional[List[datetime]] = None
    # violation: Optional[List[Detail]] = None
    approveBy: Optional[str] = None
    approveAt: Optional[datetime] = None
    
    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        extra = "allow"


class Annunciator(BaseModel):
    annunciatorEmail: str
    annunciatorName: str
    description: str
    reportedAt: datetime


class GetAllReportResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    policyId: str
    policyName: str
    violatorEmail: str
    violatorName: str
    annunciator: List[Annunciator]
    typeContent: str
    contentId: Optional[str] = None
    contentParentId: Optional[str] = None
    path: Optional[str] = None
    content: Optional[str] = None
    # verifyStatus: bool
    violation: Optional[List[datetime]] = None
    
    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        extra = "allow"



# class GetAllReportResponse(BaseModel):
#     id: Optional[PyObjectId] = Field(alias="_id", default=None)
#     policyId: str
#     policyName: str
#     violatorEmail: str
#     violatorName: str
#     annunciatorEmail: str 
#     annunciatorName: str 
#     typeContent: str
#     contentId: Optional[str] = None
#     contentParentId: Optional[str] = None
#     content: Optional[str] = None
#     description: str
#     reportedAt: datetime
#     verifyStatus: bool
#     violation: Optional[List[datetime]] = None
    
#     class Config:
#         validate_by_name = True
#         arbitrary_types_allowed = True
#         json_encoders = {ObjectId: str}
#         extra = "allow"