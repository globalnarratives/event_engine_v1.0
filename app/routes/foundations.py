from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, Actor, Institution, Tenure, Scenario, Position, ControlFrame, ScenarioEvent, TrackedActor, TrackedInstitution, TrackedPosition
from datetime import datetime, timedelta
from app.reference_data import COUNTRY_REGIONS, REGION_NAMES
from math import ceil
from sqlalchemy.orm import joinedload
import statistics

bp = Blueprint('foundations', __name__, url_prefix='/foundations')

@bp.route('/')
@login_required
def index():
    # Get query parameters
    active_tab = request.args.get('tab', 'positions')
    search = request.args.get('search', '')
    expand = request.args.get('expand', '')
    
    # Query entities based on active tab
    entities = []

    actors_by_region = {}
    institutions_by_region = {}
    positions_by_region = {}
   
    if active_tab == 'actors':
        query = Actor.query
        if search:
            query = query.filter(
                db.or_(
                    Actor.actor_id.ilike(f'%{search}%'),
                    Actor.surname.ilike(f'%{search}%'),
                    Actor.given_name.ilike(f'%{search}%')
                )
            )
        all_actors = query.options(
            joinedload(Actor.tenures).joinedload(Tenure.position)
        ).all()

        # Get user's tracked actors
        tracked_actor_ids = [ta.actor_id for ta in TrackedActor.query.filter_by(user_id=current_user.id).all()]
    
        # Calculate 24-hour cutoff
        cutoff = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    
        # Group by region
        for actor in all_actors:
            country_code = actor.actor_id.split('.')[0]
            region = COUNTRY_REGIONS.get(country_code, 'UNKNOWN')

            # Get current position from preloaded tenures
            current_tenure = next((t for t in actor.tenures if t.tenure_end is None), None)
            current_position = current_tenure.position.position_title if current_tenure and current_tenure.position else None
            
            # Count events in last 24h where actor appears
            event_count_24h = db.session.query(db.func.count(ControlFrame.event_code)).filter(
                ControlFrame.rec_timestamp >= cutoff,
                db.or_(
                    ControlFrame.identified_subjects.contains([actor.actor_id]),
                    ControlFrame.identified_objects.contains([actor.actor_id])
                )
            ).scalar() or 0
            
            # Get most recent action (where actor is subject)
            most_recent_event = ControlFrame.query.filter(
                ControlFrame.event_actor == actor.actor_id
            ).order_by(ControlFrame.rec_timestamp.desc()).first()
            
            most_recent_action = None
            if most_recent_event:
                most_recent_action = most_recent_event.action_code
            
            # Count scenarios where actor is named
            scenario_count = Scenario.query.filter_by(named_actor=actor.actor_id).count()
            
            if region not in actors_by_region:
                actors_by_region[region] = []
            actors_by_region[region].append({
                'code': actor.actor_id,
                'display_name': actor.surname,
                'given_name': actor.given_name,
                'current_position': current_position,
                'is_tracked': actor.actor_id in tracked_actor_ids,
                'metrics': None,
                'country': country_code,
                'event_count_24h': event_count_24h,
                'most_recent_action': most_recent_action,
                'scenario_count': scenario_count
            })

        # Sort within regions
        for region in actors_by_region:
            actors_by_region[region].sort(
                key=lambda x: (x['country'], x['display_name'])
            )
        
        # Prepare grouped entities with region info
        grouped_entities = []
        for region in sorted(actors_by_region.keys()):
            grouped_entities.append({
                'type': 'region_header',
                'region_code': region,
                'region_name': REGION_NAMES.get(region, region)
            })
            grouped_entities.extend(actors_by_region[region])
        
        # Pagination
        page = request.args.get('page', 1, type=int)        
        per_page = 25
        total_entities = len(grouped_entities)
        total_pages = ceil(total_entities / per_page) if total_entities > 0 else 1
        
        # Ensure page is within valid range
        page = max(1, min(page, total_pages))
        
        # Slice for current page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        entities = grouped_entities[start_idx:end_idx]  

    elif active_tab == 'institutions':
        query = Institution.query
        if search:
            query = query.filter(
                db.or_(
                    Institution.institution_code.ilike(f'%{search}%'),
                    Institution.institution_name.ilike(f'%{search}%')
                )
            )
        all_institutions = query.all()

        # Get user's tracked institutions
        tracked_institution_codes = [ti.institution_code for ti in TrackedInstitution.query.filter_by(user_id=current_user.id).all()]
        
        # Calculate 24-hour cutoff
        cutoff = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
        
        # Group by region
        for inst in all_institutions:
            country_code = inst.institution_code.split('.')[0]
            region = COUNTRY_REGIONS.get(country_code, 'UNKNOWN')
            
            # Format layer and type info
            layer_info = f"""Layer: {inst.institution_layer.lstrip("'")}""" if inst.institution_layer else None
            
            type_info = None
            if inst.institution_type:
                if inst.institution_subtype:
                    type_info = f"Type: {inst.institution_type} / {inst.institution_subtype}"
                else:
                    type_info = f"Type: {inst.institution_type}"
            
            # Count events in last 24h where institution appears
            event_count_24h = db.session.query(db.func.count(ControlFrame.event_code)).filter(
                ControlFrame.rec_timestamp >= cutoff,
                db.or_(
                    ControlFrame.identified_subjects.contains([inst.institution_code]),
                    ControlFrame.identified_objects.contains([inst.institution_code])
                )
            ).scalar() or 0
            
            # Get most recent action where institution is event_actor
            most_recent_event = ControlFrame.query.filter(
                ControlFrame.event_actor == inst.institution_code
            ).order_by(ControlFrame.rec_timestamp.desc()).first()
            
            most_recent_action = None
            if most_recent_event:
                most_recent_action = most_recent_event.action_code
            
            # Count scenarios where institution is named_actor
            scenario_count = Scenario.query.filter_by(named_actor=inst.institution_code).count()
            
            if region not in institutions_by_region:
                institutions_by_region[region] = []
            institutions_by_region[region].append({
                'code': inst.institution_code,
                'display_name': inst.institution_name,
                'layer_info': layer_info,
                'type_info': type_info,
                'is_tracked': inst.institution_code in tracked_institution_codes,
                'metrics': None,
                'country': country_code,
                'event_count_24h': event_count_24h,
                'most_recent_action': most_recent_action,
                'scenario_count': scenario_count
            })

        # Sort within regions
        for region in institutions_by_region:
            institutions_by_region[region].sort(
                key=lambda x: (x['country'], x['display_name'])
            )
        
        # Prepare grouped entities with region info
        grouped_entities = []
        for region in sorted(institutions_by_region.keys()):
            grouped_entities.append({
                'type': 'region_header',
                'region_code': region,
                'region_name': REGION_NAMES.get(region, region)
            })
            grouped_entities.extend(institutions_by_region[region])
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = 25
        total_entities = len(grouped_entities)
        total_pages = ceil(total_entities / per_page) if total_entities > 0 else 1
        
        # Ensure page is within valid range
        page = max(1, min(page, total_pages))
        
        # Slice for current page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        entities = grouped_entities[start_idx:end_idx]
            
    else:  # positions (default)
        query = Position.query
        if search:
            query = query.filter(
                db.or_(
                    Position.position_code.ilike(f'%{search}%'),
                    Position.position_title.ilike(f'%{search}%')
                )
            )
        all_positions = query.options(
            joinedload(Position.tenures).joinedload(Tenure.actor)
        ).all()
                
            # Get user's tracked positions
        tracked_position_codes = [tp.position_code for tp in TrackedPosition.query.filter_by(user_id=current_user.id).all()]
        
        # Calculate 24-hour cutoff
        cutoff = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
        
        # Group by region
        for pos in all_positions:
            country_code = pos.position_code.split('.')[0]
            region = COUNTRY_REGIONS.get(country_code, 'UNKNOWN')
            
            # Get current holder from preloaded tenures
            current_tenure = next((t for t in pos.tenures if t.tenure_end is None), None)
            if current_tenure and current_tenure.actor:
                actor = current_tenure.actor
                current_holder = f"{actor.surname}, {actor.given_name}" if actor.given_name else actor.surname
            else:
                current_holder = None
            
            # Count events in last 24h where position appears
            event_count_24h = db.session.query(db.func.count(ControlFrame.event_code)).filter(
                ControlFrame.rec_timestamp >= cutoff,
                db.or_(
                    ControlFrame.identified_subjects.contains([pos.position_code]),
                    ControlFrame.identified_objects.contains([pos.position_code])
                )
            ).scalar() or 0
            
            # Get most recent action where position is event_actor (position acting)
            most_recent_event = ControlFrame.query.filter(
                ControlFrame.event_actor == pos.position_code
            ).order_by(ControlFrame.rec_timestamp.desc()).first()
            
            most_recent_action = None
            if most_recent_event:
                most_recent_action = most_recent_event.action_code
            
            # Count scenarios where position is named_actor
            scenario_count = Scenario.query.filter_by(named_actor=pos.position_code).count()
            
            if region not in positions_by_region:
                positions_by_region[region] = []
            positions_by_region[region].append({
                'code': pos.position_code,
                'display_name': pos.position_title,
                'current_holder': current_holder,
                'is_tracked': pos.position_code in tracked_position_codes,
                'metrics': None,
                'country': country_code,
                'event_count_24h': event_count_24h,
                'most_recent_action': most_recent_action,
                'scenario_count': scenario_count
            })

        # Sort within regions
        for region in positions_by_region:
            positions_by_region[region].sort(
                key=lambda x: (x['country'], x['display_name'])
            )
        
        # Prepare grouped entities with region info
        grouped_entities = []
        for region in sorted(positions_by_region.keys()):
            grouped_entities.append({
                'type': 'region_header',
                'region_code': region,
                'region_name': REGION_NAMES.get(region, region)
            })
            grouped_entities.extend(positions_by_region[region])
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = 25
        total_entities = len(grouped_entities)
        total_pages = ceil(total_entities / per_page) if total_entities > 0 else 1
        
        # Ensure page is within valid range
        page = max(1, min(page, total_pages))
        
        # Slice for current page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        entities = grouped_entities[start_idx:end_idx]


   # Calculate 24-hour cutoff (midnight yesterday)
    cutoff = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    
    # Query user's tracked positions with metrics
    tracked_positions = []
    user_tracked_positions = TrackedPosition.query.filter_by(user_id=current_user.id).all()
    
    for tp in user_tracked_positions:
        position = Position.query.filter_by(position_code=tp.position_code).first()
        if not position:
            continue
            
        # Count total events in last 24h involving this position
        total_events = db.session.query(db.func.count(ControlFrame.event_code)).filter(
            ControlFrame.rec_timestamp >= cutoff,
            db.or_(
                ControlFrame.identified_subjects.contains([tp.position_code]),
                ControlFrame.identified_objects.contains([tp.position_code])
            )
        ).scalar() or 0
        
        # Count events as subject
        as_subject = db.session.query(db.func.count(ControlFrame.event_code)).filter(
            ControlFrame.rec_timestamp >= cutoff,
            ControlFrame.identified_subjects.contains([tp.position_code])
        ).scalar() or 0
        
        # Count events as object
        as_object = db.session.query(db.func.count(ControlFrame.event_code)).filter(
            ControlFrame.rec_timestamp >= cutoff,
            ControlFrame.identified_objects.contains([tp.position_code])
        ).scalar() or 0
        
        # Get weights for median calculation
        weights = db.session.query(ScenarioEvent.weight).join(
            ControlFrame, ScenarioEvent.event_code == ControlFrame.event_code
        ).filter(
            ControlFrame.rec_timestamp >= cutoff,
            db.or_(
                ControlFrame.identified_subjects.contains([tp.position_code]),
                ControlFrame.identified_objects.contains([tp.position_code])
            )
        ).all()
        
        median_weight = None
        if weights:
            median_weight = statistics.median([w[0] for w in weights])
        
        tracked_positions.append({
            'code': tp.position_code,
            'display_name': position.position_title,
            'collapsed_metrics': {
                'total_events_24h': total_events,
                'as_subject_24h': as_subject,
                'as_object_24h': as_object,
                'median_weight': median_weight
            },
            'expanded_details': []
        })

        # Query user's tracked institutions with metrics
    tracked_institutions = []
    user_tracked_institutions = TrackedInstitution.query.filter_by(user_id=current_user.id).all()
    
    for ti in user_tracked_institutions:
        institution = Institution.query.filter_by(institution_code=ti.institution_code).first()
        if not institution:
            continue
            
        # Count total events in last 24h involving this institution
        total_events = db.session.query(db.func.count(ControlFrame.event_code)).filter(
            ControlFrame.rec_timestamp >= cutoff,
            db.or_(
                ControlFrame.identified_subjects.contains([ti.institution_code]),
                ControlFrame.identified_objects.contains([ti.institution_code])
            )
        ).scalar() or 0
        
        # Count events as subject
        as_subject = db.session.query(db.func.count(ControlFrame.event_code)).filter(
            ControlFrame.rec_timestamp >= cutoff,
            ControlFrame.identified_subjects.contains([ti.institution_code])
        ).scalar() or 0
        
        # Count events as object
        as_object = db.session.query(db.func.count(ControlFrame.event_code)).filter(
            ControlFrame.rec_timestamp >= cutoff,
            ControlFrame.identified_objects.contains([ti.institution_code])
        ).scalar() or 0
        
        # Get weights for median calculation
        weights = db.session.query(ScenarioEvent.weight).join(
            ControlFrame, ScenarioEvent.event_code == ControlFrame.event_code
        ).filter(
            ControlFrame.rec_timestamp >= cutoff,
            db.or_(
                ControlFrame.identified_subjects.contains([ti.institution_code]),
                ControlFrame.identified_objects.contains([ti.institution_code])
            )
        ).all()
        
        median_weight = None
        if weights:
            median_weight = statistics.median([w[0] for w in weights])
        
        tracked_institutions.append({
            'code': ti.institution_code,
            'display_name': institution.institution_name,
            'collapsed_metrics': {
                'total_events_24h': total_events,
                'as_subject_24h': as_subject,
                'as_object_24h': as_object,
                'median_weight': median_weight
            },
            'expanded_details': []
        })

