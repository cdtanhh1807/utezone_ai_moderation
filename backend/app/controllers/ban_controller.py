from typing import List
from fastapi import APIRouter, Depends, HTTPException
from dto.ban.request.get_all_ban_request import GetAllBanRequest
from dto.ban.response.get_all_ban_response import GetAllBanResponse
from services.interfaces.ban_service_interface import IBanService
from core.dependency import get_ban_service
from utils.security import get_current_user


router = APIRouter()

@router.get("/get_all_ban", response_model=List[GetAllBanResponse])
async def list_bans(
    current_user: dict = Depends(get_current_user),
    service: IBanService = Depends(get_ban_service)
):
    if (current_user["role"] != "Administrator"):
        raise HTTPException(status_code=403, detail="Failed!")
    ban_list = GetAllBanRequest()
    return await service.get_all(ban_list)
