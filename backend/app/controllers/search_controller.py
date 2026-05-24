from typing import List
from fastapi import APIRouter, Depends, HTTPException
from dto.ban.request.get_all_ban_request import GetAllBanRequest
from dto.ban.response.get_all_ban_response import GetAllBanResponse
from dto.search.request.search_account_request import SearchAccountRequest
from dto.search.request.search_post_request import SearchPostRequest
from dto.search.response.search_account_response import SearchAccountResponse
from dto.search.response.search_post_response import SearchPostResponse
from models.account_model import Account
from services.interfaces.ban_service_interface import IBanService
from core.dependency import get_ban_service, get_search_service
from services.interfaces.search_service_interface import ISearchService
from services.other.file_service import FileService
from utils.security import get_current_user


router = APIRouter()

@router.get("/search_account/{key_search}", response_model=SearchAccountResponse)
async def search_account(
    key_search: str,
    current_user: dict = Depends(get_current_user),
    service: ISearchService = Depends(get_search_service)
):
    req = SearchAccountRequest(email=current_user["sub"], keySearch=key_search)
    rs = await service.search_account(req)
    for item in rs.account_list:
        user_info = item.userInfo.dict() if item.userInfo else {}

        avatar_file_id = user_info.get("avatar")
        if avatar_file_id:
            avatar_url = FileService.get_file_url(avatar_file_id, expires_seconds=3600)
            user_info["avatar"] = avatar_url
            item.userInfo = user_info

    return rs

@router.get("/search_post/{key_search}", response_model=SearchPostResponse)
async def search_post(
    key_search: str,
    current_user: dict = Depends(get_current_user),
    service: ISearchService = Depends(get_search_service)
):
    req = SearchPostRequest(email=current_user["sub"], keySearch=key_search)
    rs = await service.search_post(req)

    for p in rs.post_list:
        if p.thumbnails:  # danh sách file_id
            p.thumbnails_url = [FileService.get_file_url(file_id) for file_id in p.thumbnails]
        else:
            p.thumbnails_url = []
    return rs