# Query user's tracked actors with metrics
    tracked_actors = []
    user_tracked_actors = TrackedActor.query.filter_by(user_id=current_user.id).all()
    
    for ta in user_tracked_actors:
        actor = Actor.query.filter_by(actor_id=ta.actor_id).first()
        if not actor:
            continue
            
        # Count total events in last 24h involving this actor
        total_events = db.session.query(db.func.count(ControlFrame.event_code)).filter(
            ControlFrame.rec_timestamp >= cutoff,
            db.or_(
                ControlFrame.identified_subjects.contains([ta.actor_id]),
                ControlFrame.identified_objects.contains([ta.actor_id])
            )
        ).scalar() or 0
        
        # Count events as subject
        as_subject = db.session.query(db.func.count(ControlFrame.event_code)).filter(
            ControlFrame.rec_timestamp >= cutoff,
            ControlFrame.identified_subjects.contains([ta.actor_id])
        ).scalar() or 0
        
        # Count events as object
        as_object = db.session.query(db.func.count(ControlFrame.event_code)).filter(
            ControlFrame.rec_timestamp >= cutoff,
            ControlFrame.identified_objects.contains([ta.actor_id])
        ).scalar() or 0
        
        # Get weights for median calculation
        weights = db.session.query(ScenarioEvent.weight).join(
            ControlFrame, ScenarioEvent.event_code == ControlFrame.event_code
        ).filter(
            ControlFrame.rec_timestamp >= cutoff,
            db.or_(
                ControlFrame.identified_subjects.contains([ta.actor_id]),
                ControlFrame.identified_objects.contains([ta.actor_id])
            )
        ).all()
        
        median_weight = None
        if weights:
            median_weight = statistics.median([w[0] for w in weights])
        
        tracked_actors.append({
            'code': ta.actor_id,
            'display_name': actor.surname,
            'collapsed_metrics': {
                'total_events_24h': total_events,
                'as_subject_24h': as_subject,
                'as_object_24h': as_object,
                'median_weight': median_weight
            },
            'expanded_details': []
        })

    return render_template('foundations/index.html',
                         active_tab=active_tab,
                         entities=entities,
                         tracked_actors=tracked_actors,
                         tracked_positions=tracked_positions,
                         tracked_institutions=tracked_institutions,
                         page=page,
                         total_pages=total_pages,
                         total_entities=total_entities)

