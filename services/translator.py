import logging
import urllib.parse
import requests
from utils.helpers import DigestItem


def _google_translate(text: str, dest: str = "fa", src: str = "en") -> str:
    """ترجمه رایگان با استفاده از Google Translate (بدون وابستگی به پکیج خارجی)"""
    if not text or not text.strip():
        return text
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {"client": "gtx", "sl": src, "tl": dest, "dt": "t", "q": text}
        res = requests.get(url, params=params, timeout=10)
        if res.status_code == 200:
            data = res.json()
            translated = "".join(part[0] for part in data[0] if part[0])
            return translated if translated else text
        return text
    except Exception:
        return text


def _translate_item(item: DigestItem) -> DigestItem:
    """ترجمه عنوان و توضیحات یک آیتم به فارسی"""
    item.title = _google_translate(item.title, dest="fa", src="en")
    if item.description:
        # فقط ۲۰۰ کاراکتر اول توضیحات ترجمه شود تا سرعت بالاتر برود
        desc_short = item.description[:200]
        translated_desc = _google_translate(desc_short, dest="fa", src="en")
        # اگر توضیحات اصلی بیشتر از ۲۰۰ کاراکتر بود، بقیه را اضافه کن
        if len(item.description) > 200:
            item.description = f"{translated_desc}..."
        else:
            item.description = translated_desc
    return item


def translate_items(items: list[DigestItem], logger: logging.Logger) -> list[DigestItem]:
    """
    ترجمه عنوان و توضیحات آیتم‌ها به فارسی با استفاده از Google Translate API رایگان.
    اگر ترجمه ناموفق باشد، متن اصلی حفظ می‌شود.
    """
    translated = []
    for item in items:
        try:
            translated.append(_translate_item(item))
        except Exception as e:
            logger.warning(f"Translation failed for {item.title}: {e}")
            translated.append(item)
    logger.info(f"Translation complete: {len(translated)} items processed")
    return translated