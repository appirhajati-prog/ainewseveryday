import logging, requests
from config import Settings

def send_messages(messages: list[str], settings: Settings, logger: logging.Logger) -> None:
    for msg in messages:
        try:
            requests.post(
                f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage",
                json={
                    "chat_id": settings.telegram_chat_id, 
                    "text": msg, 
                    "parse_mode": "Markdown", 
                    "disable_web_page_preview": True
                },
                timeout=settings.request_timeout_seconds
            )
        except Exception as e:
            logger.error(f"Telegram error: {e}")
    logger.info("Digest messages successfully sent to Telegram!")
