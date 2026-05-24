from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from core.dependency import get_report_service
from dto.report.request.approve_report_request import ApproveReportRequest
from dto.report.request.get_all_history_approve_request import GetAllHistoryApproveRequest
from dto.report.request.get_all_report_request import GetAllReportRequest
from dto.report.request.get_my_report_request import GetMyReportRequest
from dto.report.request.get_report_me_request import GetReportMeRequest
from dto.report.request.reject_report_request import RejectReportRequest
from dto.report.request.send_report_request import SendReportRequest
from dto.report.request.update_report_request import UpdateReportRequest
from dto.report.response.approve_report_response import ApproveReportResponse
from dto.report.response.get_all_history_approve_reponse import GetAllHistoryApproveResponse
from dto.report.response.get_all_report_response import GetAllReportResponse
from dto.report.response.get_my_report_response import GetMyReportResponse
from dto.report.response.get_report_me_response import GetReportMeResponse, ReportGroup
from dto.report.response.reject_report_response import RejectReportResponse
from dto.report.response.send_report_response import SendReportResponse
from dto.report.response.update_report_response import UpdateReportResponse
from dto.statistic.request.get_report_of_day_request import GetReportOfDayRequest
from dto.statistic.request.get_top_report_request import GetTopReportRequest
from dto.statistic.response.get_report_of_day_response import GetReportOfDayResponse
from dto.statistic.response.get_top_report_response import GetTopReportReponse
from services.interfaces.report_service_interface import IReportService
from utils.security import get_current_user


router = APIRouter()

@router.get("/get_all_report", response_model=List[GetAllReportResponse])
async def list_reports(
    current_user: dict = Depends(get_current_user),
    service: IReportService = Depends(get_report_service)
):
    if (current_user["role"] != "Administrator"):
        raise HTTPException(status_code=403, detail="Failed!")
    report_list = GetAllReportRequest()
    return await service.get_all(report_list)

@router.put("/update_report/{report_id}", response_model=UpdateReportResponse)
async def update_report(
    report_id: str,
    report: UpdateReportRequest,
    # current_user: dict = Depends(get_current_user),
    service: IReportService = Depends(get_report_service)
):
    report.id = report_id
    updated = await service.update(report)
    if not updated:
        raise HTTPException(status_code=404, detail="Report not found")
    return updated

@router.put("/reject_report", response_model=RejectReportResponse)
async def reject(
    report_rq: RejectReportRequest,
    current_user: dict = Depends(get_current_user),
    service: IReportService = Depends(get_report_service)
):
    if (current_user["role"] == "User"):
        raise HTTPException(status_code=403, detail="Failed!")
    report_rq.rejectBy = current_user["sub"]
    updated = await service.reject(report_rq)
    if not updated:
        raise HTTPException(detail="Failed!")
    return updated

@router.put("/approve_report", response_model=ApproveReportResponse)
async def approve(
    report_rq: ApproveReportRequest,
    current_user: dict = Depends(get_current_user),
    service: IReportService = Depends(get_report_service)
):
    if (current_user["role"] == "User"):
        raise HTTPException(status_code=403, detail="Failed!")
    report_rq.approveBy = current_user["sub"]
    updated = await service.approve(report_rq)
    if not updated:
        raise HTTPException(detail="Failed!")
    return updated

@router.get("/get_all_approve_report", response_model=List[GetAllHistoryApproveResponse])
async def list_reports(
    current_user: dict = Depends(get_current_user),
    service: IReportService = Depends(get_report_service)
):
    if (current_user["role"] != "Administrator"):
        raise HTTPException(status_code=403, detail="Failed!")
    report_list = GetAllHistoryApproveRequest()
    return await service.get_all_history_approve(report_list)

@router.post("/send_report", response_model=SendReportResponse)
async def send_report(
    report: SendReportRequest,
    current_user: dict = Depends(get_current_user),
    service: IReportService = Depends(get_report_service)
):
    report.annunciatorEmail = current_user["sub"]
    return await service.send_report(report)

@router.get("/get_report_of_day", response_model=GetReportOfDayResponse)
async def list_report(
    current_user: dict = Depends(get_current_user),
    service: IReportService = Depends(get_report_service)
):
    if (current_user["role"] != "Administrator"):
        raise HTTPException(status_code=403, detail="Failed!")
    req = GetReportOfDayRequest()
    rs= await service.get_report_of_day(req)
    print(rs)
    return rs

@router.get("/get_top_report", response_model=GetTopReportReponse)
async def list_report(
    current_user: dict = Depends(get_current_user),
    service: IReportService = Depends(get_report_service)
):
    if (current_user["role"] != "Administrator"):
        raise HTTPException(status_code=403, detail="Failed!")
    req = GetTopReportRequest()
    rs= await service.get_top_report(req)
    return rs

@router.get("/get_my_report", response_model=List[GetMyReportResponse])
async def get_my_report(
    current_user: dict = Depends(get_current_user),
    service: IReportService = Depends(get_report_service)
):
    req = GetMyReportRequest(email=current_user["sub"])
    return await service.get_my_report(req)


@router.get("/get_report_me", response_model=List[ReportGroup])
async def get_report_me(
    current_user: dict = Depends(get_current_user),
    service: IReportService = Depends(get_report_service)
):
    req = GetReportMeRequest(email=current_user["sub"])
    return await service.get_report_me(req)