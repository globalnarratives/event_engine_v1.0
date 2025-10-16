import sys
import os
# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import feedparser
from datetime import datetime, timedelta
from app import create_app, db
from app.models import Article
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RSSCollector:
    """Collector for RSS feeds"""
    
    def __init__(self, app):
        self.app = app
        self.rss_feeds = app.config.get('RSS_FEEDS', [])
        
        # Clean up feeds list - remove empty strings
        if self.rss_feeds:
            self.rss_feeds = [feed.strip() for feed in self.rss_feeds if feed.strip()]
    
    def collect(self):
        """Collect articles from RSS feeds"""
        if not self.rss_feeds:
            logger.info("No RSS feeds configured")
            return 0
        
        logger.info(f"Starting RSS collection from {len(self.rss_feeds)} feeds...")
        
        total_articles_added = 0
        total_articles_skipped = 0
        
        # Get cutoff date (articles from last 24 hours)
        cutoff_date = datetime.utcnow() - timedelta(days=1)
        
        with self.app.app_context():
            for feed_url in self.rss_feeds:
                try:
                    logger.info(f"Fetching feed: {feed_url}")
                    feed = feedparser.parse(feed_url)
                    
                    if feed.bozo:
                        logger.warning(f"Feed has parsing issues: {feed_url}")
                        if hasattr(feed, 'bozo_exception'):
                            logger.warning(f"  Error: {feed.bozo_exception}")
                    
                    if not hasattr(feed, 'entries') or not feed.entries:
                        logger.warning(f"No entries found in feed: {feed_url}")
                        continue
                    
                    articles_added = 0
                    articles_skipped = 0
                    
                    for entry in feed.entries:
                        # Get article URL
                        url = entry.get('link', '')
                        if not url:
                            continue
                        
                        # Check if article already exists
                        existing = Article.query.filter_by(url=url).first()
                        if existing:
                            articles_skipped += 1
                            continue
                        
                        # Parse published date
                        published_date = None
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            try:
                                published_date = datetime(*entry.published_parsed[:6]).date()
                            except:
                                pass
                        
                        if not published_date:
                            published_date = datetime.utcnow().date()
                        
                        # Only collect recent articles (last 24 hours)
                        if datetime.combine(published_date, datetime.min.time()) < cutoff_date:
                            continue
                        
                        # Get article details
                        headline = entry.get('title', 'No title')[:250]
                        summary = entry.get('summary', entry.get('description', 'No summary'))
                        
                        # Get source name from feed title
                        source_name = feed.feed.get('title', 'Unknown RSS Feed')[:200]
                        
                        # Create article
                        article = Article(
                            url=url,
                            headline=headline,
                            summary=summary,
                            source_name=source_name,
                            published_date=published_date,
                            collected_date=datetime.utcnow(),
                            is_processed=False,
                            is_junk=False
                        )
                        
                        db.session.add(article)
                        articles_added += 1
                    
                    if articles_added > 0:
                        db.session.commit()
                        logger.info(f"✓ Added {articles_added} articles from {source_name}")
                        total_articles_added += articles_added
                    
                    if articles_skipped > 0:
                        logger.info(f"  Skipped {articles_skipped} duplicate articles")
                        total_articles_skipped += articles_skipped
                    
                except Exception as e:
                    logger.error(f"✗ Error processing feed {feed_url}: {e}")
                    continue
        
        logger.info(f"\n✓ RSS collection complete: {total_articles_added} added, {total_articles_skipped} skipped")
        return total_articles_added


def run_collection():
    """Run the RSS collection"""
    app = create_app('development')
    collector = RSSCollector(app)
    articles_added = collector.collect()
    
    if articles_added == 0:
        logger.info("No new articles collected from RSS feeds")
    
    return articles_added


if __name__ == '__main__':
    run_collection()