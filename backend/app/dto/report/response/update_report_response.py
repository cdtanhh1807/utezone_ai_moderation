from models.report_model import Report
from pydantic import BaseModel


class UpdateReportResponse(BaseModel):
    report: Report