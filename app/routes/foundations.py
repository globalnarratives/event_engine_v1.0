from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.models import db, Actor, Institution, Tenure, Scenario, Position, ControlFrame, ScenarioEvent, TrackedActor, TrackedInstitution, TrackedPosition
from datetime import datetime, timedelta
from app.reference_data import COUNTRY_REGIONS, REGION_NAMES
from math import ceil
from sqlalchemy.orm import joinedload
import statistics
import json

def get_bulk_metrics(entity_codes, cutoff):
    """
    Get bulk metrics for a list of entity codes.
    Returns three dicts: event_counts, most_recent_actions, scenario_counts
    """
    if not entity_codes:
        return {}, {}, {}
    
    # For now, skip bulk event counting due to JSONB complexity
    # Just return empty dicts for event counts
    event_counts = {}
    
    # Bulk most recent actions (using window function)
    most_recent_query = db.session.query(
        ControlFrame.event_actor,
        ControlFrame.action_code,
        db.func.row_number().over(
            partition_by=ControlFrame.event_actor,
            order_by=ControlFrame.rec_timestamp.desc()
        ).label('rn')
    ).filter(
        ControlFrame.event_actor.in_(entity_codes)
    ).subquery()
    
    most_recent_actions = {
        row.event_actor: row.action_code 
        for row in db.session.query(most_recent_query).filter(most_recent_query.c.rn == 1).all()
    }
    
    # Bulk scenario counts (scoped to the supplied codes only)
    scenario_counts_query = db.session.query(
        Scenario.named_actor,
        db.func.count(Scenario.scenario_code).label('scenario_count')
    ).filter(
        Scenario.named_actor.in_(entity_codes)
    ).group_by(Scenario.named_actor)

    scenario_counts = {row.named_actor: row.scenario_count for row in scenario_counts_query.all()}
    
    return event_counts, most_recent_actions, scenario_counts

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
   
    # Calculate 24-hour cutoff (midnight yesterday)
    cutoff = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)

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

        # Group by region (metrics are attached after pagination — only for the visible slice)
        for actor in all_actors:
            country_code = actor.actor_id.split('.')[0]
            region = COUNTRY_REGIONS.get(country_code, 'UNKNOWN')

            # Get current position from preloaded tenures
            current_tenure = next((t for t in actor.tenures if t.tenure_end is None), None)
            current_position = current_tenure.position.position_title if current_tenure and current_tenure.position else None

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
                'event_count_24h': 0,
                'most_recent_action': None,
                'scenario_count': 0
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

        # Fetch metrics for only the visible page slice
        visible_codes = [e['code'] for e in entities if e.get('type') != 'region_header']
        event_counts, most_recent_actions, scenario_counts = get_bulk_metrics(visible_codes, cutoff)
        for e in entities:
            if e.get('type') != 'region_header':
                code = e['code']
                e['event_count_24h'] = event_counts.get(code, 0)
                e['most_recent_action'] = most_recent_actions.get(code)
                e['scenario_count'] = scenario_counts.get(code, 0)

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

        # Group by region (metrics are attached after pagination — only for the visible slice)
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
                'event_count_24h': 0,
                'most_recent_action': None,
                'scenario_count': 0
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

        # Fetch metrics for only the visible page slice
        visible_codes = [e['code'] for e in entities if e.get('type') != 'region_header']
        event_counts, most_recent_actions, scenario_counts = get_bulk_metrics(visible_codes, cutoff)
        for e in entities:
            if e.get('type') != 'region_header':
                code = e['code']
                e['event_count_24h'] = event_counts.get(code, 0)
                e['most_recent_action'] = most_recent_actions.get(code)
                e['scenario_count'] = scenario_counts.get(code, 0)

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

        # Group by region (metrics are attached after pagination — only for the visible slice)
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

            if region not in positions_by_region:
                positions_by_region[region] = []
            positions_by_region[region].append({
                'code': pos.position_code,
                'display_name': pos.position_title,
                'current_holder': current_holder,
                'is_tracked': pos.position_code in tracked_position_codes,
                'metrics': None,
                'country': country_code,
                'event_count_24h': 0,
                'most_recent_action': None,
                'scenario_count': 0
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

        # Fetch metrics for only the visible page slice
        visible_codes = [e['code'] for e in entities if e.get('type') != 'region_header']
        event_counts, most_recent_actions, scenario_counts = get_bulk_metrics(visible_codes, cutoff)
        for e in entities:
            if e.get('type') != 'region_header':
                code = e['code']
                e['event_count_24h'] = event_counts.get(code, 0)
                e['most_recent_action'] = most_recent_actions.get(code)
                e['scenario_count'] = scenario_counts.get(code, 0)
    
    # Query user's tracked positions with metrics
    tracked_positions = []
    user_tracked_positions = TrackedPosition.query.filter_by(user_id=current_user.id).all()

    if user_tracked_positions:
        position_codes_tracked = [tp.position_code for tp in user_tracked_positions]

        # Batch entity lookup — one query instead of one per tracked item
        position_objects = {
            p.position_code: p
            for p in Position.query.filter(
                Position.position_code.in_(position_codes_tracked)
            ).all()
        }

        # Build combined OR filter across all tracked codes
        pos_conditions = []
        for code in position_codes_tracked:
            pos_conditions.append(ControlFrame.identified_subjects.contains([code]))
            pos_conditions.append(ControlFrame.identified_objects.contains([code]))

        # Single events query covering all tracked positions
        raw_pos_events = db.session.query(
            ControlFrame.event_code,
            ControlFrame.identified_subjects,
            ControlFrame.identified_objects
        ).filter(
            ControlFrame.rec_timestamp >= cutoff,
            db.or_(*pos_conditions)
        ).all()

        # Single weights query covering all tracked positions
        pos_weight_rows = db.session.query(
            ControlFrame.event_code,
            ScenarioEvent.weight
        ).join(
            ScenarioEvent, ScenarioEvent.event_code == ControlFrame.event_code
        ).filter(
            ControlFrame.rec_timestamp >= cutoff,
            db.or_(*pos_conditions)
        ).all()

        pos_weights_by_event = {}
        for row in pos_weight_rows:
            pos_weights_by_event.setdefault(row.event_code, []).append(float(row.weight))

        # Classify events per code in Python
        pos_metrics = {
            code: {'total': 0, 'subject': 0, 'object': 0, 'weights': []}
            for code in position_codes_tracked
        }
        for event in raw_pos_events:
            subj = event.identified_subjects or []
            obj = event.identified_objects or []
            event_weights = pos_weights_by_event.get(event.event_code, [])
            for code in position_codes_tracked:
                is_subj = code in subj
                is_obj = code in obj
                if is_subj or is_obj:
                    pos_metrics[code]['total'] += 1
                    if is_subj:
                        pos_metrics[code]['subject'] += 1
                    if is_obj:
                        pos_metrics[code]['object'] += 1
                    pos_metrics[code]['weights'].extend(event_weights)

        for tp in user_tracked_positions:
            position = position_objects.get(tp.position_code)
            if not position:
                continue
            m = pos_metrics.get(tp.position_code, {'total': 0, 'subject': 0, 'object': 0, 'weights': []})
            median_weight = statistics.median(m['weights']) if m['weights'] else None
            tracked_positions.append({
                'code': tp.position_code,
                'display_name': position.position_title,
                'collapsed_metrics': {
                    'total_events_24h': m['total'],
                    'as_subject_24h': m['subject'],
                    'as_object_24h': m['object'],
                    'median_weight': median_weight
                },
                'expanded_details': []
            })

    # Query user's tracked institutions with metrics
    tracked_institutions = []
    user_tracked_institutions = TrackedInstitution.query.filter_by(user_id=current_user.id).all()

    if user_tracked_institutions:
        institution_codes_tracked = [ti.institution_code for ti in user_tracked_institutions]

        # Batch entity lookup — one query instead of one per tracked item
        institution_objects = {
            i.institution_code: i
            for i in Institution.query.filter(
                Institution.institution_code.in_(institution_codes_tracked)
            ).all()
        }

        # Build combined OR filter across all tracked codes
        inst_conditions = []
        for code in institution_codes_tracked:
            inst_conditions.append(ControlFrame.identified_subjects.contains([code]))
            inst_conditions.append(ControlFrame.identified_objects.contains([code]))

        # Single events query covering all tracked institutions
        raw_inst_events = db.session.query(
            ControlFrame.event_code,
            ControlFrame.identified_subjects,
            ControlFrame.identified_objects
        ).filter(
            ControlFrame.rec_timestamp >= cutoff,
            db.or_(*inst_conditions)
        ).all()

        # Single weights query covering all tracked institutions
        inst_weight_rows = db.session.query(
            ControlFrame.event_code,
            ScenarioEvent.weight
        ).join(
            ScenarioEvent, ScenarioEvent.event_code == ControlFrame.event_code
        ).filter(
            ControlFrame.rec_timestamp >= cutoff,
            db.or_(*inst_conditions)
        ).all()

        inst_weights_by_event = {}
        for row in inst_weight_rows:
            inst_weights_by_event.setdefault(row.event_code, []).append(float(row.weight))

        # Classify events per code in Python
        inst_metrics = {
            code: {'total': 0, 'subject': 0, 'object': 0, 'weights': []}
            for code in institution_codes_tracked
        }
        for event in raw_inst_events:
            subj = event.identified_subjects or []
            obj = event.identified_objects or []
            event_weights = inst_weights_by_event.get(event.event_code, [])
            for code in institution_codes_tracked:
                is_subj = code in subj
                is_obj = code in obj
                if is_subj or is_obj:
                    inst_metrics[code]['total'] += 1
                    if is_subj:
                        inst_metrics[code]['subject'] += 1
                    if is_obj:
                        inst_metrics[code]['object'] += 1
                    inst_metrics[code]['weights'].extend(event_weights)

        for ti in user_tracked_institutions:
            institution = institution_objects.get(ti.institution_code)
            if not institution:
                continue
            m = inst_metrics.get(ti.institution_code, {'total': 0, 'subject': 0, 'object': 0, 'weights': []})
            median_weight = statistics.median(m['weights']) if m['weights'] else None
            tracked_institutions.append({
                'code': ti.institution_code,
                'display_name': institution.institution_name,
                'collapsed_metrics': {
                    'total_events_24h': m['total'],
                    'as_subject_24h': m['subject'],
                    'as_object_24h': m['object'],
                    'median_weight': median_weight
                },
                'expanded_details': []
            })

    # Query user's tracked actors with metrics
    tracked_actors = []
    user_tracked_actors = TrackedActor.query.filter_by(user_id=current_user.id).all()

    if user_tracked_actors:
        actor_ids_tracked = [ta.actor_id for ta in user_tracked_actors]

        # Batch entity lookup — one query instead of one per tracked item
        actor_objects = {
            a.actor_id: a
            for a in Actor.query.filter(
                Actor.actor_id.in_(actor_ids_tracked)
            ).all()
        }

        # Build combined OR filter across all tracked codes
        actor_conditions = []
        for code in actor_ids_tracked:
            actor_conditions.append(ControlFrame.identified_subjects.contains([code]))
            actor_conditions.append(ControlFrame.identified_objects.contains([code]))

        # Single events query covering all tracked actors
        raw_actor_events = db.session.query(
            ControlFrame.event_code,
            ControlFrame.identified_subjects,
            ControlFrame.identified_objects
        ).filter(
            ControlFrame.rec_timestamp >= cutoff,
            db.or_(*actor_conditions)
        ).all()

        # Single weights query covering all tracked actors
        actor_weight_rows = db.session.query(
            ControlFrame.event_code,
            ScenarioEvent.weight
        ).join(
            ScenarioEvent, ScenarioEvent.event_code == ControlFrame.event_code
        ).filter(
            ControlFrame.rec_timestamp >= cutoff,
            db.or_(*actor_conditions)
        ).all()

        actor_weights_by_event = {}
        for row in actor_weight_rows:
            actor_weights_by_event.setdefault(row.event_code, []).append(float(row.weight))

        # Classify events per code in Python
        actor_metrics = {
            code: {'total': 0, 'subject': 0, 'object': 0, 'weights': []}
            for code in actor_ids_tracked
        }
        for event in raw_actor_events:
            subj = event.identified_subjects or []
            obj = event.identified_objects or []
            event_weights = actor_weights_by_event.get(event.event_code, [])
            for code in actor_ids_tracked:
                is_subj = code in subj
                is_obj = code in obj
                if is_subj or is_obj:
                    actor_metrics[code]['total'] += 1
                    if is_subj:
                        actor_metrics[code]['subject'] += 1
                    if is_obj:
                        actor_metrics[code]['object'] += 1
                    actor_metrics[code]['weights'].extend(event_weights)

        for ta in user_tracked_actors:
            actor = actor_objects.get(ta.actor_id)
            if not actor:
                continue
            m = actor_metrics.get(ta.actor_id, {'total': 0, 'subject': 0, 'object': 0, 'weights': []})
            median_weight = statistics.median(m['weights']) if m['weights'] else None
            tracked_actors.append({
                'code': ta.actor_id,
                'display_name': actor.surname,
                'collapsed_metrics': {
                    'total_events_24h': m['total'],
                    'as_subject_24h': m['subject'],
                    'as_object_24h': m['object'],
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

def _build_hierarchy_data(position, actor_id):
    """Build org chart hierarchy data: 2 levels up, current position, 2 levels down + peers.

    Returns a nested dict suitable for JSON serialization for the org chart,
    or None if no current position.
    """
    def _position_node(pos, is_current=False):
        """Create a node dict for a position."""
        holder = pos.get_current_holder()
        return {
            'id': pos.position_code,
            'title': pos.position_title,
            'holder': holder.get_display_name() if holder else 'Vacant',
            'position_code': pos.position_code,
            'is_current': is_current,
            'children': []
        }

    def _get_reports_down(pos, depth, current_position_code):
        """Recursively get direct reports down to specified depth.

        When a position has more than 4 direct reports, collapse them into
        a single placeholder node that the frontend renders as a clickable
        "N Direct Reports" card with a modal list.
        """
        if depth <= 0:
            return []
        reports = list(pos.direct_reports)
        if len(reports) > 4:
            # Build full list for the modal
            all_reports = []
            for report in reports:
                holder = report.get_current_holder()
                all_reports.append({
                    'position_code': report.position_code,
                    'title': report.position_title,
                    'holder': holder.get_display_name() if holder else 'Vacant',
                })
            return [{
                'id': pos.position_code + '_placeholder',
                'title': str(len(reports)) + ' Direct Reports',
                'holder': 'Click to view all',
                'position_code': pos.position_code,
                'is_current': False,
                'is_placeholder': True,
                'all_reports': all_reports,
                'children': []
            }]
        nodes = []
        for report in reports:
            is_current = (report.position_code == current_position_code)
            node = _position_node(report, is_current)
            if depth > 1:
                node['children'] = _get_reports_down(report, depth - 1, current_position_code)
            nodes.append(node)
        return nodes

    # Walk up the chain: collect ancestors (up to 2 levels)
    ancestors = []
    current = position
    for _ in range(2):
        parent = current.reports_to
        if parent is None:
            break
        ancestors.append(parent)
        current = parent

    # Build tree from the topmost ancestor down
    # Start from the highest ancestor we found
    if ancestors:
        top = ancestors[-1]  # highest ancestor
        root = _position_node(top)

        # Build the chain downward through ancestors
        parent_node = root
        # Walk ancestors from top to bottom (reverse order, skipping the top which is root)
        # ancestors = [immediate_parent, ..., grandparent]
        # We iterate from second-highest down to immediate parent
        for i in range(len(ancestors) - 2, -1, -1):
            anc = ancestors[i]
            anc_node = _position_node(anc)
            parent_node['children'].append(anc_node)
            parent_node = anc_node

        # Add peers of current position (other direct reports of immediate parent)
        immediate_parent = ancestors[0]
        peers = [s for s in immediate_parent.direct_reports
                 if s.position_code != position.position_code]

        if len(peers) > 4:
            # Collapse peers into a placeholder node
            all_peer_reports = []
            for sibling in peers:
                holder = sibling.get_current_holder()
                all_peer_reports.append({
                    'position_code': sibling.position_code,
                    'title': sibling.position_title,
                    'holder': holder.get_display_name() if holder else 'Vacant',
                })
            parent_node['children'].append({
                'id': immediate_parent.position_code + '_peers_placeholder',
                'title': str(len(peers)) + ' Peers',
                'holder': 'Click to view all',
                'position_code': immediate_parent.position_code,
                'is_current': False,
                'is_placeholder': True,
                'all_reports': all_peer_reports,
                'children': []
            })
        else:
            for sibling in peers:
                peer_node = _position_node(sibling)
                parent_node['children'].append(peer_node)

        # Add current position with its direct reports (2 levels down)
        current_node = _position_node(position, is_current=True)
        current_node['children'] = _get_reports_down(position, 2, position.position_code)
        parent_node['children'].append(current_node)

    else:
        # Current position is at the top (no ancestors found)
        root = _position_node(position, is_current=True)
        root['children'] = _get_reports_down(position, 2, position.position_code)

    return root

def _build_institution_hierarchy_data(institution_code):
    """Build institutional hierarchy data: 2 levels up, current institution, peers, 2 levels down.

    Returns a nested dict suitable for JSON serialization for the org chart,
    or None if institution not found.
    """
    institution = Institution.query.filter_by(institution_code=institution_code).first()
    if not institution:
        return None

    def _institution_node(inst, is_current=False):
        """Create a node dict for an institution."""
        # Get current leader: holder of {institution_code}.exc.01
        leader_name = None
        leader_position_code = f"{inst.institution_code}.exc.01"
        leader_tenure = Tenure.query.filter_by(
            position_code=leader_position_code,
            tenure_end=None
        ).first()
        if leader_tenure and leader_tenure.actor:
            leader_name = leader_tenure.actor.get_display_name()

        return {
            'id': inst.institution_code,
            'name': inst.institution_name,
            'code': inst.institution_code,
            'leader': leader_name or 'No Leader',
            'is_current': is_current,
            'children': []
        }

    def _get_subs_down(inst, depth, current_code):
        """Recursively get sub-institutions down to specified depth."""
        if depth <= 0:
            return []
        subs = list(inst.sub_institutions)
        nodes = []
        for sub in subs:
            is_current = (sub.institution_code == current_code)
            node = _institution_node(sub, is_current)
            if depth > 1:
                node['children'] = _get_subs_down(sub, depth - 1, current_code)
            nodes.append(node)
        return nodes

    # Walk up the chain: collect ancestors (up to 2 levels)
    ancestors = []
    current = institution
    for _ in range(2):
        parent = current.parent_institution
        if parent is None:
            break
        ancestors.append(parent)
        current = parent

    # Build tree from topmost ancestor down
    if ancestors:
        top = ancestors[-1]  # highest ancestor
        root = _institution_node(top)

        # Build chain downward through ancestors
        parent_node = root
        for i in range(len(ancestors) - 2, -1, -1):
            anc = ancestors[i]
            anc_node = _institution_node(anc)
            parent_node['children'].append(anc_node)
            parent_node = anc_node

        # Add peers (other sub-institutions of immediate parent)
        immediate_parent = ancestors[0]
        peers = [s for s in immediate_parent.sub_institutions
                 if s.institution_code != institution.institution_code]
        for sibling in peers:
            peer_node = _institution_node(sibling)
            parent_node['children'].append(peer_node)

        # Add current institution with its sub-institutions (2 levels down)
        current_node = _institution_node(institution, is_current=True)
        current_node['children'] = _get_subs_down(institution, 2, institution.institution_code)
        parent_node['children'].append(current_node)

    else:
        # Current institution is at the top (no ancestors found)
        root = _institution_node(institution, is_current=True)
        root['children'] = _get_subs_down(institution, 2, institution.institution_code)

    return root


@bp.route('/actor/<actor_id>')
@login_required
def actor_detail(actor_id):
    """Display detailed information for a specific actor"""
    # Get actor with preloaded relationships
    actor = Actor.query.filter_by(actor_id=actor_id).options(
        joinedload(Actor.tenures).joinedload(Tenure.position).joinedload(Position.institution)
    ).first_or_404()
    
    # Get all relationships (both directions)
    from app.models import ActorRelationship
    relationships = ActorRelationship.get_all_relationships_for_actor(actor_id)
    
    # Process relationships for display
    family_relationships = []
    professional_relationships = []
    
    for rel in relationships:
        # Determine if we're viewing from primary or related perspective
        if rel.actor_id_primary == actor_id:
            other_actor = rel.related_actor
            label = rel.relationship_label
        else:
            other_actor = rel.primary_actor
            label = rel.get_reciprocal_label()
        
        rel_data = {
            'actor_id': other_actor.actor_id,
            'display_name': other_actor.get_display_name(),
            'label': label,
            'start_date': rel.start_date,
            'end_date': rel.end_date,
            'notes': rel.notes
        }
        
        if rel.relationship_type == 'family':
            family_relationships.append(rel_data)
        else:
            professional_relationships.append(rel_data)
    
    # Get recent events where actor appears
    cutoff = datetime.now() - timedelta(days=30)  # Last 30 days
    
    # Events as event_actor
    events_as_actor = ControlFrame.query.filter(
        ControlFrame.event_actor == actor_id,
        ControlFrame.rec_timestamp >= cutoff
    ).order_by(ControlFrame.rec_timestamp.desc()).limit(20).all()
    
    # Events in subjects (JSONB contains)
    events_as_subject = ControlFrame.query.filter(
        ControlFrame.identified_subjects.contains([actor_id]),
        ControlFrame.rec_timestamp >= cutoff
    ).order_by(ControlFrame.rec_timestamp.desc()).limit(20).all()
    
    # Events in objects (JSONB contains)
    events_as_object = ControlFrame.query.filter(
        ControlFrame.identified_objects.contains([actor_id]),
        ControlFrame.rec_timestamp >= cutoff
    ).order_by(ControlFrame.rec_timestamp.desc()).limit(20).all()
    
    # Get scenarios naming this actor
    named_scenarios = Scenario.query.filter_by(named_actor=actor_id).all()

    # Build org chart hierarchy data for the actor's first current tenure
    hierarchy_data = None
    current_tenures = [t for t in actor.tenures if t.tenure_end is None]
    if current_tenures:
        current_position = current_tenures[0].position
        hierarchy_data = _build_hierarchy_data(current_position, actor_id)
    hierarchy_json = json.dumps(hierarchy_data) if hierarchy_data else 'null'

    return render_template('foundations/actor_detail.html',
                         actor=actor,
                         family_relationships=family_relationships,
                         professional_relationships=professional_relationships,
                         events_as_actor=events_as_actor,
                         events_as_subject=events_as_subject,
                         events_as_object=events_as_object,
                         named_scenarios=named_scenarios,
                         hierarchy_json=hierarchy_json)

@bp.route('/institution/<institution_code>')
@login_required
def institution_detail(institution_code):
    """Display detailed information for a specific institution"""
    institution = Institution.query.filter_by(
        institution_code=institution_code
    ).first_or_404()

    # Get top 2 executive positions
    positions_data = []
    for suffix in ['exc.01', 'exc.02']:
        pos_code = f"{institution_code}.{suffix}"
        position = Position.query.filter_by(position_code=pos_code).first()
        if position:
            current_tenure = Tenure.query.filter_by(
                position_code=pos_code,
                tenure_end=None
            ).first()
            holder = None
            holder_id = None
            if current_tenure and current_tenure.actor:
                holder = current_tenure.actor.get_display_name()
                holder_id = current_tenure.actor.actor_id
            positions_data.append({
                'position_code': pos_code,
                'position_title': position.position_title,
                'holder_name': holder,
                'holder_id': holder_id
            })

    # Query scenarios that mention this institution
    # Scenario model has named_actor but no named_institution field,
    # so search description for institution code or name
    named_scenarios = Scenario.query.filter(
        db.or_(
            Scenario.description.ilike(f'%{institution_code}%'),
            Scenario.description.ilike(f'%{institution.institution_name}%')
        )
    ).all()

    # Query recent events (last 30 days)
    cutoff = datetime.now() - timedelta(days=30)

    # Events as subject (JSONB contains)
    events_as_subject = ControlFrame.query.filter(
        ControlFrame.identified_subjects.contains([institution_code]),
        ControlFrame.rec_timestamp >= cutoff
    ).order_by(ControlFrame.rec_timestamp.desc()).limit(20).all()

    # Events as object (JSONB contains)
    events_as_object = ControlFrame.query.filter(
        ControlFrame.identified_objects.contains([institution_code]),
        ControlFrame.rec_timestamp >= cutoff
    ).order_by(ControlFrame.rec_timestamp.desc()).limit(20).all()

    # Build institution hierarchy
    hierarchy_data = _build_institution_hierarchy_data(institution_code)
    hierarchy_json = json.dumps(hierarchy_data) if hierarchy_data else 'null'

    return render_template('foundations/institution_detail.html',
                         institution=institution,
                         positions_data=positions_data,
                         named_scenarios=named_scenarios,
                         events_as_subject=events_as_subject,
                         events_as_object=events_as_object,
                         hierarchy_json=hierarchy_json)


@bp.route('/position/<position_code>')
@login_required
def position_detail(position_code):
    """Display detailed information for a specific position"""
    # Get position with preloaded relationships
    position = Position.query.filter_by(position_code=position_code).options(
        joinedload(Position.tenures).joinedload(Tenure.actor),
        joinedload(Position.institution)
    ).first_or_404()

    # Get current holder (tenure with no end date)
    current_tenure = next((t for t in position.tenures if t.tenure_end is None), None)
    current_holder = current_tenure.actor if current_tenure else None

    # Get all tenures sorted by start date descending
    all_tenures = sorted(position.tenures, key=lambda t: t.tenure_start, reverse=True)

    # Calculate duration for each tenure
    tenures_data = []
    for tenure in all_tenures:
        end_date = tenure.tenure_end or datetime.now().date()
        duration_days = (end_date - tenure.tenure_start).days
        years = duration_days // 365
        months = (duration_days % 365) // 30
        if years > 0:
            duration_str = f"{years}y {months}m"
        else:
            duration_str = f"{months}m"
        tenures_data.append({
            'tenure': tenure,
            'duration': duration_str,
            'is_current': tenure.tenure_end is None
        })

    # Organizational context
    reports_to_position = position.reports_to
    reports_to_holder = None
    if reports_to_position:
        reports_to_holder = reports_to_position.get_current_holder()

    direct_reports = list(position.direct_reports)
    direct_reports_count = len(direct_reports)

    # Peer positions (same reports_to_position_code)
    peers = []
    if position.reports_to_position_code:
        peers = Position.query.filter(
            Position.reports_to_position_code == position.reports_to_position_code,
            Position.position_code != position_code
        ).all()

    # Query scenarios mentioning this position (search description)
    named_scenarios = Scenario.query.filter(
        db.or_(
            Scenario.description.ilike(f'%{position_code}%'),
            Scenario.description.ilike(f'%{position.position_title}%')
        )
    ).all()

    # Query recent events (last 30 days)
    cutoff = datetime.now() - timedelta(days=30)

    # Events as subject (JSONB contains)
    events_as_subject = ControlFrame.query.filter(
        ControlFrame.identified_subjects.contains([position_code]),
        ControlFrame.rec_timestamp >= cutoff
    ).order_by(ControlFrame.rec_timestamp.desc()).limit(20).all()

    # Events as object (JSONB contains)
    events_as_object = ControlFrame.query.filter(
        ControlFrame.identified_objects.contains([position_code]),
        ControlFrame.rec_timestamp >= cutoff
    ).order_by(ControlFrame.rec_timestamp.desc()).limit(20).all()

    # Build hierarchy data (reuse existing function)
    hierarchy_data = _build_hierarchy_data(position, None)
    hierarchy_json = json.dumps(hierarchy_data) if hierarchy_data else 'null'

    return render_template('foundations/position_detail.html',
                         position=position,
                         current_tenure=current_tenure,
                         current_holder=current_holder,
                         tenures_data=tenures_data,
                         reports_to_position=reports_to_position,
                         reports_to_holder=reports_to_holder,
                         direct_reports_count=direct_reports_count,
                         peers=peers,
                         named_scenarios=named_scenarios,
                         events_as_subject=events_as_subject,
                         events_as_object=events_as_object,
                         hierarchy_json=hierarchy_json)


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

