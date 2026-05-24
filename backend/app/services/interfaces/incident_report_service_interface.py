from abc import ABC, abstractmethod
from typing import List, Optional

from dto.incident_report.request.add_incident_report_request import AddIncidentReportRequest
from dto.incident_report.request.get_all_incident_report_request import GetAllIncidentReportRequest
from dto.incident_report.response.add_incident_report_response import AddIncidentReportResponse
from dto.incident_report.response.get_all_incident_report_response import GetAllIncidentReportResponse

class IIncidentReportService(ABC):

    @abstractmethod
    async def get_all(self, req: GetAllIncidentReportRequest) -> GetAllIncidentReportResponse:
        pass

    @abstractmethod
    async def add(self, req: AddIncidentReportRequest) -> AddIncidentReportResponse:
        pass