import logging, requests
from config import Settings

MAX_MESSAGE_LENGTH = 4096


def _send_text(text: str, settings: Settings, logger: logging.Logger, use_markdown: bool) -> bool:
    """Send a single message. Returns True on success."""
    payload = {
        "chat_id": settings.telegram_chat_id,
        "text": text,
        "disable_web_page_preview": True,
    }
    if use_markdown:
        payload["parse_mode"] = "Markdown"
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage",
            json=payload,
            timeout=settings.request_timeout_seconds,
        )
        if r.status_code == 200:
            try:
                return bool(r.json().get("ok"))
            except ValueError:
                return False
        logger.warning(
            f"Telegram sendMessage failed ({r.status_code}): {r.text[:300]}"
        )
        return False
    except Exception as e:
        logger.error(f"Telegram error: {e}")
        return False


def _send_with_fallback(text: str, settings: Settings, logger: logging.Logger) -> bool:
    """Try Markdown first; if Telegram rejects it, retry as plain text."""
    if _send_text(text, settings, logger, use_markdown=True):
        return True
    logger.warning("Retrying same message without Markdown formatting...")
    return _send_text(text, settings, logger, use_markdown=False)


def send_messages(messages: list[str], settings: Settings, logger: logging.Logger) -> None:
    sent = 0
    failed = 0
    for msg in messages:
        if not msg or not msg.strip():
            continue
        # Split overly long messages into chunks under Telegram's limit
        chunks = [msg[i:i + MAX_MESSAGE_LENGTH]
                  for i in range(0, len(msg), MAX_MESSAGE_LENGTH)] or [msg]
        for chunk in chunks:
            if _send_with_fallback(chunk, settings, logger):
                sent += 1
            else:
                failed += 1
    if failed == 0:
        logger.info(f"Digest messages successfully sent to Telegram! ({sent} messages)")
    else:
        logger.error(
            f"Digest sending finished with errors: {sent} sent, {failed} FAILED"
        )