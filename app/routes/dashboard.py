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
    tracked_actors = []
    for ta in TrackedActor.query.filter_by(user_id=current_user.id).all():
        actor = Actor.query.filter_by(actor_id=ta.actor_id).first()
        if actor:
            tracked_actors.append({
                'code': actor.actor_id,
                'display_name': f"{actor.surname}, {actor.given_name or ''}"
            })

    tracked_institutions = []
    for ti in TrackedInstitution.query.filter_by(user_id=current_user.id).all():
        inst = Institution.query.filter_by(institution_code=ti.institution_code).first()
        if inst:
            tracked_institutions.append({
                'code': inst.institution_code,
                'display_name': inst.institution_name
            })

    tracked_positions = []
    for tp in TrackedPosition.query.filter_by(user_id=current_user.id).all():
        pos = Position.query.filter_by(position_code=tp.position_code).first()
        if pos:
            tracked_positions.append({
                'code': pos.position_code,
                'display_name': pos.position_title
            })

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
