"""
Reddit Collector — پست‌های داغ و واقعی هوش مصنوعی از ساب‌ردیت‌های تخصصی
r/LocalLLaMA، r/MachineLearning و r/artificial
"""
import logging
import requests
from datetime import datetime, timedelta, timezone
from config import Settings
from utils.helpers import DigestItem, utc_now

# ساب‌ردیت‌های تخصصی هوش مصنوعی
SUBREDDITS = ["LocalLLaMA", "MachineLearning", "artificial"]

# کلیدواژه‌های مرتبط با AI برای فیلتر پست‌های نامرتبط
AI_KEYWORDS = [
    "llm", "gpt", "model", "agent", "rag", "diffusion",
    "openai", "claude", "training", "inference", "fine-tune",
    "fine tune", "quantization", "transformer", "neural",
    "machine learning", "deep learning", "ai", "artificial"
]


def _matches_ai(title: str, selftext: str) -> bool:
    """بررسی اینکه پست واقعاً مرتبط با هوش مصنوعی باشد"""
    text = f"{title} {selftext}".lower()
    return any(kw in text for kw in AI_KEYWORDS)


def _is_recent(created_utc: float) -> bool:
    """پست در ۷ روز اخیر ایجاد شده؟"""
    if not created_utc:
        return False
    try:
        created = datetime.fromtimestamp(created_utc, tz=timezone.utc)
        return (datetime.now(timezone.utc) - created) <= timedelta(days=7)
    except Exception:
        return False


def collect(settings: Settings, logger: logging.Logger) -> list[DigestItem]:
    items = []
    headers = {"User-Agent": "AINewsEverydayBot/2.0 (by /u/ai_news_bot)"}

    for sub in SUBREDDITS:
        try:
            url = f"https://www.reddit.com/r/{sub}/hot.json?limit=5"
            res = requests.get(url, headers=headers, timeout=settings.request_timeout_seconds)
            if res.status_code != 200:
                logger.warning(f"Reddit r/{sub}: status {res.status_code}")
                continue

            data = res.json().get("data", {}).get("children", [])
            for i, child in enumerate(data):
                p = child.get("data", {})
                if p.get("stickied"):
                    continue  # پست‌های پین‌شده را رد کن

                title = p.get("title", "")
                selftext = p.get("selftext", "")
                score = p.get("score", 0)
                num_comments = p.get("num_comments", 0)
                permalink = p.get("permalink", "")
                created_utc = p.get("created_utc", 0)

                # فیلتر: فقط پست‌های مرتبط با هوش مصنوعی
                if not _matches_ai(title, selftext):
                    continue

                desc = (
                    selftext[:300] + ("..." if len(selftext) > 300 else "")
                    if selftext
                    else f"بحث داغ در r/{sub} با {score:,} امتیاز و {num_comments} نظر."
                )

                items.append(DigestItem(
                    title=f"[r/{sub}] {title}"[:150],
                    description=desc,
                    url=f"https://reddit.com{permalink}" if permalink else f"https://reddit.com/r/{sub}",
                    source=f"Reddit (r/{sub})",
                    published_at=utc_now(),
                    metadata={"score": score, "comments": num_comments},
                    is_top_trend=(i == 0 and sub == "LocalLLaMA"),
                    is_new=_is_recent(created_utc),
                ))
                if len(items) >= 3:
                    break

        except Exception as e:
            logger.warning(f"Reddit {sub} error: {e}")

    logger.info(f"Reddit: {len(items)} AI posts collected")
    return items