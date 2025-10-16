import requests
from datetime import datetime, timedelta
from app import create_app, db
from app.models import Article
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsAPICollector:
    """Collector for The News API"""
    
    def __init__(self, app):
        self.app = app
        self.api_key = app.config['NEWS_API_KEY']
        self.api_url = app.config['NEWS_API_URL']
        self.limit = app.config['NEWS_API_LIMIT']
        self.categories = app.config['NEWS_API_CATEGORIES']
        self.language = app.config['NEWS_API_LANGUAGE']
    
    def collect(self):
        """Collect articles from The News API"""
        if not self.api_key:
            logger.error("NEWS_API_KEY not configured")
            return 0
        
        logger.info("Starting News API collection...")
        
        # Get articles published in last 24 hours
        yesterday = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S')
        
        params = {
            'api_token': self.api_key,
            'language': self.language,
            'categories': self.categories,
            'limit': self.limit,
            'published_after': yesterday
        }
        
        try:
            response = requests.get(self.api_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('data', [])
            
            logger.info(f"Retrieved {len(articles)} articles from News API")
            
            articles_added = 0
            articles_skipped = 0
            
            with self.app.app_context():
                for article_data in articles:
                    # Check if article already exists (by URL)
                    url = article_data.get('url', '')
                    if not url:
                        continue
                    
                    existing = Article.query.filter_by(url=url).first()
                    if existing:
                        articles_skipped += 1
                        continue
                    
                    # Parse published date
                    published_at = article_data.get('published_at', '')
                    try:
                        if published_at:
                            published_date = datetime.fromisoformat(published_at.replace('Z', '+00:00')).date()
                        else:
                            published_date = datetime.utcnow().date()
                    except:
                        published_date = datetime.utcnow().date()
                    
                    # Create article
                    article = Article(
                        url=url,
                        headline=article_data.get('title', 'No title')[:250],
                        summary=article_data.get('description', 'No summary'),
                        source_name=article_data.get('source', 'Unknown')[:200],
                        published_date=published_date,
                        collected_date=datetime.utcnow(),
                        is_processed=False,
                        is_junk=False
                    )
                    
                    db.session.add(article)
                    articles_added += 1
                
                if articles_added > 0:
                    db.session.commit()
                    logger.info(f"Added {articles_added} new articles")
                
                if articles_skipped > 0:
                    logger.info(f"Skipped {articles_skipped} duplicate articles")
            
            return articles_added
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching from News API: {e}")
            return 0
        except Exception as e:
            logger.error(f"Unexpected error in News API collection: {e}")
            return 0


def run_collection():
    """Run the News API collection"""
    app = create_app('production')
    collector = NewsAPICollector(app)
    articles_added = collector.collect()
    
    if articles_added == 0:
        logger.warning("No articles collected from News API")
    
    return articles_added


if __name__ == '__main__':
    run_collection()