import datetime
from utils.helpers import DigestItem, clean_text

# منطقه زمانی تهران برای نمایش تاریخ
_TEHRAN_TZ = datetime.timezone(datetime.timedelta(hours=3, minutes=30))
_FA_MONTHS = {
    1: "ژانویه", 2: "فوریه", 3: "مارس", 4: "آوریل", 5: "مه", 6: "ژوئن",
    7: "ژوئیه", 8: "اوت", 9: "سپتامبر", 10: "اکتبر", 11: "نوامبر", 12: "دسامبر",
}
_MEDALS = ["🥇", "🥈", "🥉"]


def _escape_markdown_v1(text: str) -> str:
    """کاراکترهای رزرو شده Markdown V1 تلگرام را ایمن می‌کند"""
    if not text:
        return ""
    for char in ['_', '*', '`', '[']:
        text = text.replace(char, f'\\{char}')
    return text


def _fa_date(dt: datetime.datetime) -> str:
    """تاریخ به وقت تهران با نام ماه فارسی"""
    local = dt.astimezone(_TEHRAN_TZ)
    return f"{local.day} {_FA_MONTHS[local.month]} {local.year}"


def _fmt_num(n) -> str:
    try:
        return f"{int(n):,}"
    except (TypeError, ValueError):
        return str(n)


def _metrics_line(meta: dict) -> str:
    parts = []
    if meta.get("stars"):
        parts.append(f"⭐ {_fmt_num(meta['stars'])} ستاره")
    if meta.get("forks"):
        parts.append(f"🍴 {_fmt_num(meta['forks'])} فورک")
    if meta.get("downloads"):
        parts.append(f"📥 {_fmt_num(meta['downloads'])} دانلود")
    if meta.get("likes"):
        parts.append(f"❤️ {_fmt_num(meta['likes'])} لایک")
    if meta.get("votes"):
        parts.append(f"👍 {_fmt_num(meta['votes'])} رأی")
    if meta.get("score"):
        parts.append(f"🔥 {_fmt_num(meta['score'])} امتیاز")
    if meta.get("comments"):
        parts.append(f"💬 {_fmt_num(meta['comments'])} کامنت")
    return " | ".join(parts)


def format_digest(items: list[DigestItem], generated_at: datetime.datetime) -> list[str]:
    """قالب کارت سه‌بخشی برای هر آیتم: چی هست؟ / چرا ترند شده؟ / آمار + لینک"""
    header = (
        f"🤖 *منتخب هوش مصنوعی — {len(items)} خبر برتر امروز*\n"
        f"📅 {_fa_date(generated_at)}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
    )

    body_parts = []
    for i, item in enumerate(items, 1):
        medal = _MEDALS[i - 1] if i <= len(_MEDALS) else "🔹"
        title = _escape_markdown_v1(item.title)
        desc = _escape_markdown_v1(clean_text(item.description))
        reason = _escape_markdown_v1(item.trend_reason or "📈 جزو پرتقاضاترین‌های امروز.")
        metrics = _metrics_line(item.metadata)
        metrics_block = f"📊 {metrics}\n" if metrics else ""

        part = (
            f"\n{medal} *{i}. {title}*\n\n"
            f"🎯 *چی هست؟*\n{desc}\n\n"
            f"📈 *چرا ترند شده؟*\n{reason}\n"
            f"{metrics_block}"
            f"🔗 {item.url}\n"
            f"───────────────────"
        )
        body_parts.append(part)

    full_message = header + "".join(body_parts)
    if len(full_message) <= 4000:
        return [full_message]

    messages = []
    current_msg = header
    for part in body_parts:
        if len(current_msg) + len(part) > 4000:
            messages.append(current_msg)
            current_msg = "🤖 *ادامه منتخب‌های امروز...*\n" + part
        else:
            current_msg += part
    if current_msg:
        messages.append(current_msg)

    return messages