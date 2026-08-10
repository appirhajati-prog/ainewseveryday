"""
HackerNews Collector — اخبار واقعی و داغ تکنولوژی و AI
جمع‌آوری داستان‌های برتر از Firebase API هکرنیوز
"""
import logging
import requests
from datetime import datetime, timedelta, timezone
from config import Settings
from utils.helpers import DigestItem, utc_now

# کلیدواژه‌های مرتبط با AI/تکنولوژی برای فیلتر
AI_KEYWORDS = [
    "ai", "gpt", "llm", "model", "openai", "claude",
    "language model", "agent", "transformer", "neural",
    "robot", "tech", "startup", "release", "launch"
]


def _matches_ai(title: str) -> bool:
    """بررسی اینکه خبر مرتبط با AI/تکنولوژی باشد"""
    text = title.lower()
    return any(kw in text for kw in AI_KEYWORDS)


def _is_recent(timestamp: float) -> bool:
    """خبر در ۷ روز اخیر منتشر شده؟"""
    if not timestamp:
        return False
    try:
        created = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return (datetime.now(timezone.utc) - created) <= timedelta(days=7)
    except Exception:
        return False


def collect(settings: Settings, logger: logging.Logger) -> list[DigestItem]:
    items = []
    try:
        # دریافت شناسه‌های ۱۰۰ داستان برتر روز
        top_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        res = requests.get(top_url, timeout=settings.request_timeout_seconds)
        if res.status_code != 200:
            logger.warning(f"HackerNews API error: status {res.status_code}")
            return []

        story_ids = res.json()[:30]
        for i, sid in enumerate(story_ids):
            if len(items) >= 3:
                break

            s_res = requests.get(
                f"https://hacker-news.firebaseio.com/v0/item/{sid}.json",
                timeout=settings.request_timeout_seconds,
            )
            if s_res.status_code != 200:
                continue

            story = s_res.json()
            if not story or "title" not in story:
                continue

            title = story.get("title", "")
            # فیلتر: فقط اخبار مرتبط با AI/تکنولوژی
            if not _matches_ai(title):
                continue

            score = story.get("score", 0)
            num_comments = story.get("descendants", 0)
            author = story.get("by", "unknown")
            created_utc = story.get("time", 0)
            story_url = story.get("url") or f"https://news.ycombinator.com/item?id={sid}"

            desc = (
                f"یکی از برترین اخبار روز هکرنیوز با {score:,} امتیاز و {num_comments} نظر. "
                f"ارسال‌شده توسط {author}"
            )

            items.append(DigestItem(
                title=title[:150],
                description=desc,
                url=story_url,
                source="Hacker News",
                published_at=utc_now(),
                metadata={"score": score, "comments": num_comments},
                is_top_trend=(i == 0),
                is_new=_is_recent(created_utc),
            ))

        logger.info(f"HackerNews: {len(items)} top AI news collected")

    except Exception as e:
        logger.error(f"HackerNews error: {e}")

    return items