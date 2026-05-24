import json
import re
import os
import asyncio
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup, NavigableString
from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict
from playwright.async_api import async_playwright
from dataclasses import asdict
from crawl.importdata.fit_import import import_single_article

@dataclass
class ArticleDetail:
    article_id: str
    title: str
    date: str
    image_url: str
    article_url: str
    description: str
    category: str
    full_content: str = ""
    html_content: str = ""
    structured_content: List[Dict] = field(default_factory=list)
    author: str = ""
    views: str = ""
    attachments: List[Dict] = field(default_factory=list)
    crawled_at: str = ""
    
    def __post_init__(self):
        if not self.crawled_at:
            self.crawled_at = datetime.now().isoformat()


class FITPlaywrightCrawler:
    BASE_URL = "https://fit.hcmute.edu.vn"
    
    CATEGORIES = {
        "thong-bao": {
            "name": "Các thông báo mới",
            "url": "https://fit.hcmute.edu.vn/TopicId/05556b7b-ed01-4261-9390-4583add544ea/cac-thong-bao-moi"
        },
        "hoat-dong": {
            "name": "Các hoạt động nổi bật", 
            "url": "https://fit.hcmute.edu.vn/TopicId/9525ab2d-5a64-41ae-b53d-d4b9631adb36/cac-hoat-dong-noi-bat"
        },
        "viec-lam": {
            "name": "Việc làm doanh nghiệp",
            "url": "https://fit.hcmute.edu.vn/TopicId/d48b62d3-576a-412b-8a67-dc90214479fd/viec-lam-doanh-nghiep"
        }
    }
    
    def __init__(self, headless: bool = True, delay: float = 0.5):
        self.headless = headless
        self.delay = delay
        self.browser = None
        self.context = None
        
    async def init(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        print("Browser initialized")
    
    async def close(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        await self.playwright.stop()
        print("Browser closed")
    
    def parse_list_item(self, html: str, category_key: str) -> List[ArticleDetail]:
        soup = BeautifulSoup(html, 'lxml')
        items = soup.select('li:has(a.title_topicdisplay)')
        
        articles = []
        for li in items:
            try:
                link_elem = li.select_one('a.title_topicdisplay')
                if not link_elem:
                    continue
                
                full_text = link_elem.get_text(strip=True)
                
                date_match = re.search(r'\((\d{2}/\d{2}/\d{4})\)$', full_text)
                date = date_match.group(1) if date_match else ""
                
                title = re.sub(r'\s*\(\d{2}/\d{2}/\d{4}\)$', '', full_text).strip()
                
                href = link_elem.get('href', '')
                article_url = urljoin(self.BASE_URL, href)
                
                article_id_match = re.search(r'ArticleId=([^&]+)', article_url)
                article_id = article_id_match.group(1) if article_id_match else ""
                
                img_elem = li.select_one('img')
                image_src = img_elem.get('src', '') if img_elem else ""
                image_url = urljoin(self.BASE_URL, image_src)
                
                desc_elem = li.select_one('h3.h3_content')
                description = desc_elem.get_text(strip=True) if desc_elem else ""
                
                articles.append(ArticleDetail(
                    article_id=article_id,
                    title=title,
                    date=date,
                    image_url=image_url,
                    article_url=article_url,
                    description=description,
                    category=self.CATEGORIES[category_key]["name"]
                ))
            except Exception as e:
                print(f"    Parse error: {e}")
        
        return articles
    
    async def crawl_category(self, category_key: str, max_pages: int = 0) -> List[ArticleDetail]:
        cat = self.CATEGORIES[category_key]
        print(f"\n[{category_key}] {cat['name']}")
        
        all_articles = []
        page = await self.context.new_page()
        
        try:
            print(f"   Opening page 1...")
            await page.goto(cat['url'], wait_until="networkidle")
            await asyncio.sleep(1)
            
            current_page = 1
            
            while True:
                print(f"\n   Page {current_page}")
                
                html = await page.content()
                articles = self.parse_list_item(html, category_key)
                print(f"      Found {len(articles)} items")
                
                for article in articles:
                    all_articles.append(article)
                    print(f"      {article.title[:50]}...")
                
                # Check next button
                next_selectors = [
                    '.ctl05_ctl01_lbtNext',
                    '#ctl05_ctl01_lbtNext',
                    'a[id*="lbtNext"]',
                    'a[href*="lbtNext"]'
                ]
                
                next_btn = None
                for selector in next_selectors:
                    try:
                        next_btn = await page.query_selector(selector)
                        if next_btn:
                            break
                    except:
                        continue
                
                if not next_btn:
                    print(f"      No next button")
                    break
                
                is_disabled = await next_btn.is_disabled()
                if is_disabled:
                    print(f"      Next button disabled")
                    break
                
                if max_pages > 0 and current_page >= max_pages:
                    print(f"      Max pages reached")
                    break
                
                print(f"      Clicking next...")
                try:
                    await next_btn.click()
                    await page.wait_for_load_state("networkidle")
                    await asyncio.sleep(1.5)
                    current_page += 1
                except Exception as e:
                    print(f"      Click failed: {e}")
                    break
            
            print(f"\n   Total: {len(all_articles)} articles")
            
        finally:
            await page.close()
        
        return all_articles
    
    # ==================== FIXED: EXTRACT STRUCTURED CONTENT ====================
    
    def extract_structured_content(self, element) -> List[Dict]:
        """
        Trích xuất structured content từ articleContent
        Giữ nguyên logic từ file cũ để đảm bảo hoạt động đúng
        """
        content_blocks = []
        
        # Duyệt qua tất cả descendants
        for child in element.descendants:
            # Bỏ qua NavigableString
            if isinstance(child, NavigableString):
                continue
            
            # Chỉ xử lý các thẻ cụ thể
            if child.name not in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                                 'ul', 'ol', 'table', 'img', 'a', 'br', 'hr', 'span']:
                continue
            
            # Bỏ qua script/style
            if child.name in ['script', 'style']:
                continue
            
            # Kiểm tra nếu là thẻ con trực tiếp của articleContent hoặc các container chính
            parent = child.find_parent(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'li', 'td', 'span'])
            if parent and parent != element and parent.name not in ['div', 'p']:
                # Nếu parent cũng là block-level element, bỏ qua để tránh duplicate
                if parent.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'table']:
                    continue
            
            block = self._process_element(child)
            if block and block not in content_blocks:  # Tránh duplicate
                content_blocks.append(block)
        
        # Nếu không có cấu trúc rõ ràng, thử cách khác
        if not content_blocks:
            # Tìm tất cả links trong articleContent
            for link in element.find_all('a', href=True):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                if text and href:
                    content_blocks.append({
                        "type": "link",
                        "url": urljoin(self.BASE_URL, href),
                        "text": text
                    })
        
        return content_blocks
    
    def _process_element(self, elem) -> Optional[Dict]:
        """Xử lý 1 element thành block có cấu trúc"""
        
        # Heading
        if elem.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            content = elem.get_text(strip=True)
            if content:
                return {
                    "type": "heading",
                    "level": int(elem.name[1]),
                    "content": content
                }
        
        # List
        if elem.name in ['ul', 'ol']:
            items = []
            for li in elem.find_all('li', recursive=False):
                item_text = li.get_text(separator=' ', strip=True)
                if item_text:
                    items.append(item_text)
            if items:
                return {
                    "type": "list",
                    "list_type": "bullet" if elem.name == 'ul' else "numbered",
                    "items": items
                }
            return None
        
        # Table
        if elem.name == 'table':
            rows = []
            for tr in elem.find_all('tr'):
                row_data = []
                for td in tr.find_all(['td', 'th']):
                    row_data.append(td.get_text(strip=True))
                if row_data:
                    rows.append(row_data)
            if rows:
                return {
                    "type": "table",
                    "rows": rows
                }
            return None
        
        # Image
        if elem.name == 'img':
            src = elem.get('src', '')
            if src:
                return {
                    "type": "image",
                    "src": urljoin(self.BASE_URL, src),
                    "alt": elem.get('alt', ''),
                    "title": elem.get('title', '')
                }
            return None
        
        # Link đơn lẻ (không nằm trong paragraph)
        if elem.name == 'a':
            href = elem.get('href', '')
            text = elem.get_text(strip=True)
            # Chỉ lấy link có text và không nằm trong thẻ p (vì sẽ được xử lý trong paragraph)
            if text and href and not elem.find_parent('p'):
                return {
                    "type": "link",
                    "url": urljoin(self.BASE_URL, href),
                    "text": text
                }
        
        # Paragraph hoặc Div chứa text
        if elem.name in ['p', 'div', 'span']:
            # Bỏ qua nếu chỉ chứa 1 thẻ con duy nhất là block khác
            children = [c for c in elem.children 
                       if not isinstance(c, NavigableString) or str(c).strip()]
            if len(children) == 1 and children[0].name in ['div', 'p', 'ul', 'ol', 'table']:
                return None
            
            text = elem.get_text(separator=' ', strip=True)
            if text:
                # Tìm links trong text
                links = []
                for a in elem.find_all('a'):
                    links.append({
                        "text": a.get_text(strip=True),
                        "url": urljoin(self.BASE_URL, a.get('href', ''))
                    })
                
                return {
                    "type": "paragraph",
                    "content": text,
                    "links": links if links else ""
                }
        
        return None
    
    async def crawl_detail(self, article: ArticleDetail) -> ArticleDetail:
        print(f"      {article.title[:40]}...")
        
        page = await self.context.new_page()
        
        try:
            await page.goto(article.article_url, wait_until="networkidle")
            await asyncio.sleep(0.5)
            
            html = await page.content()
            soup = BeautifulSoup(html, 'lxml')
            
            # Lấy từ articleContent
            article_content = soup.select_one('.articleContent')
            
            if article_content:
                print(f"      Found .articleContent")
                
                # Clean
                for script in article_content(['script', 'style', 'iframe']):
                    script.decompose()
                
                article.html_content = str(article_content)
                article.full_content = article_content.get_text(separator='\n', strip=True)
                
                # FIXED: Dùng hàm extract_structured_content đã sửa
                article.structured_content = self.extract_structured_content(article_content)
                print(f"      Structured: {len(article.structured_content)} blocks")
                
                # Attachments
                for link in article_content.find_all('a', href=True):
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    if any(href.lower().endswith(ext) for ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar']):
                        article.attachments.append({
                            "filename": os.path.basename(href),
                            "url": urljoin(self.BASE_URL, href),
                            "text": text
                        })
                    elif re.search(r'(tải|download|đính kèm)', text, re.I):
                        article.attachments.append({
                            "filename": os.path.basename(href) or "download",
                            "url": urljoin(self.BASE_URL, href),
                            "text": text
                        })
            else:
                print(f"      Không tìm thấy .articleContent")
            
            # Metadata
            author_elem = soup.select_one('.article-author, .author')
            if author_elem:
                article.author = author_elem.get_text(strip=True)
            
            views_elem = soup.select_one('.views, [class*="view"]')
            if views_elem:
                article.views = views_elem.get_text(strip=True)
            
        except Exception as e:
            print(f"      Error: {e}")
        finally:
            await page.close()
        
        return article
    
    async def crawl_details(self, articles: List[ArticleDetail]) -> List[ArticleDetail]:
        print(f"\nCrawling details for {len(articles)} articles...")
        
        results = []
        for i, article in enumerate(articles, 1):
            print(f"   [{i}/{len(articles)}]")
            result = await self.crawl_detail(article)
            results.append(result)
            await asyncio.sleep(self.delay)
        
        return results

    # def save(self, articles: List[ArticleDetail], output_file="fit_output/articles.json"):
    #     os.makedirs(os.path.dirname(output_file), exist_ok=True)

    #     # Load dữ liệu cũ
    #     existing_data = []
    #     existing_ids = set()

    #     if os.path.exists(output_file):
    #         try:
    #             with open(output_file, "r", encoding="utf-8") as f:
    #                 existing_data = json.load(f)
    #                 existing_ids = set(a["article_id"] for a in existing_data)
    #         except:
    #             pass

    #     # Lọc bài mới
    #     new_articles = []
    #     for a in articles:
    #         if a.article_id not in existing_ids:
    #             new_articles.append(asdict(a))
    #         else:
    #             print(f"Skip: {a.article_id}")

    #     # Append
    #     all_data = existing_data + new_articles

    #     with open(output_file, "w", encoding="utf-8") as f:
    #         json.dump(all_data, f, ensure_ascii=False, indent=2)

    #     print(f"\nAdded {len(new_articles)} new articles")
    #     print(f"Total: {len(all_data)} articles")

    ############### Save auto
    async def save(self, articles, output_file="crawl/output/fit_output/articles.json"):
        import os
        import json
        
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Load dữ liệu cũ
        existing_data = []
        existing_ids = set()

        if os.path.exists(output_file):
            try:
                with open(output_file, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                    existing_ids = set(a["article_id"] for a in existing_data)
            except Exception as e:
                print(f"⚠️ Không thể đọc file cũ: {e}")

        # === FILTER: Loại bỏ bài không có nội dung ===
        valid_articles = []
        skip_count = 0
        
        for article in articles:
            # Kiểm tra nếu cả 3 field đều rỗng
            full_content_empty = not article.full_content or not article.full_content.strip()
            html_empty = not article.html_content or not article.html_content.strip()
            structured_empty = not article.structured_content or len(article.structured_content) == 0
            
            if full_content_empty and html_empty and structured_empty:
                print(f"⏩ Skip (thiếu nội dung): {article.article_id} - {article.title[:50]}...")
                skip_count += 1
                continue
            
            valid_articles.append(article)
        
        if skip_count > 0:
            print(f"\n⚠️ Đã loại {skip_count} bài không đủ nội dung (lỗi crawl)")
        
        if not valid_articles:
            print("❌ Không có bài nào hợp lệ để import")
            return []

        # Xử lý import các bài hợp lệ
        newly_imported = []
        
        for article in valid_articles:
            article_id = article.article_id
            
            if article_id in existing_ids:
                print(f"⏩ Skip (đã tồn tại trong JSON): {article_id}")
                continue
            
            article_dict = asdict(article)
            
            print(f"\n📤 Đang import: {article.title[:60]}...")
            success, result = await import_single_article(article_dict)
            
            if success:
                newly_imported.append(article_dict)
                existing_ids.add(article_id)
                print(f"✅ Import OK -> Thêm vào JSON")
            else:
                print(f"❌ Import FAILED -> Bỏ qua, không lưu JSON")
            
            await asyncio.sleep(1)

        # Lưu file JSON
        if newly_imported:
            all_data = existing_data + newly_imported
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 Đã lưu {len(newly_imported)} bài mới vào {output_file}")
            print(f"📊 Tổng số bài trong JSON: {len(all_data)}")
        else:
            print(f"\n⚠️ Không có bài mới nào được import thành công để lưu")

        return newly_imported
    
    # async def run(self, category: str = "all", max_pages: int = 0, 
    #               fetch_detail: bool = True) -> List[ArticleDetail]:
    #     print("FIT.HCMUTE Crawler")
    #     print(f"   Category: {category}")
    #     print(f"   Max pages: {'unlimited' if max_pages == 0 else max_pages}")
        
    #     await self.init()
        
    #     try:
    #         all_articles = []
    #         if category == "all":
    #             for key in self.CATEGORIES:
    #                 articles = await self.crawl_category(key, max_pages)
    #                 all_articles.extend(articles)
    #         else:
    #             all_articles = await self.crawl_category(category, max_pages)
            
    #         print(f"\n Total from lists: {len(all_articles)} articles")
            
    #         if fetch_detail and all_articles:
    #             all_articles = await self.crawl_details(all_articles)
            
    #         if all_articles:
    #             self.save(all_articles)
                
    #             print(f"\n DONE!")
    #             print(f"   Total: {len(all_articles)} articles")
    #             by_cat = {}
    #             for a in all_articles:
    #                 by_cat[a.category] = by_cat.get(a.category, 0) + 1
    #             for cat, count in by_cat.items():
    #                 print(f"   - {cat}: {count}")
                
    #             # Stats
    #             with_structured = sum(1 for a in all_articles if a.structured_content)
    #             print(f"   With structured content: {with_structured}")
            
    #         return all_articles
            
    #     finally:
    #         await self.close()
    async def run(self, category: str = "all", max_pages: int = 0, 
                  fetch_detail: bool = True, auto_import: bool = True) -> List[ArticleDetail]:
        print("FIT.HCMUTE Crawler")
        print(f"   Category: {category}")
        print(f"   Max pages: {'unlimited' if max_pages == 0 else max_pages}")
        print(f"   Auto import: {'Bật' if auto_import else 'Tắt'}")
        
        await self.init()
        
        try:
            all_articles = []
            if category == "all":
                for key in self.CATEGORIES:
                    articles = await self.crawl_category(key, max_pages)
                    all_articles.extend(articles)
            else:
                all_articles = await self.crawl_category(category, max_pages)
            
            print(f"\n📥 Tổng từ lists: {len(all_articles)} articles")
            
            if fetch_detail and all_articles:
                all_articles = await self.crawl_details(all_articles)
            
            if all_articles:
                # ===== THAY ĐỔI Ở ĐÂY =====
                if auto_import:
                    await self.save(all_articles)  # Import rồi mới lưu
                else:
                    self.save(all_articles)  # Lưu thường (cũ)
                
                # Stats
                print(f"\n✅ DONE!")
                by_cat = {}
                for a in all_articles:
                    by_cat[a.category] = by_cat.get(a.category, 0) + 1
                for cat, count in by_cat.items():
                    print(f"   - {cat}: {count}")
                
                with_structured = sum(1 for a in all_articles if a.structured_content)
                print(f"   Có structured content: {with_structured}")
            
            return all_articles
            
        finally:
            await self.close()


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="FIT.HCMUTE Crawler (Fixed)")
    parser.add_argument("-c", "--category", 
                       choices=['thong-bao', 'hoat-dong', 'viec-lam', 'all'],
                       default='all')
    parser.add_argument("-p", "--pages", type=int, default=0,
                       help="Max pages per category (0 = unlimited)")
    parser.add_argument("--no-detail", action="store_true")
    parser.add_argument("--visible", "-v", action="store_true",
                       help="Show browser window")
    parser.add_argument("-d", "--delay", type=float, default=0.5)
    
    args = parser.parse_args()
    
    crawler = FITPlaywrightCrawler(
        headless=not args.visible,
        delay=args.delay
    )
    
    await crawler.run(
        category=args.category,
        max_pages=args.pages,
        fetch_detail=not args.no_detail
    )


if __name__ == "__main__":
    asyncio.run(main())