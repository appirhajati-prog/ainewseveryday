import logging, requests, xml.etree.ElementTree as ET
from config import Settings
from utils.helpers import DigestItem, utc_now

def collect(settings: Settings, logger: logging.Logger) -> list[DigestItem]:
    try:
        url = "http://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=submittedDate&sortOrder=descending&max_results=2"
        res = requests.get(url, timeout=settings.request_timeout_seconds)
        if res.status_code != 200: return []
        
        root = ET.fromstring(res.content)
        namespace = {'atom': 'http://www.w3.org/2005/Atom'}
        items = []
        for i, entry in enumerate(root.findall('atom:entry', namespace)):
            title = entry.find('atom:title', namespace).text.strip().replace('\n', ' ')
            summary = entry.find('atom:summary', namespace).text.strip().replace('\n', ' ')
            link = entry.find('atom:id', namespace).text
            
            detailed_desc = (
                f"این مقاله یکی از تازه‌ترین و پیشرفته‌ترین پژوهش‌های انجام‌شده در حوزه هوش مصنوعی و یادگیری ماشین است که به بررسی زوایای جدیدی از این فناوری می‌پردازد.\n\n"
                f"📖 چکیده تخصصی پژوهش:\n{summary}\n\n"
                f"🔬 اهمیت علمی و کاربرد آینده: این تحقیق چارچوب جدیدی را معرفی می‌کند که می‌تواند به محققان در حل چالش‌های پیچیده الگوریتمی، بهینه‌سازی مدل‌های زبانی و افزایش دقت سیستم‌های خودمختار کمک شایانی کند."
            )
            
            items.append(DigestItem(
                title=f"مقاله آرکسیو: {title}",
                description=detailed_desc,
                url=link,
                source="arXiv",
                published_at=utc_now(),
                metadata={"score": 500},
                is_top_trend=(i == 0)
            ))
        return items
    except Exception as e:
        logger.error(f"arXiv error: {e}")
        return []
