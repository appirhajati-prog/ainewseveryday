import datetime
import re
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
        f"� *آخرین اخبار و ابزارهای کاربردی هوش مصنوعی*\n"
        f"�📅 تاریخ: {generated_at.strftime('%Y-%m-%d')}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
    )
    
    body_parts = []
    for i, item in enumerate(items, 1):
        trend_badge = "🔥 *[ابزار ترند و پرطرفدار روز]*\n" if item.is_top_trend else ""
        safe_title = _escape_markdown_v1(item.title)
        safe_source = _escape_markdown_v1(item.source)
        safe_desc = _escape_markdown_v1(clean_text(item.description))
        part = (
            f"\n*{i}. {safe_title}*\n"
            f"{trend_badge}"
            f"🌐 منبع: `{safe_source}`\n"
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
