from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Scenario, MarkedScenario, ScenarioEvent, User
from app import db
from datetime import datetime

bp = Blueprint('scenarios', __name__, url_prefix='/scenarios')

@bp.route('/')
@login_required
def index():
    """List all scenarios"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    scenarios = Scenario.query.order_by(Scenario.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('scenarios/index.html', scenarios=scenarios)

# Update the create() function in app/routes/scenarios.py

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new scenario (proposition)"""
    if request.method == 'POST':
        scenario_code = request.form.get('scenario_code')
        title = request.form.get('title')
        description = request.form.get('description')
        start_date_str = request.form.get('start_date')  # NEW
        close_date_str = request.form.get('close_date')
        
        # Validation
        if not scenario_code or not title or not start_date_str or not close_date_str:
            flash('Scenario code, title, start date, and close date are required.', 'error')
            return render_template('scenarios/create.html')
        
        # Check if scenario code already exists
        if Scenario.query.filter_by(scenario_code=scenario_code).first():
            flash('A scenario with this code already exists.', 'error')
            return render_template('scenarios/create.html')
        
        # Parse dates
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            close_date = datetime.strptime(close_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Use YYYY-MM-DD.', 'error')
            return render_template('scenarios/create.html')
        
        # Validate date logic
        if close_date <= start_date:
            flash('Resolution date must be after start date.', 'error')
            return render_template('scenarios/create.html')
        
        # Create scenario
        scenario = Scenario(
            scenario_code=scenario_code,
            title=title,
            description=description,
            start_date=start_date,  # NEW
            close_date=close_date,
            created_by_id=current_user.id
        )
        
        db.session.add(scenario)
        
        try:
            db.session.commit()
            flash(f'Scenario {scenario_code} created successfully!', 'success')
            return redirect(url_for('scenarios.detail', scenario_id=scenario.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating scenario: {str(e)}', 'error')
    
    return render_template('scenarios/create.html')

@bp.route('/<int:scenario_id>')
@login_required
def detail(scenario_id):
    """View scenario detail with all marked scenarios"""
    scenario = Scenario.query.get_or_404(scenario_id)
    
    # Get all marked scenarios for this scenario
    marked_scenarios = MarkedScenario.query.filter_by(
        scenario_id=scenario_id
    ).order_by(MarkedScenario.created_at.desc()).all()
    
    return render_template('scenarios/detail.html', 
                         scenario=scenario,
                         marked_scenarios=marked_scenarios)

@bp.route('/<int:scenario_id>/mark', methods=['GET', 'POST'])
@login_required
def create_marked(scenario_id):
    """Create analyst's assessment (marked scenario)"""
    scenario = Scenario.query.get_or_404(scenario_id)
    
    if request.method == 'POST':
        title = request.form.get('title')  # Optional custom label
        description = request.form.get('description')
        initial_probability_str = request.form.get('initial_probability')
        
        # Validation
        if not initial_probability_str:
            flash('Initial probability is required.', 'error')
            return render_template('scenarios/create_marked.html', scenario=scenario)
        
        try:
            initial_probability = float(initial_probability_str)
            if not (0 <= initial_probability <= 1):
                flash('Probability must be between 0 and 1.', 'error')
                return render_template('scenarios/create_marked.html', scenario=scenario)
        except ValueError:
            flash('Invalid probability value.', 'error')
            return render_template('scenarios/create_marked.html', scenario=scenario)
        
        # Create marked scenario
        marked = MarkedScenario(
            scenario_id=scenario_id,
            analyst_id=current_user.id,
            title=title if title else None,
            description=description,
            initial_probability=initial_probability,
            current_probability=initial_probability,
            probability_history=[{
                'probability': float(initial_probability),
                'timestamp': datetime.utcnow().isoformat(),
                'reason': 'Initial assessment',
                'event_code': None,
                'user_id': current_user.id
            }]
        )
        
        db.session.add(marked)
        
        try:
            db.session.commit()
            flash(f'Assessment created: {marked.display_name}', 'success')
            return redirect(url_for('scenarios.marked_detail', marked_id=marked.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating assessment: {str(e)}', 'error')
    
    return render_template('scenarios/create_marked.html', scenario=scenario)

@bp.route('/marked/<int:marked_id>')
@login_required
def marked_detail(marked_id):
    """View marked scenario detail with linked events and probability history"""
    marked = MarkedScenario.query.get_or_404(marked_id)
    
    # Get linked events
    event_links = ScenarioEvent.query.filter_by(
        marked_scenario_id=marked_id
    ).order_by(ScenarioEvent.linked_at.desc()).all()
    
    # Get all events for sidebar listing
    from app.models import ControlFrame
    all_events = ControlFrame.query.order_by(ControlFrame.rec_timestamp.desc()).limit(100).all()
    
    # Get list of already-linked event codes to filter out
    linked_event_codes = [link.event_code for link in event_links]
    
    return render_template('scenarios/marked_detail.html',
                         marked=marked,
                         event_links=event_links,
                         all_events=all_events,
                         linked_event_codes=linked_event_codes)

@bp.route('/marked/<int:marked_id>/link-event', methods=['GET', 'POST'])
@login_required
def link_event(marked_id):
    """Link an event to a marked scenario with weight"""
    marked = MarkedScenario.query.get_or_404(marked_id)
    
    # Check if user owns this marked scenario
    if marked.analyst_id != current_user.id:
        flash('You can only link events to your own assessments.', 'error')
        return redirect(url_for('scenarios.marked_detail', marked_id=marked_id))
    
    if request.method == 'POST':
        event_code = request.form.get('event_code')
        weight_str = request.form.get('weight')
        notes = request.form.get('notes')
        
        # Validation
        if not event_code or not weight_str:
            flash('Event code and weight are required.', 'error')
            return render_template('scenarios/link_event.html', marked=marked)
        
        # Check if event exists
        from app.models import ControlFrame
        event = ControlFrame.query.filter_by(event_code=event_code).first()
        if not event:
            flash(f'Event {event_code} not found.', 'error')
            return render_template('scenarios/link_event.html', marked=marked)
        
        # Check if already linked
        existing = ScenarioEvent.query.filter_by(
            marked_scenario_id=marked_id,
            event_code=event_code
        ).first()
        if existing:
            flash(f'Event {event_code} is already linked to this assessment.', 'error')
            return render_template('scenarios/link_event.html', marked=marked)
        
        try:
            weight = float(weight_str)
            
            # Validate weight range and increment
            if weight == 0:
                flash('Weight cannot be zero. Please use a value between -12.0 and +12.0.', 'error')
                return render_template('scenarios/link_event.html', marked=marked, available_events=[])
            
            if not (-12.0 <= weight <= 12.0):
                flash('Weight must be between -12.0 and +12.0.', 'error')
                return render_template('scenarios/link_event.html', marked=marked, available_events=[])
            
            # Check if weight is in valid 0.1 increments
            # Allow some floating point tolerance
            if abs(round(weight * 10) - (weight * 10)) > 0.01:
                flash('Weight must be in 0.1 increments (e.g., 3.5, -7.2, 11.0).', 'error')
                return render_template('scenarios/link_event.html', marked=marked, available_events=[])
                
        except ValueError:
            flash('Invalid weight value.', 'error')
            return render_template('scenarios/link_event.html', marked=marked)
        
        # Link the event
        try:
            marked.add_event(event_code, weight, current_user.id, notes)
            db.session.commit()
            flash(f'Event {event_code} linked successfully!', 'success')
            return redirect(url_for('scenarios.marked_detail', marked_id=marked_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error linking event: {str(e)}', 'error')
    
    # GET: Show available events
    from app.models import ControlFrame
    
    # Get events not yet linked to this marked scenario
    linked_event_codes = [link.event_code for link in marked.event_links]
    available_events = ControlFrame.query.filter(
        ~ControlFrame.event_code.in_(linked_event_codes) if linked_event_codes else True
    ).order_by(ControlFrame.rec_timestamp.desc()).limit(50).all()
    
    return render_template('scenarios/link_event.html', 
                         marked=marked,
                         available_events=available_events)


@bp.route('/marked/<int:marked_id>/unlink-event/<event_code>', methods=['POST'])
@login_required
def unlink_event(marked_id, event_code):
    """Remove event link from marked scenario"""
    marked = MarkedScenario.query.get_or_404(marked_id)
    
    # Check if user owns this marked scenario
    if marked.analyst_id != current_user.id:
        flash('You can only unlink events from your own assessments.', 'error')
        return redirect(url_for('scenarios.marked_detail', marked_id=marked_id))
    
    link = ScenarioEvent.query.filter_by(
        marked_scenario_id=marked_id,
        event_code=event_code
    ).first()
    
    if not link:
        flash(f'Event {event_code} is not linked to this assessment.', 'error')
        return redirect(url_for('scenarios.marked_detail', marked_id=marked_id))
    
    try:
        # Reverse the probability change
        previous_prob = float(marked.current_probability)
        new_prob = previous_prob - float(link.weight)
        new_prob = max(0.0, min(1.0, new_prob))
        
        marked.current_probability = new_prob
        
        # Add to history
        if not marked.probability_history:
            marked.probability_history = []
        
        marked.probability_history.append({
            'probability': float(new_prob),
            'timestamp': datetime.utcnow().isoformat(),
            'reason': f'Event {event_code} unlinked (weight {link.weight} removed)',
            'event_code': event_code,
            'user_id': current_user.id
        })
        
        marked.updated_at = datetime.utcnow()
        
        # Delete the link
        db.session.delete(link)
        db.session.commit()
        
        flash(f'Event {event_code} unlinked successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error unlinking event: {str(e)}', 'error')
    
    return redirect(url_for('scenarios.marked_detail', marked_id=marked_id))

    # Add this route to app/routes/scenarios.py

@bp.route('/<int:scenario_id>/delete', methods=['POST'])
@login_required
def delete_scenario(scenario_id):
    """Delete a scenario (admin/creator only)"""
    scenario = Scenario.query.get_or_404(scenario_id)
    
    # Check if user created this scenario or is admin
    if scenario.created_by_id != current_user.id and current_user.role != 'admin':
        flash('You do not have permission to delete this scenario.', 'error')
        return redirect(url_for('scenarios.detail', scenario_id=scenario_id))
    
    # Check if scenario has marked scenarios
    if scenario.marked_scenarios:
        flash(f'Cannot delete scenario with {len(scenario.marked_scenarios)} existing assessments.', 'error')
        return redirect(url_for('scenarios.detail', scenario_id=scenario_id))
    
    scenario_code = scenario.scenario_code
    
    try:
        db.session.delete(scenario)
        db.session.commit()
        flash(f'Scenario {scenario_code} deleted successfully.', 'success')
        return redirect(url_for('scenarios.index'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting scenario: {str(e)}', 'error')
        return redirect(url_for('scenarios.detail', scenario_id=scenario_id))