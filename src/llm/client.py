from groq import Groq
from src.config import Config

class LLMClient:
    def __init__(self, provider="groq"):
        self.provider = provider
        # Force Groq client initialization
        self.client = Groq(api_key=Config.GROQ_API_KEY)
    
    def generate(self, prompt: str, model: str = None, json_mode: bool = False) -> str:
        """
        Generic generation method.
        """
        model = model or Config.DEFAULT_MODEL
        
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            response_format={"type": "json_object"} if json_mode else None
        )
        return response.choices[0].message.content
