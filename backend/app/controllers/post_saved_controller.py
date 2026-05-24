from fastapi import APIRouter, Depends, HTTPException
from dto.post_saved.request.add_collection_request import AddCollectionRequest
from dto.post_saved.request.add_post_to_collection_request import AddPostToCollectionRequest
from dto.post_saved.request.delete_collection_request import DeleteCollectionRequest
from dto.post_saved.request.find_by_email_request import FindByEmailRequest
from dto.post_saved.request.remove_post_from_collection_request import RemovePostFromCollectionRequest
from dto.post_saved.request.rename_collection_request import RenameCollectionRequest
from dto.post_saved.request.update_status_collection_request import UpdateStatusCollectionRequest
from dto.post_saved.response.add_collection_response import AddCollectionResponse
from dto.post_saved.response.add_post_to_collection_response import AddPostToCollectionResponse
from dto.post_saved.response.delete_collection_response import DeleteCollectionResponse
from dto.post_saved.response.find_by_email_response import FindByEmailResponse
from dto.post_saved.response.remove_post_from_collection_response import RemovePostFromCollectionResponse
from dto.post_saved.response.rename_collection_response import RenameCollectionResponse
from dto.post_saved.response.update_status_collection_response import UpdateStatusCollectionResponse
from services.interfaces.post_saved_service_interface import IPostSavedService
from core.dependency import get_post_saved_service
from utils.security import get_current_user


router = APIRouter()

@router.get("/get_collections/{email}", response_model=FindByEmailResponse)
async def get_collection(
    email: str,
    current_user: dict = Depends(get_current_user),
    service: IPostSavedService = Depends(get_post_saved_service)
):
    req: FindByEmailRequest = FindByEmailRequest(email=email)
    return await service.find_by_email(req)

@router.post("/add_collection", response_model=AddCollectionResponse)
async def add_collection(
    req: AddCollectionRequest,
    current_user: dict = Depends(get_current_user),
    service: IPostSavedService = Depends(get_post_saved_service)
):
    req.email = current_user["sub"]
    return await service.add_collection(req)

@router.post("/add_post_to_collection", response_model=AddPostToCollectionResponse)
async def add_post_to_collection(
    req: AddPostToCollectionRequest,
    current_user: dict = Depends(get_current_user),
    service: IPostSavedService = Depends(get_post_saved_service)
):
    req.email = current_user["sub"]
    return await service.add_post_to_collection(req)

@router.post("/remove_post_from_collection", response_model=RemovePostFromCollectionResponse)
async def remove_post_from_collection(
    req: RemovePostFromCollectionRequest,
    current_user: dict = Depends(get_current_user),
    service: IPostSavedService = Depends(get_post_saved_service)
):
    req.email = current_user["sub"]
    return await service.remove_post_from_collection(req)

@router.post("/delete_collection", response_model=DeleteCollectionResponse)
async def delete_collection(
    req: DeleteCollectionRequest,
    current_user: dict = Depends(get_current_user),
    service: IPostSavedService = Depends(get_post_saved_service)
):
    req.email = current_user["sub"]
    return await service.delete_collection(req)

@router.post("/rename_collection", response_model=RenameCollectionResponse)
async def rename_collection(
    req: RenameCollectionRequest,
    current_user: dict = Depends(get_current_user),
    service: IPostSavedService = Depends(get_post_saved_service)
):
    req.email = current_user["sub"]
    return await service.rename_collection(req)

@router.post("/update_status_collection", response_model=UpdateStatusCollectionResponse)
async def update_status_collection(
    req: UpdateStatusCollectionRequest,
    current_user: dict = Depends(get_current_user),
    service: IPostSavedService = Depends(get_post_saved_service)
):
    req.email = current_user["sub"]
    return await service.update_status_collection(req)