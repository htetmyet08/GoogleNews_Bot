import os
import time
import logging
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import Database
from news_fetcher import NewsFetcher
from scraper import Scraper
from processor import AIProcessor
from bot import TelegramBot
import asyncio

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def job():
    """
    Main task to be executed every 30 minutes.
    """
    load_dotenv()
    
    # Configuration
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
    tg_channel = os.getenv("TELEGRAM_CHANNEL_ID")
    gcp_project = os.getenv("GOOGLE_CLOUD_PROJECT")
    gcp_location = os.getenv("GOOGLE_CLOUD_LOCATION", "asia-southeast1")
    interval = int(os.getenv("CHECK_INTERVAL_MINUTES", 30))
    max_news = int(os.getenv("MAX_NEWS_ITEMS", 10))

    if not all([tg_token, tg_channel, gcp_project]):
        logger.error("Missing required environment variables. Please check your .env file.")
        return

    # Initialize components
    db = Database()
    fetcher = NewsFetcher(max_results=max_news)
    scraper = Scraper()
    processor = AIProcessor(project_id=gcp_project, location=gcp_location)
    bot = TelegramBot(token=tg_token, channel_id=tg_channel)

    # 1. Fetch news
    logger.info("Fetching world news...")
    news_items = fetcher.fetch_world_news()
    
    # 2. Process items
    new_items_processed = 0
    for item in news_items:
        url_hash = item['url_hash']
        url = item['url']
        title = item['title']

        # Skip if already processed
        if db.is_news_processed(url_hash):
            continue

        logger.info(f"Processing new article: {title}")

        # 3. Scrape full article
        article_data = scraper.extract_full_article(url)
        if not article_data:
            logger.warning(f"Could not extract content for {url}. Skipping.")
            continue

        # 4. Generate Myanmar Summary
        summary = processor.rewrite_to_myanmar(article_data['text'])
        if not summary:
            logger.warning(f"Failed to generate summary for {url}. Skipping.")
            continue

        # 5. Send to Telegram
        success = await bot.send_news(summary, url, title)
        
        if success:
            # 6. Mark as processed
            db.mark_news_as_processed(url_hash, title)
            new_items_processed += 1
            logger.info(f"Successfully posted: {title}")
            # Be nice to APIs
            time.sleep(2) 
        else:
            logger.error(f"Failed to post: {title}")

    logger.info(f"Cycle completed. Processed {new_items_processed} new articles.")

if __name__ == "__main__":
    load_dotenv()
    interval = int(os.getenv("CHECK_INTERVAL_MINUTES", 30))
    
    logger.info("Starting Google News Myanmar Bot...")
    
    # Setup scheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(job, 'interval', minutes=interval)
    
    # Start the first run immediately in the background
    asyncio.get_event_loop().create_task(job())
    
    try:
        scheduler.start()
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
