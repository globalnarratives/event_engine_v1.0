#!/usr/bin/env python3
"""
Main article collection script for Global Narratives System
Run this script via cron job for daily article collection
"""

import sys
import os
from datetime import datetime
import logging

# Add parent directory to path so we can import from collectors
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from collectors.news_api_collector import run_collection as run_news_api
from collectors.rss_collector import run_collection as run_rss

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Run all article collectors"""
    logger.info("="*60)
    logger.info("Starting daily article collection")
    logger.info(f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    logger.info("="*60)
    
    total_articles = 0
    errors = []
    
    # Run News API collector
    try:
        logger.info("\n--- Running News API Collector ---")
        news_api_count = run_news_api()
        total_articles += news_api_count
        logger.info(f"News API: {news_api_count} articles collected")
    except Exception as e:
        error_msg = f"News API collection failed: {e}"
        logger.error(error_msg)
        errors.append(error_msg)
    
    # Run RSS collector
    try:
        logger.info("\n--- Running RSS Collector ---")
        rss_count = run_rss()
        total_articles += rss_count
        logger.info(f"RSS: {rss_count} articles collected")
    except Exception as e:
        error_msg = f"RSS collection failed: {e}"
        logger.error(error_msg)
        errors.append(error_msg)
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("Collection Summary")
    logger.info("="*60)
    logger.info(f"Total articles collected: {total_articles}")
    
    if errors:
        logger.error(f"Errors encountered: {len(errors)}")
        for error in errors:
            logger.error(f"  - {error}")
    else:
        logger.info("No errors")
    
    # Alert if zero articles collected
    if total_articles == 0:
        logger.warning("WARNING: Zero articles collected!")
        logger.warning("Check API keys and RSS feed configurations")
    
    logger.info("Collection complete")
    logger.info("="*60)
    
    return 0 if not errors else 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)