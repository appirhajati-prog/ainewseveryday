"""
Product Hunt Collector — ابزارهای واقعی AI روز
جمع‌آوری از فید عمومی Product Hunt (بدون نیاز به توکن API)
"""
import logging
import re
import requests
from datetime import datetime, timedelta, timezone
from config import Settings
from utils.helpers import DigestItem, utc_now


def _parse_date(date_str: str):
    """تبدیل تاریخ RSS به datetime"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
    except Exception:
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            return None


def _is_recent(date_str: str) -> bool:
    """آیتم در ۷ روز اخیر منتشر شده؟"""
    d = _parse_date(date_str)
    if not d:
        return False
    return (datetime.now(timezone.utc) - d) <= timedelta(days=7)


def _extract_votes(description: str) -> int:
    """استخراج تعداد آرا از متن توضیح فید (مثل: Votes: 523)"""
    if not description:
        return 0
    m = re.search(r"Votes?:\s*([\d,]+)", description, re.IGNORECASE)
    if m:
        return int(m.group(1).replace(",", ""))
    return 0


AI_KEYWORDS = [
    "ai", "gpt", "llm", "agent", "bot", "assistant",
    "intelligence", "machine learning", "artificial",
]


def _matches_ai(title: str, description: str) -> bool:
    """فقط ابزارهای مرتبط با هوش مصنوعی برگردان"""
    text = f"{title} {description}".lower()
    return any(kw in text for kw in AI_KEYWORDS)


def collect(settings: Settings, logger: logging.Logger) -> list[DigestItem]:
    items = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AINewsBot/1.0"}

    # اول: فید تخصصی موضوع هوش مصنوعی (متمرکزترین منبع)
    feeds = [
        "https://www.producthunt.com/topics/artificial-intelligence/feed",
        "https://www.producthunt.com/feed",
    ]

    import xml.etree.ElementTree as ET

    for feed_url in feeds:
        try:
            res = requests.get(feed_url, headers=headers, timeout=settings.request_timeout_seconds)
            if res.status_code != 200:
                logger.warning(f"ProductHunt feed {feed_url}: status {res.status_code}")
                continue

            root = ET.fromstring(res.content)
            channel = root.find("channel")
            if channel is None:
                continue

            for i, item in enumerate(channel.findall("item")):
                title = (item.findtext("title") or "").strip()
                link = (item.findtext("link") or "https://www.producthunt.com").strip()
                desc = (item.findtext("description") or "").strip()
                pub_date = item.findtext("pubDate") or ""

                if not title:
                    continue

                # در فید تخصصی AI دیگر نیازی به فیلتر نیست؛
                # در فید عمومی، فقط موارد مرتبط با AI را نگه دار
                if "topics/artificial-intelligence" in feed_url or _matches_ai(title, desc):
                    # حذف تگ‌های HTML از توضیحات
                    clean_desc = re.sub(r"<[^>]+>", " ", desc)
                    clean_desc = " ".join(clean_desc.split())[:300]
                    votes = _extract_votes(desc)

                    items.append(DigestItem(
                        title=title[:150],
                        description=clean_desc or "ابزار جدید هوش مصنوعی منتشر شده در Product Hunt",
                        url=link,
                        source="Product Hunt",
                        published_at=utc_now(),
                        metadata={"votes": votes, "score": votes},
                        is_top_trend=(i == 0),
                        is_new=_is_recent(pub_date),
                    ))
                    if len(items) >= 3:
                        break

            if items:
                logger.info(f"ProductHunt: {len(items)} AI products collected from {feed_url}")
                return items

        except Exception as e:
            logger.warning(f"ProductHunt feed error ({feed_url}): {e}")

    # fallback: اگر هیچ فیدی در دسترس نبود، به صفحه موضوع AI لینک بده
    if not items:
        logger.warning("ProductHunt: all feeds failed, using placeholder")
        items.append(DigestItem(
            title="جستجوی ابزارهای هوش مصنوعی Product Hunt",
            description="برای مشاهده جدیدترین ابزارهای AI روز، به صفحه موضوع هوش مصنوعی مراجعه کنید.",
            url="https://www.producthunt.com/topics/artificial-intelligence",
            source="Product Hunt",
            published_at=utc_now(),
            metadata={"votes": 0},
            is_top_trend=True,
            is_new=True,
        ))

    return items