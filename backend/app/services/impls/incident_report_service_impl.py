from datetime import datetime
from typing import List

from dto.incident_report.request.add_incident_report_request import AddIncidentReportRequest
from dto.incident_report.request.get_all_incident_report_request import GetAllIncidentReportRequest
from dto.incident_report.response.add_incident_report_response import AddIncidentReportResponse
from dto.incident_report.response.get_all_incident_report_response import GetAllIncidentReportResponse
from models.base_model import bson_to_dict
from models.incident_report_model import IncidentReport
from repositories.incident_report_repository import IncidentReportRepository
from services.interfaces.incident_report_service_interface import IIncidentReportService


class IncidentReportServiceImpl(IIncidentReportService):

    async def get_all(self, req: GetAllIncidentReportRequest) -> GetAllIncidentReportResponse:
        dic_list = await IncidentReportRepository.find_all()
        incident_report = [IncidentReport(**bson_to_dict(dic)) for dic in dic_list]
        rs: GetAllIncidentReportResponse = GetAllIncidentReportResponse(rs=incident_report)
        return rs
    
    async def add(self, req: AddIncidentReportRequest) -> AddIncidentReportResponse:
        req.reportedAt = datetime.now()
        req.status = False
        rs = await IncidentReportRepository.insert(req.model_dump())
        if rs:
            return AddIncidentReportResponse(incident_report=IncidentReport(**bson_to_dict(rs)))
        return AddIncidentReportResponse(incident_report=None)
    
