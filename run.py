"""
اسکریپت اجرای یک‌بار دایجست — مناسب برای Cron Job روی alwaysdata
"""
import logging
from config import Settings, BASE_DIR
from collectors import github, hackernews, huggingface, reddit, producthunt, arxiv
from services.deduplicate import remove_duplicates
from services.formatter import format_digest
from services.logger import configure_logging
from services.ranking import rank
from services.telegram import send_messages
from services.translator import translate_items
from utils.helpers import utc_now


def run():
    settings = Settings.from_environment()
    logger = configure_logging("INFO", BASE_DIR)
    logger.info("Starting daily AI tools and news collection...")

    all_collectors = [
        github.collect,
        huggingface.collect,
        arxiv.collect,
        hackernews.collect,
        reddit.collect,
        producthunt.collect,
    ]

    collected = []
    for c in all_collectors:
        try:
            collected.extend(c(settings, logger))
        except Exception as e:
            logger.error(f"Collector error: {e}")

    if not collected:
        logger.warning("No items collected today.")
        return

    processed = translate_items(
        rank(remove_duplicates(collected)), logger
    )[: settings.max_digest_items]

    if processed:
        messages = format_digest(processed, utc_now())
        send_messages(messages, settings, logger)
        logger.info("AI Tools digest sent successfully.")
    else:
        logger.warning("No items after processing.")


if __name__ == "__main__":
    run()