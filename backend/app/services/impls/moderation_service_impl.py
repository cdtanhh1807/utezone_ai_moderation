from core.ollama_client import OllamaSession, get_ollama_client

class ModerationServiceImpl:
    def __init__(self):
        self.ollama = get_ollama_client(model="llama3.2:3b")
    
    async def check_content(self, text: str):
        async with OllamaSession(self.ollama) as client:
            prompt = f"Kiểm tra nội dung: {text}"
            return await client.generate(prompt, temperature=0.1)