import logging
from config import Settings
from utils.helpers import DigestItem, utc_now

def collect(settings: Settings, logger: logging.Logger) -> list[DigestItem]:
    return [
        DigestItem(
            title="پروداکت هانت: ترندترین ابزار هوش مصنوعی اول",
            description="معرفی محصول پیشتاز هوش مصنوعی روز که بیشترین آرا را در پروداکت هانت به دست آورده است.\n⭐ مزیت رقابتی: اتوماسیون پیشرفته و رابط کاربری بسیار ساده برای کاربران حرفه‌ای و مبتدی.",
            url="https://www.producthunt.com/topics/artificial-intelligence",
            source="Product Hunt",
            published_at=utc_now(),
            metadata={"votes": 400},
            is_top_trend=True
        ),
        DigestItem(
            title="پروداکت هانت: محصول نوآورانه دوم هوش مصنوعی",
            description="یکی دیگر از ابزارهای جدید و کاربردی که به تازگی در پروداکت هانت لانچ شده و سر و صدا به پا کرده است.\n⭐ کاربرد اصلی: افزایش بهره‌وری و مدیریت هوشمند وظایف روزمره.",
            url="https://www.producthunt.com/topics/artificial-intelligence",
            source="Product Hunt",
            published_at=utc_now(),
            metadata={"votes": 250},
            is_top_trend=False
        )
    ]
