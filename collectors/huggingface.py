"""
HuggingFace Collector — مدل‌ها، اسپیس‌ها و دیتاست‌های واقعی
جمع‌آوری داده‌های زنده از Hugging Face API
"""
import logging
import requests
from datetime import datetime, timedelta, timezone
from config import Settings
from utils.helpers import DigestItem, utc_now


def _is_recent(updated_at: str) -> bool:
    """بررسی اینکه آیتم در ۷ روز اخیر آپدیت یا ساخته شده"""
    if not updated_at:
        return False
    try:
        u_date = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - u_date).days <= 7
    except Exception:
        return False


def _safe_get(url: str, settings: Settings, params: dict):
    """درخواست GET با مدیریت خطا"""
    return requests.get(url, params=params, timeout=settings.request_timeout_seconds)


def collect(settings: Settings, logger: logging.Logger) -> list[DigestItem]:
    items = []

    # --- ۱. مدل‌های ترند (بر اساس دانلود) ---
    try:
        res = _safe_get(
            "https://huggingface.co/api/models",
            settings,
            {"sort": "downloads", "direction": "-1", "limit": 3},
        )
        if res.status_code == 200:
            for i, m in enumerate(res.json()[:3]):
                model_id = m.get("id", "")
                downloads = m.get("downloads", 0)
                likes = m.get("likes", 0)
                tags = ", ".join(m.get("tags", [])[:4]) or "AI"
                items.append(DigestItem(
                    title=model_id,
                    description=(
                        f"مدل هوش مصنوعی با {downloads:,} دانلود و {likes} لایک. "
                        f"موضوع: {tags}"
                    ),
                    url=f"https://huggingface.co/{model_id}",
                    source="HuggingFace Models",
                    published_at=utc_now(),
                    metadata={"downloads": downloads, "likes": likes},
                    is_top_trend=(i == 0),
                    is_new=_is_recent(m.get("lastModified", "")),
                ))
    except Exception as e:
        logger.error(f"HuggingFace models error: {e}")

    # --- ۲. اسپیس‌های ترند (بر اساس لایک) ---
    try:
        res = _safe_get(
            "https://huggingface.co/api/spaces",
            settings,
            {"sort": "likes", "direction": "-1", "limit": 2},
        )
        if res.status_code == 200:
            for i, s in enumerate(res.json()[:2]):
                space_id = s.get("id", "")
                likes = s.get("likes", 0)
                sdk = s.get("sdk", "unknown")
                items.append(DigestItem(
                    title=space_id,
                    description=(
                        f"دموی زنده و تعاملی هوش مصنوعی با {likes:,} لایک. "
                        f"ساخت‌شده با {sdk}"
                    ),
                    url=f"https://huggingface.co/spaces/{space_id}",
                    source="HuggingFace Spaces",
                    published_at=utc_now(),
                    metadata={"likes": likes, "score": likes},
                    is_top_trend=False,
                    is_new=_is_recent(s.get("lastModified", "")),
                ))
    except Exception as e:
        logger.error(f"HuggingFace spaces error: {e}")

    # --- ۳. دیتاست‌های ترند (بر اساس دانلود) ---
    try:
        res = _safe_get(
            "https://huggingface.co/api/datasets",
            settings,
            {"sort": "downloads", "direction": "-1", "limit": 2},
        )
        if res.status_code == 200:
            for i, d in enumerate(res.json()[:2]):
                ds_id = d.get("id", "")
                downloads = d.get("downloads", 0)
                items.append(DigestItem(
                    title=ds_id,
                    description=(
                        f"دیتاست پرکاربرد آموزش مدل با {downloads:,} دانلود. "
                        f"منبع داده‌ای محبوب برای آموزش و فاین‌تیون"
                    ),
                    url=f"https://huggingface.co/datasets/{ds_id}",
                    source="HuggingFace Datasets",
                    published_at=utc_now(),
                    metadata={"downloads": downloads},
                    is_top_trend=False,
                    is_new=_is_recent(d.get("lastModified", "")),
                ))
    except Exception as e:
        logger.error(f"HuggingFace datasets error: {e}")

    return items