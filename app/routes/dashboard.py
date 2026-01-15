from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import ControlFrame, Article
from datetime import datetime, timedelta

bp = Blueprint('dashboard', __name__)

@bp.route('/')
@login_required
def home():
    """Main dashboard after login"""
    
    # Get recent events (last 10)
    recent_events = ControlFrame.query.order_by(
        ControlFrame.rec_timestamp.desc()
    ).limit(10).all()
    
    # Get unprocessed articles count
    unprocessed_articles = Article.query.filter_by(
        is_processed=False, 
        is_junk=False
    ).count()
    
    return render_template('dashboard/home.html',
                         recent_events=recent_events,
                         unprocessed_articles=unprocessed_articles)