from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy  # type: ignore
from flask_migrate import Migrate  # type: ignore
from flask_login import LoginManager  # type: ignore
from config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()  # Add this line

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
    login_manager.init_app(app)  # Add this line
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # User loader callback
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.routes import articles, events, actors, positions, institutions, auth, dashboard, admin, scenarios
    
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(articles.bp)
    app.register_blueprint(events.bp)
    app.register_blueprint(actors.bp)
    app.register_blueprint(positions.bp)
    app.register_blueprint(institutions.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(scenarios.bp)
    
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
        return redirect(url_for('dashboard.home'))

    return app