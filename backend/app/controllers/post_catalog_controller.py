from fastapi import APIRouter, Depends, HTTPException
from dto.post_catalog.request.add_post_catalog_request import AddPostCatalogRequest
from dto.post_catalog.request.delete_post_catalog_request import DeletePostCatalogRequest
from dto.post_catalog.request.find_post_catalog_request import FindPostCatalogRequest
from dto.post_catalog.request.get_my_post_catalog_request import GetMyPostCatalogRequest
from dto.post_catalog.request.get_post_catalog_request import GetPostCatalogRequest
from dto.post_catalog.request.update_post_catalog_request import UpdatePostCatalogRequest
from dto.post_catalog.response.add_post_catalog_response import AddPostCatalogResponse
from dto.post_catalog.response.delete_post_catalog_response import DeletePostCatalogResponse
from dto.post_catalog.response.find_post_catalog_response import FindPostCatalogResponse
from dto.post_catalog.response.get_my_post_catalog_response import GetMyPostCatalogResponse
from dto.post_catalog.response.get_post_catalog_response import GetPostCatalogResponse
from dto.post_catalog.response.update_post_catalog_response import UpdatePostCatalogResponse
from services.interfaces.post_catalog_service_interface import IPostCatalogService
from core.dependency import get_post_catalog_service
from utils.security import get_current_user


router = APIRouter()

@router.post("/add_post_catalog", response_model=AddPostCatalogResponse)
async def add_post_catalog(
    req: AddPostCatalogRequest,
    current_user: dict = Depends(get_current_user),
    service: IPostCatalogService = Depends(get_post_catalog_service)
):
    if (current_user["role"] == "User"):
        raise HTTPException(status_code=403, detail="Failed!")
    req.email = current_user["sub"]
    return await service.add_post_catalog(req)

@router.put("/update_post_catalog/{post_id}", response_model=UpdatePostCatalogResponse)
async def update_post_catalog(
    post_id: str,
    req: UpdatePostCatalogRequest,
    current_user: dict = Depends(get_current_user),
    service: IPostCatalogService = Depends(get_post_catalog_service)
):
    if (current_user["role"] == "User"):
        raise HTTPException(status_code=403, detail="Failed!")
    req.post_id = post_id
    rs = await service.update_post_catalog(req)
    if not rs:
        raise HTTPException(status_code=404, detail="Post Catalog not found")
    return rs

@router.post("/find_post_catalog/{post_id}", response_model=FindPostCatalogResponse)
async def find_post_catalog(
    post_id: str,
    current_user: dict = Depends(get_current_user),
    service: IPostCatalogService = Depends(get_post_catalog_service)
):
    if (current_user["role"] == "User"):
        raise HTTPException(status_code=403, detail="Failed!")
    req: FindPostCatalogRequest = FindPostCatalogRequest(post_id=post_id)
    return await service.find_post_catalog(req)

@router.delete("/delete_post_catalog/{post_id}", response_model=DeletePostCatalogResponse)
async def delete_post_catalog(
    post_id: str,
    current_user: dict = Depends(get_current_user),
    service: IPostCatalogService = Depends(get_post_catalog_service)
):
    if (current_user["role"] == "User"):
        raise HTTPException(status_code=403, detail="Failed!")
    req: DeletePostCatalogRequest = DeletePostCatalogRequest(post_id=post_id) 
    success = await service.delete_post_catalog(req)
    if not success:
        raise HTTPException(status_code=404, detail="Post Catalog not found")
    return success

@router.get("/get_my_post_catalog/", response_model=GetMyPostCatalogResponse)
async def get_my_post_catalog(
    current_user: dict = Depends(get_current_user),
    service: IPostCatalogService = Depends(get_post_catalog_service)
):
    if (current_user["role"] == "User"):
        raise HTTPException(status_code=403, detail="Failed!")
    req: GetMyPostCatalogRequest = GetMyPostCatalogRequest(email=current_user["sub"])
    return await service.get_my_post_catalog(req)

@router.get("/get_post_catalog/", response_model=GetPostCatalogResponse)
async def get_post_catalog(
    current_user: dict = Depends(get_current_user),
    service: IPostCatalogService = Depends(get_post_catalog_service)
):
    req: GetPostCatalogRequest = GetPostCatalogRequest(email=current_user["sub"])
    return await service.get_post_catalog(req)


    