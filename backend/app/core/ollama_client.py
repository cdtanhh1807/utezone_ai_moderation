import asyncio
import base64
import aiohttp
from typing import Optional


class OllamaClient:
    """
    Client để gọi Ollama API.
    Singleton pattern để tránh tạo nhiều session.

    UPDATE v2: generate_with_image hỗ trợ cả URL và local file path.
    """

    DEFAULT_BASE_URL = "http://10.122.240.252:11434"
    DEFAULT_MODEL = "llama3.1:8b"
    DEFAULT_TIMEOUT = 60
    DEFAULT_VISION_MODEL = "qwen2.5vl:7b"

    _instance = None
    _session: Optional[aiohttp.ClientSession] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self, 
        base_url: str = None, 
        model: str = None, 
        vision_model: str = None,
        timeout: int = None
    ):
        if hasattr(self, '_initialized'):
            return

        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.model = model or self.DEFAULT_MODEL
        self.vision_model = vision_model or self.DEFAULT_VISION_MODEL
        self.timeout = timeout or self.DEFAULT_TIMEOUT

        self._initialized = True

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def generate(
        self, 
        prompt: str, 
        system: Optional[str] = None, 
        temperature: float = 0.3,
        num_predict: int = 200
    ) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": num_predict
            }
        }

        if system:
            payload["system"] = system

        session = await self._get_session()

        try:
            async with session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise Exception(f"Ollama HTTP {resp.status}: {error_text}")

                data = await resp.json()
                return data.get("response", "").strip()

        except aiohttp.ClientError as e:
            raise Exception(f"Cannot connect to Ollama at {self.base_url}: {str(e)}")
        except asyncio.TimeoutError:
            raise Exception(f"Ollama request timeout after {self.timeout}s")

    async def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7
    ) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }

        session = await self._get_session()

        async with session.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        ) as resp:
            if resp.status != 200:
                raise Exception(f"Ollama error: {await resp.text()}")

            data = await resp.json()
            return data.get("message", {}).get("content", "").strip()

    async def health_check(self) -> bool:
        try:
            session = await self._get_session()
            async with session.get(
                f"{self.base_url}/api/tags",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                return resp.status == 200
        except:
            return False

    async def generate_with_image(
        self,
        prompt: str,
        image_urls: list[str],
        system: Optional[str] = None,
        temperature: float = 0.3,
        num_predict: int = 500
    ) -> str:
        """
        Generate text từ Ollama với vision (ảnh).

        UPDATE v2: Hỗ trợ cả URL (http://...) và local file path (/tmp/...).
        """
        images_base64 = []

        for url in image_urls:
            try:
                if url.startswith("http://") or url.startswith("https://"):
                    # Download từ URL
                    async with aiohttp.ClientSession() as temp_session:
                        async with temp_session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                            if resp.status == 200:
                                image_bytes = await resp.read()
                                image_b64 = base64.b64encode(image_bytes).decode('utf-8')
                                images_base64.append(image_b64)
                            else:
                                print(f"Failed to download image: {url}, status: {resp.status}")
                else:
                    # Local file path
                    with open(url, "rb") as f:
                        image_bytes = f.read()
                        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
                        images_base64.append(image_b64)
            except Exception as e:
                print(f"Error loading image {url}: {e}")

        if not images_base64:
            raise Exception("Không thể tải ảnh nào từ URLs/paths")

        payload = {
            "model": self.vision_model,
            "prompt": prompt,
            "images": images_base64,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": num_predict
            }
        }

        if system:
            payload["system"] = system

        session = await self._get_session()

        try:
            async with session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise Exception(f"Ollama HTTP {resp.status}: {error_text}")

                data = await resp.json()
                return data.get("response", "").strip()

        except asyncio.TimeoutError:
            raise Exception(f"Ollama vision request timeout after {self.timeout}s")


def get_ollama_client(
    base_url: str = None,
    model: str = None,
    vision_model: str = None,
    timeout: int = None
) -> OllamaClient:
    return OllamaClient(base_url, model, vision_model, timeout)


class OllamaSession:
    def __init__(self, client: OllamaClient = None):
        self.client = client or get_ollama_client()

    async def __aenter__(self):
        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.close()
