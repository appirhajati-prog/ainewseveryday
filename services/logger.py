import logging
import os

def configure_logging(level: str, base_dir: str) -> logging.Logger:
    logger = logging.getLogger("ai_news_bot")
    logger.setLevel(logging.INFO)
    
    # جلوگیری از تکرار لاگ‌ها
    if logger.handlers:
        return logger

    # فرمت خروجی
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # لاگ در کنسول
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    # لاگ در فایل bot.log
    logs_dir = os.path.join(base_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    fh = logging.FileHandler(os.path.join(logs_dir, "bot.log"), encoding="utf-8")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    
    return logger
