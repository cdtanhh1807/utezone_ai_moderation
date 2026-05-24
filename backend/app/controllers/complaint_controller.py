from typing import List
from fastapi import APIRouter, Depends, HTTPException
from core.dependency import get_complaint_service
from dto.complaint.request.action_complaint_request import ActionComplaintRequest
from dto.complaint.request.add_complaint_request import AddComplaintRequest
from dto.complaint.request.get_all_complaint_request import GetAllComplaintRequest
from dto.complaint.response.action_complaint_response import ActionComplaintResponse
from dto.complaint.response.add_complaint_request import AddComplaintResponse
from dto.complaint.response.get_all_complaint_response import GetAllComplaintResponse
from dto.statistic.request.get_complaint_of_day_request import GetComplaintOfDayRequest
from dto.statistic.response.get_complaint_of_day_response import GetComplaintOfDayResponse
from services.interfaces.complaint_service_interface import IComplaintService
from utils.security import get_current_user


router = APIRouter()

@router.get("/get_all_complaint", response_model=List[GetAllComplaintResponse])
async def list_complaints(
    current_user: dict = Depends(get_current_user),
    service: IComplaintService = Depends(get_complaint_service)
):
    if (current_user["role"] != "Administrator"):
        raise HTTPException(status_code=403, detail="Failed!")
    complaint_list = GetAllComplaintRequest()
    return await service.get_all(complaint_list)

@router.put("/reject_complaint/{complaint_id}", response_model=ActionComplaintResponse)
async def reject(
    complaint_id: str,
    current_user: dict = Depends(get_current_user),
    service: IComplaintService = Depends(get_complaint_service)
):
    if current_user["role"] == "User":
        raise HTTPException(status_code=401, detail="Failed!")
    complaint_rq = ActionComplaintRequest(id = complaint_id)
    updated = await service.reject(complaint_rq)
    if updated.success:
        return updated
    raise HTTPException(status_code=400, detail="Failed!")

@router.put("/approve_complaint/{complaint_id}", response_model=ActionComplaintResponse)
async def reject(
    complaint_id: str,
    current_user: dict = Depends(get_current_user),
    service: IComplaintService = Depends(get_complaint_service)
):
    if current_user["role"] == "User":
        raise HTTPException(status_code=401, detail="Failed!")
    complaint_rq = ActionComplaintRequest(id = complaint_id, actionBy=current_user["sub"])
    updated = await service.approve(complaint_rq)
    if updated.success:
        return updated
    raise HTTPException(status_code=400, detail="Failed!")

@router.post("/add_complaint", response_model=AddComplaintResponse)
async def add_complaint(
    complaint: AddComplaintRequest,
    current_user: dict = Depends(get_current_user),
    service: IComplaintService = Depends(get_complaint_service)
):
    complaint.complainantEmail = current_user["sub"]
    return await service.add_complaint(complaint)
    
@router.get("/get_complaint_of_day", response_model=GetComplaintOfDayResponse)
async def list_complaint(
    current_user: dict = Depends(get_current_user),
    service: IComplaintService = Depends(get_complaint_service)
):
    if (current_user["role"] != "Administrator"):
        raise HTTPException(status_code=403, detail="Failed!")
    req = GetComplaintOfDayRequest()
    rs= await service.get_complaint_of_day(req)
    print(rs)
    return rs
