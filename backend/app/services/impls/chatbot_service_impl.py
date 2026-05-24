from core.ollama_client import get_ollama_client, OllamaSession

class ChatbotServiceImpl:
    def __init__(self):
        self.ollama = get_ollama_client(model="llama3.1:8b")
    
    async def chat(self, message: str, history: list = None):
        async with OllamaSession(self.ollama) as client:
            messages = history or []
            messages.append({"role": "user", "content": message})
            
            return await client.chat(messages, temperature=0.7)