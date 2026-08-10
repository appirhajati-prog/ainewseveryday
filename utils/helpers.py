import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

@dataclass
class DigestItem:
    title: str
    description: str
    url: str
    source: str
    published_at: Optional[datetime] = None
    metadata: dict = field(default_factory=dict)
    score: float = 0.0
    is_top_trend: bool = False  # مشخص‌کننده ترندترین خبر آن منبع
    is_new: bool = False        # مشخص‌کننده پروژه/مقاله جدید (کمتر از ۷ روز)

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    return " ".join(text.split())