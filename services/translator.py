import logging
import re
import requests
from utils.helpers import DigestItem

# حداقل نسبت حروف فارسی برای اینکه متن «از قبل فارسی» در نظر گرفته شود و ترجمه نشود

# موتورهای ترجمه به ترتیب اولویت — اولین موتور موفق استفاده می‌شود
_GOOGLE_HOSTS = [
    "https://translate.googleapis.com/translate_a/single",
    "https://translate.google.com/translate_a/single",
]
_MYMERY_URL = "https://api.mymemory.translated.net/get"

# قطع‌کنندهٔ مدار (Circuit Breaker): اگر موتوری شکست خورد، در همین اجرا دیگر امتحان نشود
_engine_disabled = set()

# MyMemory در هر درخواست حداکثر ~500 کاراکتر می‌پذیرد
_MYMERY_CHUNK = 450


def _is_persian(text: str) -> bool:
    """اگر متن از قبل فارسی است، ترجمه لازم نیست"""
    if not text:
        return False
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return False
    persian = sum(1 for c in letters if "\u0600" <= c <= "\u06FF")
    return persian / len(letters) > 0.4


def _google_translate(text: str, dest: str = "fa", src: str = "en", logger=None):
    """ترجمه با Google Translate (endpointهای gtx) — در صورت شکست None"""
    if "google" in _engine_disabled:
        return None
    params = {"client": "gtx", "sl": src, "tl": dest, "dt": "t", "q": text}
    for host in _GOOGLE_HOSTS:
        try:
            res = requests.get(host, params=params, timeout=8)
            if res.status_code == 200:
                data = res.json()
                translated = "".join(part[0] for part in data[0] if part[0])
                if translated and translated.strip():
                    return translated
            elif logger and res.status_code in (429, 403):
                logger.warning(f"Google Translate {host.split('//')[1]}: {res.status_code}")
        except Exception:
            pass
    _engine_disabled.add("google")  # هر دو هاست شکست خوردند — در این اجرا دیگر امتحان نشود
    return None


def _mymemory_translate(text: str, dest: str = "fa", src: str = "en", logger=None):
    """ترجمه با MyMemory (رایگان، بدون کلید) — متن به قطعات ≤450 کاراکتر تقسیم می‌شود"""
    if "mymemory" in _engine_disabled:
        return None
    try:
        chunks = []
        remaining = text
        while remaining:
            chunks.append(remaining[:_MYMERY_CHUNK])
            remaining = remaining[_MYMERY_CHUNK:]
        out = []
        for ch in chunks:
            res = requests.get(
                _MYMERY_URL,
                params={"q": ch, "langpair": f"{src}|{dest}"},
                timeout=15,
            )
            if res.status_code != 200:
                if logger:
                    logger.warning(f"MyMemory HTTP {res.status_code}")
                _engine_disabled.add("mymemory")
                return None
            data = res.json()
            translated = (data.get("responseData") or {}).get("translatedText", "")
            # اگر سهمیهٔ روزانه تمام شده باشد MyMemory پیام هشدار برمی‌گرداند
            if not translated or "MYMEMORY WARNING" in translated.upper() or "QUOTA" in translated.upper():
                if logger:
                    logger.warning("MyMemory quota exhausted or empty response")
                _engine_disabled.add("mymemory")
                return None
            out.append(translated)
        return "".join(out)
    except Exception as e:
        if logger:
            logger.warning(f"MyMemory error: {e}")
        _engine_disabled.add("mymemory")
        return None


def translate_text(text: str, dest: str = "fa", src: str = "en", logger=None):
    """ترجمه متن با زنجیرهٔ موتورها؛ اگر همه شکست بخورند None برمی‌گرداند"""
    if not text or not text.strip() or _is_persian(text):
        return None
    result = _google_translate(text, dest, src, logger)
    if result:
        return result
    result = _mymemory_translate(text, dest, src, logger)
    if result:
        return result
    return None


def _translate_item(item: DigestItem, logger: logging.Logger) -> bool:
    """ترجمه عنوان و توضیحات؛ True اگر حداقل یکی ترجمه شود"""
    ok = False
    new_title = translate_text(item.title, logger=logger)
    if new_title:
        item.title = new_title
        ok = True
    if item.description:
        new_desc = translate_text(item.description[:600], logger=logger)
        if new_desc:
            item.description = new_desc + ("..." if len(item.description) > 600 else "")
            ok = True
    return ok


def translate_items(items: list[DigestItem], logger: logging.Logger) -> list[DigestItem]:
    """
    ترجمه عنوان و توضیحات آیتم‌ها به فارسی با زنجیرهٔ موتورها:
    Google (2 هاست) → MyMemory. اگر همه شکست بخورند متن اصلی (انگلیسی) حفظ می‌شود
    و در لاگ صریحاً گزارش می‌شود.
    """
    translated_count = 0
    failed = []
    for item in items:
        try:
            if _translate_item(item, logger):
                translated_count += 1
            else:
                failed.append(item.source)
        except Exception as e:
            logger.error(f"Translation failed for {item.title}: {e}")
            failed.append(item.source)
    if failed:
        logger.warning(
            f"Translation: {translated_count}/{len(items)} items translated to Persian; "
            f"UNTRANSLATED (English kept) sources: {failed} "
            f"(disabled engines: {sorted(_engine_disabled) or 'none'})"
        )
    else:
        logger.info(f"Translation complete: {translated_count}/{len(items)} items translated to Persian")
    return items