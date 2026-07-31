import argparse
import logging
import time
import schedule
from config import Settings, BASE_DIR
from collectors import github, hackernews, huggingface, reddit, producthunt
from services.deduplicate import remove_duplicates
from services.formatter import format_digest
from services.logger import configure_logging
from services.ranking import rank
from services.telegram import send_messages
from services.translator import translate_items
from utils.helpers import utc_now

def run_digest(settings: Settings, logger: logging.Logger) -> None:
    logger.info("Starting daily AI tools and news collection...")
    
    # آرکسیو (مقالات علمی) حذف شد تا فقط ابزار و اخبار ترند بمانند
    collectors = [
        github.collect, 
        huggingface.collect, 
        hackernews.collect, 
        reddit.collect, 
        producthunt.collect
    ]
    
    collected = []
    for c in collectors:
        try:
            collected.extend(c(settings, logger))
        except Exception as e:
            logger.error(f"Collector error: {e}")
            
    if not collected:
        logger.warning("No items collected today.")
        return
        
    processed = translate_items(rank(remove_duplicates(collected)), logger)[:settings.max_digest_items]
    
    if processed:
        messages = format_digest(processed, utc_now())
        send_messages(messages, settings, logger)
        logger.info("AI Tools digest sent successfully.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--daemon", action="store_true", help="Run in background and schedule daily tasks at 12:00")
    args = parser.parse_args()
    
    settings = Settings.from_environment()
    logger = configure_logging("INFO", BASE_DIR)
    
    if not args.daemon:
        run_digest(settings, logger)
        return
        
    logger.info("Bot started in DAEMON mode. Scheduled to run daily at 12:00.")
    schedule.every().day.at("12:00").do(run_digest, settings=settings, logger=logger)
    
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    main()
