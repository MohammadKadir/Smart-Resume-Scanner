import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Smart Resume Screener")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./resume_screener.db")
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "").strip()
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    @property
    def is_ai_mode(self) -> bool:
        """Returns True if a valid-looking OpenAI API key is set."""
        return bool(self.OPENAI_API_KEY and len(self.OPENAI_API_KEY) > 10 and not self.OPENAI_API_KEY.startswith("your_"))

    @property
    def mode_name(self) -> str:
        return "AI Mode (OpenAI)" if self.is_ai_mode else "Demo Mode (Heuristic Engine)"

settings = Settings()
