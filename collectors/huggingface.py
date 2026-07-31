import logging, requests
from config import Settings
from utils.helpers import DigestItem, utc_now

def collect(settings: Settings, logger: logging.Logger) -> list[DigestItem]:
    items = []
    # ۲ مدل برتر
    try:
        res = requests.get("https://huggingface.co/api/models?sort=downloads&direction=-1&limit=2", timeout=settings.request_timeout_seconds)
        if res.status_code == 200:
            for i, m in enumerate(res.json()):
                downloads = m.get("downloads", 0)
                items.append(DigestItem(
                    title=f"مدل هاگینگ فیس: {m.get('id')}",
                    description=f"این مدل هوش مصنوعی توانسته است توجه توسعه‌دهندگان جهانی را به خود جلب کند.\n📥 میزان دانلود: {downloads:,} مرتبه\n💡 ویژگی شاخص: بهینه‌سازی شده برای اجرای سریع در پروژه‌های مختلف پردازش متن و داده.",
                    url=f"https://huggingface.co/{m.get('id')}",
                    source="Hugging Face Models",
                    published_at=utc_now(),
                    metadata={"downloads": downloads},
                    is_top_trend=(i == 0)
                ))
    except Exception as e:
        logger.error(f"HF Models error: {e}")

    # ۲ اسپیس برتر
    try:
        res = requests.get("https://huggingface.co/api/spaces?sort=likes&direction=-1&limit=2", timeout=settings.request_timeout_seconds)
        if res.status_code == 200:
            for i, s in enumerate(res.json()):
                likes = s.get("likes", 0)
                items.append(DigestItem(
                    title=f"اسپیس هاگینگ فیس: {s.get('id')}",
                    description=f"یک اپلیکیشن و دمو زنده تعاملی مبتنی بر هوش مصنوعی که کاربران می‌توانند خروجی آن را مستقیماً تست کنند.\n❤️ تعداد لایک‌ها: {likes}\n🛠 نوع کاربرد: ابزار کاربردی و خلاقانه آنلاین.",
                    url=f"https://huggingface.co/spaces/{s.get('id')}",
                    source="Hugging Face Spaces",
                    published_at=utc_now(),
                    metadata={"likes": likes},
                    is_top_trend=(i == 0)
                ))
    except Exception as e:
        logger.error(f"HF Spaces error: {e}")

    return items
