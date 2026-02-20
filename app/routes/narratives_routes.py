from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Narrative, NarrativeScenario, NarrativeResolution, MarkedScenario, ControlFrame, ScenarioEvent
from app import db
from datetime import datetime
from collections import Counter
from app.probability_algorithms import VolatilityCalculator, VelocityCalculator, TimeWindowFilter

bp = Blueprint('narratives', __name__, url_prefix='/narratives')


@bp.route('/')
@login_required
def index():
    """List all narratives"""
    narratives = Narrative.query.order_by(Narrative.narrative_code).all()
    return render_template('narratives/index.html', narratives=narratives)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new narrative with resolution conditions and scenario linkages"""
    marked_scenarios = MarkedScenario.query.order_by(MarkedScenario.id).all()

    if request.method == 'POST':
        narrative_code = request.form.get('narrative_code', '').strip()
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        res_horizon_str = request.form.get('res_horizon', '').strip()
        initial_trend_str = request.form.get('initial_trend', '').strip()

        # Validation
        if not narrative_code or not title or not description or not res_horizon_str or initial_trend_str == '':
            flash('Narrative code, title, description, resolution horizon, and initial trend are required.', 'error')
            return render_template('narratives/create.html', marked_scenarios=marked_scenarios)

        if Narrative.query.filter_by(narrative_code=narrative_code).first():
            flash('A narrative with this code already exists.', 'error')
            return render_template('narratives/create.html', marked_scenarios=marked_scenarios)

        try:
            res_horizon = datetime.strptime(res_horizon_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid resolution horizon format. Use YYYY-MM-DD.', 'error')
            return render_template('narratives/create.html', marked_scenarios=marked_scenarios)

        try:
            initial_trend = int(initial_trend_str)
        except ValueError:
            flash('Invalid initial trend value.', 'error')
            return render_template('narratives/create.html', marked_scenarios=marked_scenarios)

        narrative = Narrative(
            narrative_code=narrative_code,
            title=title,
            description=description,
            res_horizon=res_horizon,
            initial_trend=initial_trend,
        )
        db.session.add(narrative)

        # Resolution conditions
        entity_codes = request.form.getlist('entity_code[]')
        entity_types = request.form.getlist('entity_type[]')
        action_codes = request.form.getlist('action_code[]')
        polarities = request.form.getlist('polarity[]')
        weights = request.form.getlist('weight[]')

        for i, entity_code in enumerate(entity_codes):
            if not entity_code.strip():
                continue
            resolution = NarrativeResolution(
                narrative_code=narrative_code,
                entity_code=entity_code.strip(),
                entity_type=entity_types[i] if i < len(entity_types) else 'actor',
                action_code=action_codes[i].strip() if i < len(action_codes) else '',
                polarity=polarities[i] == 'true' if i < len(polarities) else True,
                weight=float(weights[i]) if i < len(weights) else 1.0,
            )
            db.session.add(resolution)

        # Scenario linkages
        marked_scenario_ids = request.form.getlist('marked_scenario_id[]')
        relationships = request.form.getlist('relationship[]')
        potencies = request.form.getlist('potency[]')

        for i, ms_id in enumerate(marked_scenario_ids):
            if not ms_id.strip():
                continue
            linkage = NarrativeScenario(
                marked_scenario_id=int(ms_id),
                narrative_code=narrative_code,
                relationship=relationships[i] == 'true' if i < len(relationships) else True,
                potency=float(potencies[i]) if i < len(potencies) else 1.0,
            )
            db.session.add(linkage)

        try:
            db.session.commit()
            flash(f'Narrative {narrative_code} created successfully.', 'success')
            return redirect(url_for('narratives.detail', narrative_code=narrative_code))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating narrative: {str(e)}', 'error')

    return render_template('narratives/create.html', marked_scenarios=marked_scenarios)


@bp.route('/<narrative_code>')
@login_required
def detail(narrative_code):
    """View narrative detail with resolution conditions and linked scenarios"""
    narrative = Narrative.query.get_or_404(narrative_code)

    # Build resolution conditions with occurred status
    resolution_data = []
    for resolution in narrative.narrative_resolutions:
        occurred = ControlFrame.query.filter(
            ControlFrame.event_actor.ilike(f'%{resolution.entity_code}%'),
            ControlFrame.action_code == resolution.action_code,
            ControlFrame.rec_timestamp < narrative.res_horizon,
        ).first() is not None
        resolution_data.append({'resolution': resolution, 'occurred': occurred})

    # Split resolution conditions by polarity, ordered by created_at
    resolution_data_positive = sorted(
        [d for d in resolution_data if d['resolution'].polarity],
        key=lambda d: d['resolution'].created_at
    )
    resolution_data_negative = sorted(
        [d for d in resolution_data if not d['resolution'].polarity],
        key=lambda d: d['resolution'].created_at
    )

    # Split linked scenarios by relationship, ordered by created_at
    linkages_direct = sorted(
        [ns for ns in narrative.narrative_scenarios if ns.relationship],
        key=lambda ns: ns.created_at
    )
    linkages_inverse = sorted(
        [ns for ns in narrative.narrative_scenarios if not ns.relationship],
        key=lambda ns: ns.created_at
    )

    # Compute probability metrics for each linked marked scenario
    scenario_metrics = {}
    for ns in narrative.narrative_scenarios:
        ms = ns.marked_scenario
        events = [
            (link.event_code, float(link.weight), link.linked_at)
            for link in ms.event_links
        ]
        filtered = TimeWindowFilter.filter_30day(events)
        if filtered:
            vol_result = VolatilityCalculator.calculate(filtered)
            volatility = vol_result['volatility_score']
            velocity = VelocityCalculator.calculate(volatility, vol_result['event_count'])
        else:
            volatility = None
            velocity = None
        scenario_metrics[ns.marked_scenario_id] = {
            'current_probability': float(ms.current_probability) if ms.current_probability is not None else None,
            'volatility': volatility,
            'velocity': velocity,
        }

    # Compute metadata from events linked through narrative's marked scenarios
    total_event_count = None
    most_common_action = None
    most_common_region = None
    most_common_actor = None

    marked_ids = [ns.marked_scenario_id for ns in narrative.narrative_scenarios]
    if marked_ids:
        event_links = ScenarioEvent.query.filter(
            ScenarioEvent.marked_scenario_id.in_(marked_ids)
        ).all()
        event_codes = [el.event_code for el in event_links]

        if event_codes:
            events = ControlFrame.query.filter(
                ControlFrame.event_code.in_(event_codes)
            ).all()

            total_event_count = len(events)

            action_counter = Counter(
                e.action_code for e in events if e.action_code
            )
            if action_counter:
                most_common_action = action_counter.most_common(1)[0][0]

            region_counter = Counter()
            for e in events:
                parts = e.event_code.split('.')
                if len(parts) >= 3:
                    region_counter[parts[2]] += 1
            if region_counter:
                most_common_region = region_counter.most_common(1)[0][0]

            actor_counter = Counter(
                e.event_actor for e in events if e.event_actor
            )
            if actor_counter:
                most_common_actor = actor_counter.most_common(1)[0][0]

    return render_template(
        'narratives/detail.html',
        narrative=narrative,
        resolution_data_positive=resolution_data_positive,
        resolution_data_negative=resolution_data_negative,
        linkages_direct=linkages_direct,
        linkages_inverse=linkages_inverse,
        scenario_metrics=scenario_metrics,
        total_event_count=total_event_count,
        most_common_action=most_common_action,
        most_common_region=most_common_region,
        most_common_actor=most_common_actor,
    )


@bp.route('/<narrative_code>/edit', methods=['GET', 'POST'])
@login_required
def edit(narrative_code):
    """Edit an existing narrative — update core fields, append new resolution/linkage rows"""
    narrative = Narrative.query.get_or_404(narrative_code)
    all_marked_scenarios = MarkedScenario.query.order_by(MarkedScenario.id).all()
    existing_resolutions = NarrativeResolution.query.filter_by(
        narrative_code=narrative_code
    ).order_by(NarrativeResolution.created_at).all()
    existing_linkages = NarrativeScenario.query.filter_by(
        narrative_code=narrative_code
    ).order_by(NarrativeScenario.created_at).all()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        res_horizon_str = request.form.get('res_horizon', '').strip()
        initial_trend_str = request.form.get('initial_trend', '').strip()

        if not title or not description or not res_horizon_str or initial_trend_str == '':
            flash('Title, description, resolution horizon, and initial trend are required.', 'error')
            return render_template(
                'narratives/edit.html',
                narrative=narrative,
                all_marked_scenarios=all_marked_scenarios,
                existing_resolutions=existing_resolutions,
                existing_linkages=existing_linkages,
            )

        try:
            res_horizon = datetime.strptime(res_horizon_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid resolution horizon format. Use YYYY-MM-DD.', 'error')
            return render_template(
                'narratives/edit.html',
                narrative=narrative,
                all_marked_scenarios=all_marked_scenarios,
                existing_resolutions=existing_resolutions,
                existing_linkages=existing_linkages,
            )

        try:
            initial_trend = int(initial_trend_str)
        except ValueError:
            flash('Invalid initial trend value.', 'error')
            return render_template(
                'narratives/edit.html',
                narrative=narrative,
                all_marked_scenarios=all_marked_scenarios,
                existing_resolutions=existing_resolutions,
                existing_linkages=existing_linkages,
            )

        # Update core fields
        narrative.title = title
        narrative.description = description
        narrative.res_horizon = res_horizon
        narrative.initial_trend = initial_trend

        # Append new resolution condition rows
        entity_codes = request.form.getlist('entity_code[]')
        entity_types = request.form.getlist('entity_type[]')
        action_codes = request.form.getlist('action_code[]')
        polarities = request.form.getlist('polarity[]')
        weights = request.form.getlist('weight[]')

        for i, entity_code in enumerate(entity_codes):
            if not entity_code.strip():
                continue
            resolution = NarrativeResolution(
                narrative_code=narrative_code,
                entity_code=entity_code.strip(),
                entity_type=entity_types[i] if i < len(entity_types) else 'actor',
                action_code=action_codes[i].strip() if i < len(action_codes) else '',
                polarity=polarities[i] == 'true' if i < len(polarities) else True,
                weight=float(weights[i]) if i < len(weights) else 1.0,
            )
            db.session.add(resolution)

        # Append new scenario linkage rows
        marked_scenario_ids = request.form.getlist('marked_scenario_id[]')
        relationships = request.form.getlist('relationship[]')
        potencies = request.form.getlist('potency[]')

        for i, ms_id in enumerate(marked_scenario_ids):
            if not ms_id.strip():
                continue
            linkage = NarrativeScenario(
                marked_scenario_id=int(ms_id),
                narrative_code=narrative_code,
                relationship=relationships[i] == 'true' if i < len(relationships) else True,
                potency=float(potencies[i]) if i < len(potencies) else 1.0,
            )
            db.session.add(linkage)

        try:
            db.session.commit()
            flash(f'Narrative {narrative_code} updated successfully.', 'success')
            return redirect(url_for('narratives.detail', narrative_code=narrative_code))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating narrative: {str(e)}', 'error')

    return render_template(
        'narratives/edit.html',
        narrative=narrative,
        all_marked_scenarios=all_marked_scenarios,
        existing_resolutions=existing_resolutions,
        existing_linkages=existing_linkages,
    )
