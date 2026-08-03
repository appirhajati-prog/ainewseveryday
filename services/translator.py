import logging
from deep_translator import GoogleTranslator
from utils.helpers import DigestItem

def translate_items(items: list[DigestItem], logger: logging.Logger) -> list[DigestItem]:
    try:
        translator = GoogleTranslator(source='auto', target='fa')
    except Exception as e:
        logger.error(f"Failed to initialize translator: {e}")
        return items

    for item in items:
        # ترجمه عنوان
        if item.title:
            try:
                translated_title = translator.translate(item.title)
                if translated_title:
                    item.title = translated_title
            except Exception as e:
                logger.warning(f"Translation warning (title): {e}")

        # ترجمه توضیحات
        if item.description:
            try:
                text = item.description
                if len(text) > 400:
                    # برش هوشمند روی مرز جملات یا فاصله‌ها تا کلمات قطع نشوند
                    chunks = []
                    while len(text) > 400:
                        split_idx = text.rfind(' ', 0, 400)
                        if split_idx == -1:
                            split_idx = 400
                        chunks.append(text[:split_idx])
                        text = text[split_idx:].strip()
                    if text:
                        chunks.append(text)
                    
                    translated_chunks = []
                    for chunk in chunks:
                        t_chunk = translator.translate(chunk)
                        if t_chunk:
                            translated_chunks.append(t_chunk)
                        else:
                            translated_chunks.append(chunk)
                    item.description = " ".join(translated_chunks)
                else:
                    translated_desc = translator.translate(text)
                    if translated_desc:
                        item.description = translated_desc
            except Exception as e:
                logger.warning(f"Translation warning (description): {e}")
                
    return items
