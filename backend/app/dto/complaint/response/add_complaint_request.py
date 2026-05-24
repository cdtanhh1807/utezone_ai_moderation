from pydantic import BaseModel
from models.complaint_model import Complaint


class AddComplaintResponse(BaseModel):
    complaint: Complaint