@bp.route('/toggle_track/<entity_type>/<entity_code>', methods=['POST'])
@login_required
def toggle_track(entity_type, entity_code):
    try:
        if entity_type == 'actor':
            # Check if already tracked
            existing = TrackedActor.query.filter_by(
                user_id=current_user.id,
                actor_id=entity_code
            ).first()
            
            if existing:
                db.session.delete(existing)
                db.session.commit()
                flash(f'Stopped tracking {entity_code}', 'success')
            else:
                # Verify actor exists
                actor = Actor.query.filter_by(actor_id=entity_code).first()
                if not actor:
                    flash(f'Actor {entity_code} not found', 'error')
                    return redirect(url_for('foundations.index', tab='actors'))
                
                new_track = TrackedActor(user_id=current_user.id, actor_id=entity_code)
                db.session.add(new_track)
                db.session.commit()
                flash(f'Now tracking {entity_code}', 'success')
            
            return redirect(url_for('foundations.index', tab='actors'))
        
        elif entity_type == 'position':
            existing = TrackedPosition.query.filter_by(
                user_id=current_user.id,
                position_code=entity_code
            ).first()
            
            if existing:
                db.session.delete(existing)
                db.session.commit()
                flash(f'Stopped tracking {entity_code}', 'success')
            else:
                position = Position.query.filter_by(position_code=entity_code).first()
                if not position:
                    flash(f'Position {entity_code} not found', 'error')
                    return redirect(url_for('foundations.index', tab='positions'))
                
                new_track = TrackedPosition(user_id=current_user.id, position_code=entity_code)
                db.session.add(new_track)
                db.session.commit()
                flash(f'Now tracking {entity_code}', 'success')
            
            return redirect(url_for('foundations.index', tab='positions'))
        
        elif entity_type == 'institution':
            existing = TrackedInstitution.query.filter_by(
                user_id=current_user.id,
                institution_code=entity_code
            ).first()
            
            if existing:
                db.session.delete(existing)
                db.session.commit()
                flash(f'Stopped tracking {entity_code}', 'success')
            else:
                institution = Institution.query.filter_by(institution_code=entity_code).first()
                if not institution:
                    flash(f'Institution {entity_code} not found', 'error')
                    return redirect(url_for('foundations.index', tab='institutions'))
                
                new_track = TrackedInstitution(user_id=current_user.id, institution_code=entity_code)
                db.session.add(new_track)
                db.session.commit()
                flash(f'Now tracking {entity_code}', 'success')
            
            return redirect(url_for('foundations.index', tab='institutions'))
        
        else:
            flash(f'Invalid entity type: {entity_type}', 'error')
            return redirect(url_for('foundations.index'))
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error tracking entity: {str(e)}', 'error')
        return redirect(url_for('foundations.index'))

