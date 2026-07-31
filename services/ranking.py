import math
from utils.helpers import DigestItem
def rank(items: list[DigestItem]) -> list[DigestItem]:
    for item in items:
        eng = sum(float(v) for k, v in item.metadata.items() if isinstance(v, (int, float)))
        # اخبار ترندتر امتیاز بالاتری می‌گیرند
        trend_bonus = 50.0 if item.is_top_trend else 0.0
        item.score = math.log1p(eng + 1) * 10 + trend_bonus
    return sorted(items, key=lambda i: i.score, reverse=True)
