import os
from dataclasses import dataclass
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

@dataclass
class Settings:
    telegram_bot_token: str
    telegram_chat_id: str
    max_digest_items: int = 5
    request_timeout_seconds: int = 15
    github_token: str = ""

    @classmethod
    def from_environment(cls) -> "Settings":
        token = os.getenv("TELEGRAM_TOKEN")
        chat_id = os.getenv("CHAT_ID")
        if not token or not chat_id:
            raise ValueError("TELEGRAM_TOKEN and CHAT_ID must be set in .env")
        return cls(
            telegram_bot_token=token,
            telegram_chat_id=chat_id,
            max_digest_items=int(os.getenv("MAX_DIGEST_ITEMS", 5)),
            request_timeout_seconds=int(os.getenv("REQUEST_TIMEOUT", 15)),
            github_token=os.getenv("GITHUB_TOKEN", ""),
        )
