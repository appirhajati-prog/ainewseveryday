import logging, requests
from config import Settings
from utils.helpers import DigestItem, utc_now

def collect(settings: Settings, logger: logging.Logger) -> list[DigestItem]:
    try:
        url = "https://api.github.com/search/repositories"
        params = {"q": "ai tool OR llm agent OR openai OR claude OR AI application", "sort": "stars", "order": "desc", "per_page": 2}
        res = requests.get(url, params=params, timeout=settings.request_timeout_seconds)
        if res.status_code != 200: return []
        items = []
        for i, repo in enumerate(res.json().get("items", [])):
            stars = repo.get("stargazers_count", 0)
            raw_desc = repo.get('description') or 'توضیحی ثبت نشده است'
            
            detailed_desc = (
                f"این ابزار و پروژه متن‌باز به تازگی سر و صدای زیادی در دنیای هوش مصنوعی به پا کرده است.\n\n"
                f"🛠 معرفی و ماهیت ابزار:\n{raw_desc}\n\n"
                f"💡 کاربرد اصلی و اینکه به چه دردی می‌خورد:\n"
                f"این ابزار به توسعه‌دهندگان و کاربران کمک می‌کند تا قابلیت‌های هوش مصنوعی را به پروژه‌های خود اضافه کنند، فرآیندهای تکراری را خودکار سازند و بهره‌وری را به شدت افزایش دهند.\n\n"
                f"🔥 دلیل محبوبیت:\n"
                f"داشتن مستندات قوی، سادگی استفاده و کسب {stars:,} ستاره در گیت‌هاب نشان‌دهنده استقبال بی‌نظیر جامعه برنامه‌نویسان از این ابزار است."
            )
            
            items.append(DigestItem(
                title=f"ابزار گیت‌هاب: {repo.get('full_name')}",
                description=detailed_desc,
                url=repo.get("html_url"),
                source="GitHub Tools",
                published_at=utc_now(),
                metadata={"stars": stars},
                is_top_trend=(i == 0)
            ))
        return items
    except Exception as e:
        logger.error(f"GitHub error: {e}")
        return []
