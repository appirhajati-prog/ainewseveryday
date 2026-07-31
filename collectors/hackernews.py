import logging, requests
from config import Settings
from utils.helpers import DigestItem, utc_now

def collect(settings: Settings, logger: logging.Logger) -> list[DigestItem]:
    try:
        top_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        res = requests.get(top_url, timeout=settings.request_timeout_seconds)
        if res.status_code != 200: return []
        items = []
        for sid in res.json()[:10]:
            s_res = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=settings.request_timeout_seconds)
            if s_res.status_code == 200:
                story = s_res.json()
                if story and "title" in story:
                    title_lower = story["title"].lower()
                    if any(kw in title_lower for kw in ["ai", "gpt", "model", "llm", "openai", "claude", "tech"]) or len(items) == 0:
                        score = story.get("score", 0)
                        items.append(DigestItem(
                            title=f"هکرنیوز: {story.get('title')}",
                            description=f"یکی از موضوعات داغ و بحث‌برانگیز میان توسعه‌دهندگان در هکرنیوز.\n🔥 امتیاز محبوبیت: {score} رای مثبت\n💬 تحلیل جامعه: این موضوع بازخورد شدیدی در زمینه آینده تکنولوژی داشته است.",
                            url=story.get("url") or f"https://news.ycombinator.com/item?id={sid}",
                            source="Hacker News",
                            published_at=utc_now(),
                            metadata={"score": score},
                            is_top_trend=(len(items) == 0)
                        ))
                        if len(items) >= 2: break
        return items
    except Exception as e:
        logger.error(f"HackerNews error: {e}")
        return []
