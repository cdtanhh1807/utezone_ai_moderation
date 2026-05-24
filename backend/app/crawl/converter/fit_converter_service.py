import httpx
import mimetypes
from io import BytesIO
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from urllib.parse import urlparse
import uuid

from dto.post.request.add_post_request import AddPostRequest

class CrawlToPostConverter:
    # Các định dạng file được hỗ trợ
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg', '.ico'}
    VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v'}
    
    def __init__(self, upload_endpoint: str, timeout: int = 30):
        self.upload_endpoint = upload_endpoint
        self.timeout = timeout
        self.max_file_size = 50 * 1024 * 1024  # Tăng lên 50MB cho video
    
    def get_file_type(self, url: str) -> Tuple[str, str]:
        """
        Phân loại file dựa trên URL/extension
        Returns: (file_type, filename)
        file_type: 'image' | 'video' | 'document' | 'unknown'
        """
        parsed = urlparse(url)
        path = parsed.path.lower()
        filename = path.split('/')[-1] if '/' in path else "unknown"
        
        # Lấy extension
        if '.' in filename:
            ext = '.' + filename.split('.')[-1].lower()
        else:
            ext = ''
        
        if ext in self.IMAGE_EXTENSIONS:
            return ('image', filename)
        elif ext in self.VIDEO_EXTENSIONS:
            return ('video', filename)
        else:
            return ('document', filename)
    
    async def download_media(self, url: str) -> Tuple[bytes, str]:
        """Tải file từ URL (cho image và video)"""
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            async with client.stream("GET", url.strip(), headers=headers) as response:
                response.raise_for_status()
                
                content_length = response.headers.get("content-length")
                if content_length and int(content_length) > self.max_file_size:
                    raise ValueError(f"File quá lớn: {int(content_length)/1024/1024:.2f}MB")
                
                chunks = []
                async for chunk in response.aiter_bytes(chunk_size=8192):
                    chunks.append(chunk)
                    
                file_bytes = b"".join(chunks)
                
                # Lấy filename
                parsed = urlparse(url)
                filename = parsed.path.split('/')[-1].split('?')[0]
                if not filename or '.' not in filename:
                    content_type = response.headers.get("content-type", "application/octet-stream")
                    ext = mimetypes.guess_extension(content_type) or ".bin"
                    filename = f"media_{uuid.uuid4().hex[:8]}{ext}"
                    
                return file_bytes, filename
    
    async def upload_to_minio(self, file_bytes: bytes, filename: str) -> str:
        """Upload file lên MinIO và trả về file_id"""
        file_obj = BytesIO(file_bytes)
        content_type, _ = mimetypes.guess_type(filename)
        if not content_type:
            content_type = "application/octet-stream"
        
        files = {"file": (filename, file_obj, content_type)}
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(self.upload_endpoint, files=files)
            response.raise_for_status()
            result = response.json()
            
            file_id = result.get("file_id")
            if not file_id:
                raise ValueError("Upload response không chứa file_id")
            return file_id
    
    def parse_date(self, date_str: str, crawled_at: Optional[str]) -> datetime:
        """Parse date từ crawl data"""
        if crawled_at:
            try:
                return datetime.fromisoformat(crawled_at.replace("Z", "+00:00"))
            except:
                pass
            
        if date_str and "/" in date_str:
            try:
                day, month, year = date_str.split("/")
                return datetime(int(year), int(month), int(day), tzinfo=timezone.utc)
            except:
                pass
            
        return datetime.now(timezone.utc)
    
    def map_category(self, crawl_category: str) -> str:
        """Map category từ crawl sang category của hệ thống"""
        category_mapping = {
            "Các thông báo mới": "CÔNG NGHỆ THÔNG TIN",
            "Tin tức": "CÔNG NGHỆ THÔNG TIN",
            "Sự kiện": "CÔNG NGHỆ THÔNG TIN",
        }
        return category_mapping.get(crawl_category, crawl_category)
    
    def build_content_with_links(self, full_content: str, document_links: List[Dict[str, str]]) -> str:
        """
        Build content kết hợp full_content gốc + các link tài liệu
        document_links: [{"text": "filename.pdf", "url": "https://..."}, ...]
        """
        parts = []
        
        # Thêm content gốc
        if full_content and full_content.strip():
            parts.append(full_content.strip())
        
        # Thêm section tài liệu đính kèm nếu có
        if document_links:
            parts.append("\n\n📎 Tài liệu đính kèm:")
            for link in document_links:
                text = link.get("text", "Tải xuống")
                url = link.get("url", "")
                if url:
                    parts.append(f"• {text}")
                    parts.append(f"  {url}")
        
        return "\n".join(parts)
    
    async def convert(self, crawl_doc: Dict[str, Any]) -> AddPostRequest:
        """
        Chuyển đổi document crawl thành AddPostRequest
        - Ảnh/Video: Download + Upload MinIO -> thumbnails
        - PDF/DOCX/...: Giữ link -> chèn vào content
        """
        thumbnails = []  
        document_links = []  
        seen_urls = set()  # Track URLs đã xử lý để tránh duplicate
        
        # 1. Xử lý structured_content
        for item in crawl_doc.get("structured_content", []):
            item_type = item.get("type")
            
            if item_type == "image":
                src = item.get("src", "").strip()
                if not src or src in seen_urls:
                    continue
                
                file_type, filename = self.get_file_type(src)
                
                if file_type == "image":
                    try:
                        print(f"📥 Đang tải ảnh: {filename}")
                        file_bytes, _ = await self.download_media(src)
                        file_id = await self.upload_to_minio(file_bytes, filename)
                        thumbnails.append(file_id)
                        seen_urls.add(src)  # Đánh dấu đã xử lý
                        print(f"✅ Ảnh uploaded: {file_id}")
                    except Exception as e:
                        print(f"❌ Lỗi tải ảnh {src}: {e}")
                        
                elif file_type == "video":
                    try:
                        print(f"🎥 Đang tải video: {filename}")
                        file_bytes, _ = await self.download_media(src)
                        file_id = await self.upload_to_minio(file_bytes, filename)
                        thumbnails.append(file_id)
                        seen_urls.add(src)
                        print(f"✅ Video uploaded: {file_id}")
                    except Exception as e:
                        print(f"❌ Lỗi tải video {src}: {e}")
            
            elif item_type == "link":
                url = item.get("url", "").strip()
                text = item.get("text", "").strip() or url
                
                if not url or url in seen_urls:
                    continue
                
                file_type, filename = self.get_file_type(url)
                
                if file_type in ["document", "unknown"]:
                    document_links.append({
                        "text": text or filename,
                        "url": url
                    })
                    seen_urls.add(url)  # Đánh dấu đã thêm
        
        # 2. Xử lý attachments - chỉ thêm nếu URL chưa có trong seen_urls
        for att in crawl_doc.get("attachments", []):
            url = att.get("url", "").strip()
            filename = att.get("filename", "") or att.get("text", "Tải xuống")
            
            if not url or url in seen_urls:
                continue
            
            file_type, _ = self.get_file_type(url)
            
            if file_type in ["document", "unknown"]:
                document_links.append({
                    "text": filename,
                    "url": url
                })
                seen_urls.add(url)
                
            elif file_type == "image":
                try:
                    file_bytes, _ = await self.download_media(url)
                    file_id = await self.upload_to_minio(file_bytes, filename)
                    thumbnails.append(file_id)
                    seen_urls.add(url)
                except Exception as e:
                    print(f"❌ Lỗi tải attachment ảnh {url}: {e}")
        
        # 3. Xử lý image_url nếu chưa xử lý
        if crawl_doc.get("image_url"):
            img_url = crawl_doc["image_url"].strip()
            if img_url not in seen_urls:
                file_type, filename = self.get_file_type(img_url)
                
                if file_type == "image":
                    try:
                        print(f"📥 Đang tải thumbnail chính: {filename}")
                        file_bytes, _ = await self.download_media(img_url)
                        file_id = await self.upload_to_minio(file_bytes, filename)
                        thumbnails.insert(0, file_id)
                        seen_urls.add(img_url)
                        print(f"✅ Thumbnail uploaded: {file_id}")
                    except Exception as e:
                        print(f"❌ Lỗi tải thumbnail {img_url}: {e}")
        
        # 4. Build content
        content = self.build_content_with_links(
            crawl_doc.get("full_content", ""),
            document_links
        )
        
        if not content.strip() and crawl_doc.get("description"):
            content = crawl_doc["description"]
        
        post_type = "long" if len(content) > 800 else "short"
        
        categories = []
        crawl_cat = crawl_doc.get("category")
        if crawl_cat:
            categories.append(self.map_category(crawl_cat))
        if not categories:
            categories = ["CÔNG NGHỆ THÔNG TIN"]
        
        return AddPostRequest(
            title=crawl_doc.get("title", "").strip(),
            content=content,
            createdAt=self.parse_date(crawl_doc.get("date"), crawl_doc.get("crawled_at")),
            postType=post_type,
            visibility="public",
            status="active",
            createdBy="cdtanhh@gmail.com",
            category=categories,
            pollData=None,
            thumbnails=thumbnails if thumbnails else None
        )