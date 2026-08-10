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