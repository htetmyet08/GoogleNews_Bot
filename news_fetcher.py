from gnews import GNews
import hashlib

class NewsFetcher:
    def __init__(self, max_results=10):
        self.google_news = GNews(language='en', country='US', period='1h', max_results=max_results)

    def fetch_world_news(self):
        """
        Fetches world news from Google News.
        Returns a list of dictionaries with title, url, and url_hash.
        """
        news_items = self.google_news.get_news_by_topic('WORLD')
        results = []
        for item in news_items:
            url = item.get('url')
            title = item.get('title')
            if url and title:
                url_hash = hashlib.md5(url.encode()).hexdigest()
                results.append({
                    'title': title,
                    'url': url,
                    'url_hash': url_hash,
                    'published_date': item.get('published date')
                })
        return results
