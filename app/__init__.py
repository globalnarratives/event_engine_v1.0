from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy  # type: ignore
from flask_migrate import Migrate  # type: ignore
from config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])

    # Add min/max to Jinja2 globals
    app.jinja_env.globals.update(min=min, max=max)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Register blueprints
    from app.routes import articles, events, actors, positions, institutions
    
    app.register_blueprint(articles.bp)
    app.register_blueprint(events.bp)
    app.register_blueprint(actors.bp)
    app.register_blueprint(positions.bp)
    app.register_blueprint(institutions.bp)
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found(error):
        return "Page not found", 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return "Internal server error", 500
    
    @app.route('/')
    def index():
        return redirect(url_for('articles.dashboard'))



    return app