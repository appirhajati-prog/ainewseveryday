"""
Smart Ranking Service — امتیازدهی هوشمند و انتخاب خبر منتخب روز
"""
import math
from utils.helpers import DigestItem


def rank(items: list[DigestItem]) -> list[DigestItem]:
    for item in items:
        # استخراج فاکتورهای تعامل از metadata
        meta = item.metadata
        stars = float(meta.get("stars", 0))
        forks = float(meta.get("forks", 0))
        downloads = float(meta.get("downloads", 0))
        likes = float(meta.get("likes", 0))
        votes = float(meta.get("votes", 0))
        score = float(meta.get("score", 0))
        comments = float(meta.get("comments", 0))

        # محاسبه امتیاز تعامل (Engagement) — وزن هر متریک متناسب با ارزشش
        engagement = (
            stars * 2.0
            + forks * 1.0
            + downloads * 0.05
            + likes * 1.5
            + votes * 3.0
            + score * 1.5
            + comments * 0.5
        )

        # پاداش‌ها: ترند بودن و جدید بودن
        trend_bonus = 100.0 if item.is_top_trend else 0.0
        new_bonus = 50.0 if item.is_new else 0.0

        item.score = math.log1p(engagement + 1) * 15 + trend_bonus + new_bonus

    # مرتب‌سازی نزولی بر اساس امتیاز
    sorted_items = sorted(items, key=lambda i: i.score, reverse=True)

    # انتخاب دقیقاً یک «خبر منتخب روز» (Star of the Day)
    if sorted_items:
        # ریست ترندهای موقتی که هر کالکتور تنظیم کرده است
        for item in sorted_items:
            item.is_top_trend = False
        # بالاترین امتیاز به عنوان خبر منتخب روز انتخاب می‌شود
        sorted_items[0].is_top_trend = True

    return sorted_items


def _fmt_num(n) -> str:
    try:
        return f"{int(n):,}"
    except (TypeError, ValueError):
        return str(n)


def _build_trend_reason(item: DigestItem) -> str:
    """تولید دلیل ترند شدن بر اساس منبع و داده‌های تعامل واقعی آیتم"""
    meta = item.metadata
    source = (item.source or "").lower()
    url = (item.url or "").lower()

    if "github" in source or "github.com" in url:
        stars = meta.get("stars")
        forks = meta.get("forks")
        if stars:
            reason = (
                f"⭐ {_fmt_num(stars)} ستاره در گیت‌هاب — جزو داغ‌ترین پروژه‌های هفته در "
                f"GitHub Trending؛ توجه ویژه جامعه open-source را جلب کرده است."
            )
            if forks:
                reason += f" با {_fmt_num(forks)} فورک نیز یکی از فعال‌ترین ریپوهاست."
            return reason
        return "📈 ورود به GitHub Trending — رشد ناگهانی توجه جامعه توسعه‌دهندگان."

    if "hacker" in source or "news.ycombinator" in url:
        parts = []
        if meta.get("score"):
            parts.append(f"{_fmt_num(meta['score'])} امتیاز")
        if meta.get("comments"):
            parts.append(f"{_fmt_num(meta['comments'])} کامنت")
        stats = " و ".join(parts) if parts else "تعامل بالا"
        return (
            f"🔥 {stats} — صدر صفحه اول HackerNews؛ یکی از بحث‌برانگیزترین "
            f"موضوعات امروز جامعه تکنولوژی."
        )

    if "arxiv" in source or "arxiv.org" in url:
        if item.is_new:
            return (
                "🆕 مقاله تازه‌منتشرشده در arXiv — در یکی از داغ‌ترین حوزه‌های "
                "تحقیقاتی هوش مصنوعی این روزها."
            )
        return "📄 مقاله‌ای که همچنان در صدر پربازدیدترین مقالات هفته arXiv است."

    if "hugging" in source:
        downloads = meta.get("downloads")
        if downloads:
            return (
                f"📥 {_fmt_num(downloads)} دانلود — یکی از محبوب‌ترین مدل‌های "
                f"جامعه HuggingFace در هفته گذشته."
            )
        return "📥 محبوبیت بالا و استقبال گسترده جامعه HuggingFace."

    if "reddit" in source:
        likes = meta.get("likes")
        if likes:
            return f"❤️ {_fmt_num(likes)} آپ‌ووت — از پربازدیدترین پست‌های هوش مصنوعی Reddit."
        return "❤️ استقبال بالای کاربران Reddit از این پست."

    if "producthunt" in source or "product hunt" in source:
        votes = meta.get("votes")
        if votes:
            return f"👍 {_fmt_num(votes)} رأی — جزو محصولات برتر روز در ProductHunt."
        return "🚀 معرفی‌شده به‌عنوان یکی از محصولات برتر روز در ProductHunt."

    return f"📈 پرتعامل‌ترین آیتم امروز از منبع {item.source}."


def attach_trend_reasons(items: list[DigestItem]) -> None:
    """دلیل ترند شدن هر آیتم را بر اساس داده‌های منبع تولید و ذخیره می‌کند"""
    for item in items:
        item.trend_reason = _build_trend_reason(item)