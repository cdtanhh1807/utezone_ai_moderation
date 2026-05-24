from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any
import httpx

from core.dependency import get_post_service
from crawl.converter.fit_converter_service import CrawlToPostConverter
from dto.post.response.add_post_response import AddPostResponse
from services.impls.post_service_impl import PostServiceImpl
from services.interfaces.post_service_interface import IPostService

router = APIRouter(prefix="/crawl_import", tags=["Crawl Import"])

class CrawlImportService:
    def __init__(self, post_service: PostServiceImpl, converter: CrawlToPostConverter):
        self.post_service = post_service
        self.converter = converter
    
    async def import_single(self, crawl_doc: Dict[str, Any]) -> AddPostResponse:
        """Import 1 bài crawl thành post"""
        try:
            # Chuyển đổi
            post_request = await self.converter.convert(crawl_doc)
            
            # Thêm vào DB qua service có sẵn
            result = await self.post_service.add(post_request)
            return result
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")
    
    async def import_bulk(self, crawl_docs: List[Dict[str, Any]]) -> dict:
        """Import nhiều bài cùng lúc"""
        results = {"success": [], "failed": []}
        
        for doc in crawl_docs:
            try:
                result = await self.import_single(doc)
                results["success"].append({
                    "article_id": doc.get("article_id"),
                    "title": doc.get("title"),
                    "result": result
                })
            except Exception as e:
                results["failed"].append({
                    "article_id": doc.get("article_id"),
                    "title": doc.get("title"),
                    "error": str(e)
                })
        
        return results

# Dependency
def get_crawl_converter():
    # Cấu hình URL upload (có thể lấy từ settings)
    return CrawlToPostConverter(upload_endpoint="http://localhost:8000/file/upload")

@router.post("/import_single", response_model=AddPostResponse)
async def import_crawled_post(
    crawl_doc: Dict[str, Any],
    service: IPostService = Depends(get_post_service),
    converter: CrawlToPostConverter = Depends(get_crawl_converter)
):
    """
    Import 1 bài viết đã crawl thành post trong hệ thống
    
    Example body:
    {
        "article_id": "f3388afe...",
        "title": "Thông báo...",
        "date": "17/10/2025",
        "image_url": "https://...",
        "structured_content": [...]
    }
    """
    import_service = CrawlImportService(service, converter)
    return await import_service.import_single(crawl_doc)

@router.post("/import_bulk")
async def import_bulk_posts(
    crawl_docs: List[Dict[str, Any]],
    background_tasks: BackgroundTasks,
    service: IPostService = Depends(get_post_service),
    converter: CrawlToPostConverter = Depends(get_crawl_converter)
):
    """
    Import nhiều bài viết cùng lúc
    
    Có thể chạy async trong background nếu số lượng lớn
    """
    import_service = CrawlImportService(service, converter)
    
    # Nếu ít bài (< 10) thì xử lý sync, nếu nhiều thì background
    if len(crawl_docs) <= 5:
        return await import_service.import_bulk(crawl_docs)
    else:
        # Chạy background để tránh timeout
        background_tasks.add_task(import_service.import_bulk, crawl_docs)
        return {
            "message": "Đang xử lý import trong background",
            "total": len(crawl_docs),
            "status": "processing"
        }