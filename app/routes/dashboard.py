from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import (
    ControlFrame, Article, MarkedScenario,
    TrackedActor, TrackedInstitution, TrackedPosition,
    Actor, Institution, Position
)
from app import db
from app.routes.helpers import compute_marked_metrics

bp = Blueprint('dashboard', __name__)


@bp.route('/')
@login_required
def home():
    """Main dashboard - 3-column command center"""

    # === CENTER COLUMN: Tracked Scenarios ===
    my_marked = MarkedScenario.query.filter_by(
        analyst_id=current_user.id
    ).order_by(MarkedScenario.created_at.desc()).all()

    my_marked_with_metrics = compute_marked_metrics(my_marked)

    # === RIGHT COLUMN: Events Feed (20 most recent) ===
    recent_events = ControlFrame.query.order_by(
        ControlFrame.rec_timestamp.desc()
    ).limit(20).all()

    # Group events by region (extracted from event_code)
    events_by_region = {}
    for event in recent_events:
        parts = event.event_code.split('.') if event.event_code else []
        region = parts[2] if len(parts) > 2 else 'unknown'
        if region not in events_by_region:
            events_by_region[region] = []
        events_by_region[region].append(event)

    # === LEFT COLUMN: Tracked Foundations ===
    # Single JOIN query per entity type instead of one lookup query per tracked item
    actors = db.session.query(Actor).join(
        TrackedActor, Actor.actor_id == TrackedActor.actor_id
    ).filter(TrackedActor.user_id == current_user.id).all()
    tracked_actors = [
        {'code': a.actor_id, 'display_name': f"{a.surname}, {a.given_name or ''}"}
        for a in actors
    ]

    institutions = db.session.query(Institution).join(
        TrackedInstitution, Institution.institution_code == TrackedInstitution.institution_code
    ).filter(TrackedInstitution.user_id == current_user.id).all()
    tracked_institutions = [
        {'code': i.institution_code, 'display_name': i.institution_name}
        for i in institutions
    ]

    positions = db.session.query(Position).join(
        TrackedPosition, Position.position_code == TrackedPosition.position_code
    ).filter(TrackedPosition.user_id == current_user.id).all()
    tracked_positions = [
        {'code': p.position_code, 'display_name': p.position_title}
        for p in positions
    ]

    # Unprocessed articles count (for badge on Input Feed link)
    unprocessed_articles = Article.query.filter_by(
        is_processed=False, is_junk=False
    ).count()

    return render_template('dashboard/home.html',
                           my_marked_with_metrics=my_marked_with_metrics,
                           recent_events=recent_events,
                           events_by_region=events_by_region,
                           tracked_actors=tracked_actors,
                           tracked_institutions=tracked_institutions,
                           tracked_positions=tracked_positions,
                           unprocessed_articles=unprocessed_articles)
