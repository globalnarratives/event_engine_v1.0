import os

class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        # For local development, provide a helpful error
        raise ValueError("DATABASE_URL environment variable is not set!")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # The News API
    NEWS_API_KEY = os.environ.get('NEWS_API_KEY')
    NEWS_API_URL = 'https://api.thenewsapi.com/v1/news/all'
    NEWS_API_LIMIT = 25
    NEWS_API_CATEGORIES = 'general,politics,world,business'
    NEWS_API_LANGUAGE = 'en'
    
    # RSS Feeds
    RSS_FEEDS = os.environ.get('RSS_FEEDS', '').split(',') if os.environ.get('RSS_FEEDS') else []
    
    # Application Settings
    ARTICLES_PER_PAGE = int(os.environ.get('ARTICLES_PER_PAGE', '50'))
    TIMEZONE = os.environ.get('TIMEZONE', 'UTC')
    
    # Region codes
    VALID_REGIONS = ['weu', 'eeu', 'nam', 'sam', 'nea', 'sea', 'sas', 'mea', 'waf', 'eaf', 'caf', 'saf', 'oce', 'cmb']
    
    # Code type and role type options
    CODE_TYPES = ['position', 'actor']
    ROLE_TYPES = ['subject', 'object']

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://localhost/global_narratives_test')

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}