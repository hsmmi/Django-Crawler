from celery import shared_task
from utils.logging import logger


@shared_task(name="scrape_products")
def scrape_products():
    from .esmerdis_scraper.spiders.products import ProductSpider
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    """Celery task to run the product scraper."""
    logger.info("🚀 Starting product scraping task...")

    try:
        process = CrawlerProcess(get_project_settings())
        process.crawl(ProductSpider)
        process.start()
        logger.info("✅ Scraping completed successfully!")
    except Exception as e:
        logger.error(f"❌ Error in scraping task: {e}", exc_info=True)
        return f"Scraping failed: {e}"

    return "Scraping completed!"
