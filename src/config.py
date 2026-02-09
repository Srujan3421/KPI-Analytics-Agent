import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(env_path)

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "kpi_agent_db")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    
    # LLM Selection (default to Groq/Llama3 for speed)
    DEFAULT_MODEL = "llama-3.3-70b-versatile"

    @classmethod
    def validate(cls):
        if not cls.GROQ_API_KEY:
            raise ValueError("Missing API Key: Set GROQ_API_KEY in .env")
