"""
arXiv Collector — مقالات واقعی و اخیر هوش مصنوعی
جمع‌آوری مقالات روز از arXiv API با فیلتر هوشمند
"""
import logging
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, date, timedelta, timezone
from config import Settings
from utils.helpers import DigestItem, utc_now

# دسته‌بندی‌های آرکسیو مرتبط با هوش مصنوعی
AI_CATEGORIES = ["cs.AI", "cs.CL", "cs.CV", "cs.LG", "cs.MA"]

# کلیدواژه‌های موضوعی برای اطمینان از مرتبط بودن مقاله با AI
AI_KEYWORDS = [
    "llm", "language model", "transformer", "diffusion",
    "agent", "retrieval", "reinforcement", "vision",
    "robotics", "neural", "generative", "foundation model",
    "machine learning", "deep learning", "gpt", "openai"
]


def _matches_ai(title: str, summary: str) -> bool:
    """بررسی اینکه مقاله واقعاً مرتبط با هوش مصنوعی باشد"""
    text = f"{title} {summary}".lower()
    return any(kw in text for kw in AI_KEYWORDS)


def _is_recent(published_str: str) -> bool:
    """بررسی اینکه مقاله در ۷ روز اخیر منتشر شده باشد"""
    if not published_str:
        return False
    try:
        pub_date = datetime.fromisoformat(published_str.replace("Z", "+00:00")).date()
        return (date.today() - pub_date) <= timedelta(days=7)
    except Exception:
        return False


def collect(settings: Settings, logger: logging.Logger) -> list[DigestItem]:
    items = []
    try:
        cat_query = "+OR+".join(f"cat:{c}" for c in AI_CATEGORIES)
        url = (
            "http://export.arxiv.org/api/query"
            f"?search_query={cat_query}"
            "&sortBy=submittedDate&sortOrder=descending&max_results=8"
        )
        res = requests.get(url, timeout=settings.request_timeout_seconds)
        if res.status_code != 200:
            logger.warning(f"arXiv API error: status {res.status_code}")
            return []

        root = ET.fromstring(res.content)
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        for i, entry in enumerate(root.findall("atom:entry", ns)):
            title_elem = entry.find("atom:title", ns)
            summary_elem = entry.find("atom:summary", ns)
            id_elem = entry.find("atom:id", ns)
            published_elem = entry.find("atom:published", ns)

            title = title_elem.text.strip().replace("\n", " ") if title_elem is not None else "بدون عنوان"
            summary = summary_elem.text.strip().replace("\n", " ") if summary_elem is not None else "بدون خلاصه"
            link = id_elem.text.strip() if id_elem is not None else "https://arxiv.org"
            published = published_elem.text.strip()[:10] if published_elem is not None else ""

            # فیلتر: فقط مقالات مرتبط با هوش مصنوعی
            if not _matches_ai(title, summary):
                continue

            items.append(DigestItem(
                title=title[:150],
                description=summary[:400] + ("..." if len(summary) > 400 else ""),
                url=link,
                source="arXiv",
                published_at=utc_now(),
                metadata={"published": published, "score": 80},
                is_top_trend=(i == 0),
                is_new=_is_recent(published),
            ))

        logger.info(f"arXiv: {len(items)} AI papers collected")

    except Exception as e:
        logger.error(f"arXiv error: {e}")

    return items