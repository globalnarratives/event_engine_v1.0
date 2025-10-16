from flask import redirect, url_for

# Import blueprints
from . import articles, events, actors, positions, institutions

# Define a default route for the root URL
def register_routes(app):
    """Register all route blueprints and add root redirect"""
    
    @app.route('/')
    def index():
        """Redirect root to articles dashboard"""
        return redirect(url_for('articles.dashboard'))

__all__ = ['articles', 'events', 'actors', 'positions', 'institutions']