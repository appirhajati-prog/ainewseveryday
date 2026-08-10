"""
GitHub Trending AI Projects Collector
جمع‌آوری پروژه‌های واقعی و داغ هوش مصنوعی از GitHub Trending API
"""
import logging
import re
import requests
from datetime import datetime, timedelta, timezone
from config import Settings
from utils.helpers import DigestItem, utc_now


def _get_headers(settings: Settings):
    """هدرهای مورد نیاز GitHub API با پشتیبانی از توکن"""
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "AINewsEverydayBot/2.0",
    }
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"
    return headers


def _is_recent(created_at_str: str) -> bool:
    """بررسی اینکه پروژه در ۷ روز اخیر ساخته شده باشد"""
    if not created_at_str:
        return False
    try:
        c_date = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - c_date).days <= 7
    except Exception:
        return False


def _parse_trending_html(html: str) -> list[str]:
    """استخراج نام پروژه‌ها از صفحه HTML ترند گیت‌هاب"""
    # الگوی استخراج repo از لینک‌های /owner/repo
    repos = re.findall(r'href="/([^/]+/[^"]+)"', html)
    seen = set()
    result = []
    for r in repos:
        if r not in seen and "/" in r and not r.startswith(("login", "signup", "features", "enterprise", "pricing")):
            seen.add(r)
            result.append(r)
    return result


def _get_trending_repos(logger: logging.Logger, settings: Settings) -> list[str]:
    """دریافت لیست پروژه‌های ترند از صفحه GitHub Trending"""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AINewsBot/2.0"}
        # فقط زبان هوش مصنوعی و ماشین لرنینگ
        for lang in ["python", "jupyter-notebook"]:
            url = f"https://github.com/trending/{lang}?since=daily"
            res = requests.get(url, headers=headers, timeout=settings.request_timeout_seconds)
            if res.status_code == 200:
                repos = _parse_trending_html(res.text)
                if repos:
                    logger.info(f"GitHub Trending ({lang}): {len(repos)} repos found")
                    return repos[:10]
        logger.warning("GitHub Trending: no repos found from HTML")
        return []
    except Exception as e:
        logger.error(f"GitHub Trending HTML error: {e}")
        return []


def collect(settings: Settings, logger: logging.Logger) -> list[DigestItem]:
    items = []
    try:
        # مرحله ۱: دریافت پروژه‌های ترند از صفحه Trending
        trending_names = _get_trending_repos(logger, settings)
        if not trending_names:
            # fallback: استفاده از search API
            return _fallback_search(settings, logger)

        # مرحله ۲: دریافت جزئیات هر پروژه از GitHub API
        api_headers = _get_headers(settings)
        for i, name in enumerate(trending_names[:5]):
            try:
                res = requests.get(
                    f"https://api.github.com/repos/{name}",
                    headers=api_headers,
                    timeout=settings.request_timeout_seconds,
                )
                if res.status_code != 200:
                    continue
                repo = res.json()
                full_name = repo.get("full_name", "")
                stars = repo.get("stargazers_count", 0)
                forks = repo.get("forks_count", 0)
                description = repo.get("description") or "توضیحی ثبت نشده است"
                created = repo.get("created_at", "")[:10]
                html_url = repo.get("html_url", "")
                topics = ", ".join(repo.get("topics", [])[:4]) or "AI"

                items.append(DigestItem(
                    title=full_name,
                    description=f"{description} | موضوعات: {topics}",
                    url=html_url,
                    source="GitHub Trending",
                    published_at=utc_now(),
                    metadata={"stars": stars, "forks": forks, "created": created},
                    is_top_trend=(i == 0),
                    is_new=_is_recent(repo.get("created_at", "")),
                ))
            except Exception as e:
                logger.warning(f"GitHub API detail fetch error for {name}: {e}")

        logger.info(f"GitHub Trending: {len(items)} items collected")

    except Exception as e:
        logger.error(f"GitHub error: {e}")

    return items


def _fallback_search(settings: Settings, logger: logging.Logger) -> list[DigestItem]:
    """جستجوی جایگزین اگر صفحه ترند در دسترس نبود"""
    items = []
    try:
        seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
        query = f"ai OR llm OR agent OR machine-learning created:>{seven_days_ago}"
        params = {"q": query, "sort": "stars", "order": "desc", "per_page": 5}
        res = requests.get(
            "https://api.github.com/search/repositories",
            params=params,
            headers=_get_headers(settings),
            timeout=settings.request_timeout_seconds,
        )
        if res.status_code == 200:
            for i, repo in enumerate(res.json().get("items", [])):
                items.append(DigestItem(
                    title=repo.get("full_name", ""),
                    description=repo.get("description") or "توضیحی ثبت نشده است",
                    url=repo.get("html_url", ""),
                    source="GitHub Search (Fallback)",
                    published_at=utc_now(),
                    metadata={
                        "stars": repo.get("stargazers_count", 0),
                        "forks": repo.get("forks_count", 0),
                    },
                    is_top_trend=(i == 0),
                    is_new=_is_recent(repo.get("created_at", "")),
                ))
    except Exception as e:
        logger.error(f"GitHub fallback error: {e}")
    return items
