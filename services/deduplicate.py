from utils.helpers import DigestItem
def remove_duplicates(items: list[DigestItem]) -> list[DigestItem]:
    seen, unique = set(), []
    for item in items:
        if item.url not in seen:
            seen.add(item.url)
            unique.append(item)
    return unique
