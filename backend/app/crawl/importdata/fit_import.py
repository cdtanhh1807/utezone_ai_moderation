import httpx
import asyncio

from typing import Dict, Any, Tuple

async def fit_import():
    url = "http://localhost:8000/crawl/crawl_import/import_single"
    
    data_crawl = {}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data_crawl, timeout=120.0)
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Response: {result}")
            
            if result.get("success"):
                print("✅ Import thành công!")
            else:
                print(f"❌ Import thất bại: {result.get('message')}")
                
        except Exception as e:
            print(f"Error: {e}")


############
async def import_single_article(data_crawl: Dict[str, Any], api_url: str = "http://localhost:8000/crawl/crawl_import/import_single") -> Tuple[bool, Dict]:

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(api_url, json=data_crawl, timeout=120.0)
            result = response.json()
            
            if response.status_code == 200 and result.get("success"):
                print(f"✅ Import thành công: {data_crawl.get('title', 'Unknown')[:50]}...")
                return True, result
            else:
                error_msg = result.get('message', 'Unknown error')
                print(f"❌ Import thất bại: {error_msg}")
                return False, result
                
        except httpx.TimeoutException:
            print(f"⏱️ Timeout khi import: {data_crawl.get('title', 'Unknown')[:50]}")
            return False, {"error": "Timeout after 120s"}
        except Exception as e:
            print(f"❌ Lỗi kết nối: {e}")
            return False, {"error": str(e)}


if __name__ == "__main__":
    asyncio.run(fit_import())