from newspaper import Article, Config
import logging
import requests
from googlenewsdecoder import new_decoderv1

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
            # 1. Decode Google News URL if it's an RSS/Encoded link
            try:
                decoded_data = new_decoderv1(url, interval=5)
                if decoded_data and decoded_data.get('status') == True:
                    final_url = decoded_data.get('decoded_url')
                    self.logger.info(f"Decoded Google News URL: {final_url}")
                else:
                    final_url = url
            except Exception as e:
                self.logger.warning(f"Decoding failed for {url}: {e}. Using original.")
                final_url = url

            # 2. Try to resolve the final URL link to follow any remaining redirects
            try:
                response = requests.head(final_url, allow_redirects=True, timeout=10, headers={'User-Agent': config.browser_user_agent})
                final_url = response.url
            except Exception as e:
                self.logger.debug(f"HEAD request failed: {e}")

            self.logger.info(f"Scraping final URL: {final_url}")
            
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
