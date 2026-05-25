from datetime import datetime
from typing import List

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
from models.base_model import bson_to_dict
from models.post_catalog_model import PostCatalog
from repositories.post_catalog_repository import PostCatalogRepository
from repositories.post_saved_repository import PostSavedRepository
from services.interfaces.post_catalog_service_interface import IPostCatalogService

class PostCatalogServiceImpl(IPostCatalogService):

    async def add_post_catalog(self, req: AddPostCatalogRequest) -> AddPostCatalogResponse:
        dic = await PostCatalogRepository.insert(req.model_dump())
        if dic:
            rs = PostCatalog(**bson_to_dict(dic))
            return AddPostCatalogResponse(item=rs)
        return AddPostCatalogResponse(item=None)
    
    async def update_post_catalog(self, req: UpdatePostCatalogRequest) -> UpdatePostCatalogResponse:
        updated_post_catalog = await PostCatalogRepository.update(req.model_dump(exclude_none=True))
        if updated_post_catalog:
            return UpdatePostCatalogResponse(post_catalog=PostCatalog(**bson_to_dict(updated_post_catalog)))
        return UpdatePostCatalogResponse(post_catalog=None)
    
    async def find_post_catalog(self, req: FindPostCatalogRequest) -> FindPostCatalogResponse:
        dic = await PostCatalogRepository.find_by_post_id(req.post_id)
        if dic:
            post_catalog: PostCatalog = PostCatalog(**bson_to_dict(dic))
            now = datetime.now()
            if post_catalog.end_at > now:
                return FindPostCatalogResponse(post_catalog=post_catalog)
            else:  
                rs_delete = await PostCatalogRepository.delete(post_catalog.post_id)
                return FindPostCatalogResponse(post_catalog=None)
        return FindPostCatalogResponse(post_catalog=None)
    
    async def delete_post_catalog(self, req: DeletePostCatalogRequest) -> DeletePostCatalogResponse:
        rs = await PostCatalogRepository.delete(req.post_id)
        if rs:
            return DeletePostCatalogResponse(success=True, message="Deleted")
        else:
            return DeletePostCatalogResponse(success=False, message="Failed to delete post")
        
    async def get_my_post_catalog(self, req: GetMyPostCatalogRequest) -> GetMyPostCatalogResponse:
        list_dic = await PostCatalogRepository.find_by_email(req.email)
        if list_dic:
            list_rs: List[PostCatalog] = []
            for dic in list_dic:
                post_catalog: PostCatalog = PostCatalog(**bson_to_dict(dic))
                now = datetime.now()
                if post_catalog.end_at > now:
                    list_rs.append(post_catalog)
                else: rs_delete = await PostCatalogRepository.delete(post_catalog.post_id)
            return GetMyPostCatalogResponse(post_catalog_list=list_rs)
        return GetMyPostCatalogResponse(post_catalog_list=[])

    async def get_post_catalog(self, req: GetPostCatalogRequest) -> GetPostCatalogResponse:
        list_dic = await PostCatalogRepository.find_all()
        if list_dic:
            list_rs: List[PostCatalog] = []
            for dic in list_dic:
                post_catalog: PostCatalog = PostCatalog(**bson_to_dict(dic))
                now = datetime.now()
                if post_catalog.end_at > now:
                    list_rs.append(post_catalog)
                else: rs_delete = await PostCatalogRepository.delete(post_catalog.post_id)
            return GetPostCatalogResponse(post_catalog_list=list_rs)
        return GetPostCatalogResponse(post_catalog_list=[])
