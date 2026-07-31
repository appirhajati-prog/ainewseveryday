import logging, requests
from config import Settings
from utils.helpers import DigestItem, utc_now

def collect(settings: Settings, logger: logging.Logger) -> list[DigestItem]:
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get("https://www.reddit.com/r/artificial/hot.json?limit=2", headers=headers, timeout=settings.request_timeout_seconds)
        if res.status_code != 200: return []
        items = []
        for i, post in enumerate(res.json().get("data", {}).get("children", [])):
            p_data = post.get("data", {})
            score = p_data.get("score", 0)
            items.append(DigestItem(
                title=f"ردیت (r/artificial): {p_data.get('title')}",
                description=f"پست پربحث و محبوب در جامعه هوش مصنوعی ردیت.\n👍 امتیاز کاربران: {score} | 💬 تعداد نظرات: {p_data.get('num_comments', 0)}\n📌 محور بحث: تبادل نظر کاربران پیرامون قابلیت‌ها و ابزارهای جدید.",
                url=f"https://reddit.com{p_data.get('permalink')}",
                source="Reddit",
                published_at=utc_now(),
                metadata={"score": score},
                is_top_trend=(i == 0)
            ))
        return items
    except Exception as e:
        logger.error(f"Reddit error: {e}")
        return []
