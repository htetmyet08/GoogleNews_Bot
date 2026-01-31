from newspaper import Article, Config
import logging
import requests

class Scraper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def extract_full_article(self, url):
        """
        Downloads and extracts the main text from a news article URL.
        Includes a User-Agent to bypass simple anti-scraping blocks.
        """
        config = Config()
        config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        config.request_timeout = 15

        try:
            # First, try to resolve the URL in case it's a redirect (like Google News RSS)
            # This helps newspaper4k get to the actual content faster
            response = requests.head(url, allow_redirects=True, timeout=10, headers={'User-Agent': config.browser_user_agent})
            final_url = response.url
            
            self.logger.info(f"Resolved final URL: {final_url}")
            
            article = Article(final_url, config=config)
            article.download()
            article.parse()
            
            if not article.text or len(article.text) < 150:
                self.logger.warning(f"Extracted content too short ({len(article.text) if article.text else 0} chars). Site might be blocking scraper.")
                return None
                
            return {
                'text': article.text,
                'top_image': article.top_image,
                'author': article.authors
            }
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {e}")
            return None
