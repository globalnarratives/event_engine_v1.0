"""
Article collectors for Global Narratives System
"""

from .news_api_collector import NewsAPICollector
from .rss_collector import RSSCollector

__all__ = ['NewsAPICollector', 'RSSCollector']