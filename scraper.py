from newspaper import Article
import logging

class Scraper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def extract_full_article(self, url):
        """
        Downloads and extracts the main text from a news article URL.
        """
        try:
            article = Article(url)
            article.download()
            article.parse()
            
            if not article.text or len(article.text) < 100:
                self.logger.warning(f"Extracted content too short or empty for {url}")
                return None
                
            return {
                'text': article.text,
                'top_image': article.top_image,
                'author': article.authors
            }
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {e}")
            return None
