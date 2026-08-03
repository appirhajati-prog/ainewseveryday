from utils.helpers import DigestItem
import re

def _normalize_title(title: str) -> str:
    """عنوان را برای مقایسه نرمال‌سازی می‌کند (حذف علائم و حروف اضافه)"""
    if not title:
        return ""
    # تبدیل به حروف کوچک و حذف کاراکترهای غیرالفبایی
    text = title.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return " ".join(text.split())

def remove_duplicates(items: list[DigestItem]) -> list[DigestItem]:
    seen_urls = set()
    seen_titles = set()
    unique = []
    
    for item in items:
        if not item.url:
            continue
            
        # بررسی URL تکراری
        if item.url in seen_urls:
            continue
            
        # بررسی عنوان تکراری (شباهت بالا یا یکسان)
        norm_title = _normalize_title(item.title)
        if norm_title and norm_title in seen_titles:
            continue
            
        seen_urls.add(item.url)
        if norm_title:
            seen_titles.add(norm_title)
            
        unique.append(item)
        
    return unique
