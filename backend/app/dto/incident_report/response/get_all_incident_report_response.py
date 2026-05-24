from typing import List
from pydantic import BaseModel, Field
from models.incident_report_model import IncidentReport


class GetAllIncidentReportResponse(BaseModel):
    rs: List[IncidentReport]
