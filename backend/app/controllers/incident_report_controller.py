from typing import List
from fastapi import APIRouter, Depends, HTTPException
from core.dependency import get_incident_report_service
from dto.incident_report.request.add_incident_report_request import AddIncidentReportRequest
from dto.incident_report.request.get_all_incident_report_request import GetAllIncidentReportRequest
from dto.incident_report.response.add_incident_report_response import AddIncidentReportResponse
from dto.incident_report.response.get_all_incident_report_response import GetAllIncidentReportResponse
from services.interfaces.incident_report_service_interface import IIncidentReportService
from utils.security import get_current_user


router = APIRouter()

@router.get("/get_all_incident_report", response_model=GetAllIncidentReportResponse)
async def list_incident_report(
    current_user: dict = Depends(get_current_user),
    service: IIncidentReportService = Depends(get_incident_report_service)
):
    if (current_user["role"] != "Administrator"):
        raise HTTPException(status_code=403, detail="Failed!")
    req = GetAllIncidentReportRequest()
    return await service.get_all(req)

@router.post("/add_incident_report", response_model=AddIncidentReportResponse)
async def add_incident_report(
    req: AddIncidentReportRequest,
    current_user: dict = Depends(get_current_user),
    service: IIncidentReportService = Depends(get_incident_report_service)
):
    req.email = current_user["sub"]
    return await service.add(req)