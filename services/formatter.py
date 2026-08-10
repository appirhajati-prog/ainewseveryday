import datetime
from utils.helpers import DigestItem, clean_text

def _escape_markdown_v1(text: str) -> str:
    """کاراکترهای رزرو شده Markdown V1 تلگرام را ایمن می‌کند"""
    if not text:
        return ""
    chars = ['_', '*', '`', '[']
    for char in chars:
        text = text.replace(char, f'\\{char}')
    return text

def format_digest(items: list[DigestItem], generated_at: datetime.datetime) -> list[str]:
    header = (
        f"🤖 *آخرین اخبار و ابزارهای کاربردی هوش مصنوعی*\n"
        f"📅 تاریخ: {generated_at.strftime('%Y-%m-%d')}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
    )
    
    body_parts = []
    for i, item in enumerate(items, 1):
        # بج‌های جذاب بر اساس ویژگی‌های آیتم
        badges = []
        if item.is_top_trend:
            badges.append("🌟 *[خبر منتخب روز (Star of the Day)]*")
        if item.is_new:
            badges.append("� *[جدید و داغ]*")
        
        badge_str = "\n".join(badges) + ("\n" if badges else "")
        
        # استخراج متریک‌های تعامل برای نمایش در خروجی
        meta = item.metadata
        metric_str = ""
        if meta.get("stars"):
            metric_str += f"⭐ {meta['stars']:,} ستاره  "
        if meta.get("forks"):
            metric_str += f"🍴 {meta['forks']:,} فورک  "
        if meta.get("downloads"):
            metric_str += f"📥 {meta['downloads']:,} دانلود  "
        if meta.get("likes"):
            metric_str += f"❤️ {meta['likes']:,} لایک  "
        if meta.get("votes"):
            metric_str += f"👍 {meta['votes']:,} رای  "
        if meta.get("score") and not meta.get("votes") and not meta.get("stars"):
            metric_str += f"🔥 امتیاز: {meta['score']}  "

        safe_title = _escape_markdown_v1(item.title)
        safe_source = _escape_markdown_v1(item.source)
        safe_desc = _escape_markdown_v1(clean_text(item.description))
        
        metrics_line = f"📊 *آمار:* `{metric_str.strip()}`\n" if metric_str.strip() else ""

        part = (
            f"\n*{i}. {safe_title}*\n"
            f"{badge_str}"
            f"🌐 منبع: `{safe_source}`\n"
            f"{metrics_line}"
            f"📝 *بررسی کاربرد و جزئیات:*\n{safe_desc}\n"
            f"🔗 [لینک ابزار و دسترسی مستقیم]({item.url})\n"
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
            current_msg = "🤖 *ادامه معرفی ابزارها و اخبار هوش مصنوعی...*\n" + part
        else:
            current_msg += part
    if current_msg:
        messages.append(current_msg)
        
    return messages