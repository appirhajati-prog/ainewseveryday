import logging
from deep_translator import GoogleTranslator
from utils.helpers import DigestItem

def translate_items(items: list[DigestItem], logger: logging.Logger) -> list[DigestItem]:
    translator = GoogleTranslator(source='auto', target='fa')
    for item in items:
        try:
            if item.title:
                item.title = translator.translate(item.title)
            if item.description:
                # اگر متن خیلی طولانی بود، آن را تکه تکه ترجمه می‌کنیم تا مترجم گوگل خطا ندهد
                text = item.description
                if len(text) > 400:
                    chunks = [text[i:i+400] for i in range(0, len(text), 400)]
                    translated_chunks = [translator.translate(chunk) for chunk in chunks]
                    item.description = " ".join(translated_chunks)
                else:
                    item.description = translator.translate(text)
        except Exception as e:
            logger.warning(f"Translation warning: {e}")
    return items
