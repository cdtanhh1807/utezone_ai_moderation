from typing import List
from fastapi import APIRouter, Depends, HTTPException
from core.dependency import get_announce_service
from dto.announce.request.get_all_announce_request import GetAllAnnounceRequest
from dto.announce.request.send_announce_request import SendAnnounceRequest
from dto.announce.response.get_all_announce_response import GetAllAnnounceResponse
from dto.announce.response.send_announce_response import SendAnnounceResponse
from services.interfaces.announce_service_interface import IAnnounceService
from utils.security import get_current_user


router = APIRouter()

@router.get("/get_all_announce", response_model=GetAllAnnounceResponse)
async def list_bans(
    current_user: dict = Depends(get_current_user),
    service: IAnnounceService = Depends(get_announce_service)
):
    req = GetAllAnnounceRequest(email=current_user["sub"])
    return await service.get_all_by_receiver_email(req)

@router.post("/send_announce", response_model=SendAnnounceResponse)
async def list_bans(
    req: SendAnnounceRequest,
    current_user: dict = Depends(get_current_user),
    service: IAnnounceService = Depends(get_announce_service)
):
    return await service.add(req)
