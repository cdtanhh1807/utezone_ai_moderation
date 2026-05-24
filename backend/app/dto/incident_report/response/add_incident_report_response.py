from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from bson import ObjectId

from models.incident_report_model import IncidentReport


class AddIncidentReportResponse(BaseModel):
    incident_report: Optional[IncidentReport]
