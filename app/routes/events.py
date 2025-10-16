from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from app.models import Event, EventActor, Article, Actor, Position
from app.forms import EventCreationForm, EventEditForm, EventSearchForm
from app import db
from datetime import datetime

bp = Blueprint('events', __name__, url_prefix='/events')


@bp.route('/')
def index():
    """List all events with search/filter"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    query = Event.query
    search_form = EventSearchForm(request.args)
    
    # Apply filters
    if request.args.get('date_from'):
        query = query.filter(Event.event_date >= search_form.date_from.data)
    
    if request.args.get('date_to'):
        query = query.filter(Event.event_date <= search_form.date_to.data)
    
    if request.args.get('region') and search_form.region.data:
        query = query.filter(Event.region == search_form.region.data)
    
    if request.args.get('core_action'):
        query = query.filter(Event.core_action.ilike(f'%{search_form.core_action.data}%'))
    
    if request.args.get('search_text'):
        search = f'%{search_form.search_text.data}%'
        query = query.filter(
            db.or_(
                Event.cie_description.ilike(search),
                Event.natural_summary.ilike(search)
            )
        )
    
    # Sort by event date (newest first)
    query = query.order_by(Event.event_date.desc())
    
    events = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('events/index.html', 
                         events=events,
                         search_form=search_form)


@bp.route('/<event_code>')
def detail(event_code):
    """View event details with resolved actors"""
    event = Event.query.get_or_404(event_code)
    
    # Get subjects and objects with display info
    subjects = []
    for ea in event.get_subjects():
        subjects.append(ea.get_display_info())
    
    objects = []
    for ea in event.get_objects():
        objects.append(ea.get_display_info())
    
    return render_template('events/detail.html',
                         event=event,
                         subjects=subjects,
                         objects=objects)


@bp.route('/create', methods=['GET', 'POST'])
@bp.route('/create/<int:article_id>', methods=['GET', 'POST'])
def create(article_id=None):
    """Create new event, optionally from an article"""
    form = EventCreationForm()
    article = None
    
    # Load article if specified
    if article_id:
        article = Article.query.get_or_404(article_id)
        form.article_id.data = article_id
    
    # Populate actor/position choices
    actors = Actor.query.order_by(Actor.surname, Actor.given_name).all()
    positions = Position.query.order_by(Position.position_title).all()
    
    choices = []
    for actor in actors:
        choices.append((f'actor:{actor.actor_id}', f'{actor.actor_id} - {actor.get_display_name()}'))
    for position in positions:
        choices.append((f'position:{position.position_code}', f'{position.position_code} - {position.position_title}'))
    
    form.subject_codes.choices = choices
    form.object_codes.choices = choices
    
    if form.validate_on_submit():
        # Generate event code
        event_date = form.event_date.data
        region = form.region.data
        
        # Calculate ordinal for this date and region
        existing_count = Event.query.filter_by(
            event_date=event_date,
            region=region
        ).count()
        ordinal = existing_count + 1
        
        # Format event code: e.ddmmyyyy.region.ordinal
        event_code = f"e.{event_date.strftime('%d%m%Y')}.{region}.{ordinal:04d}"
        
        # Create event
        event = Event(
            event_code=event_code,
            event_date=event_date,
            region=region,
            ordinal=ordinal,
            core_action=form.core_action.data,
            cie_description=form.cie_description.data,
            natural_summary=form.natural_summary.data,
            article_url=article.url if article else '',
            article_headline=article.headline if article else '',
            created_by=form.created_by.data
        )
        
        db.session.add(event)
        
        # Add subject actors
        for code in form.subject_codes.data:
            code_type, code_value = code.split(':', 1)
            event_actor = EventActor(
                event_code=event_code,
                code=code_value,
                code_type=code_type,
                role_type='subject'
            )
            db.session.add(event_actor)
        
        # Add object actors
        for code in form.object_codes.data:
            code_type, code_value = code.split(':', 1)
            event_actor = EventActor(
                event_code=event_code,
                code=code_value,
                code_type=code_type,
                role_type='object'
            )
            db.session.add(event_actor)
        
        # Mark article as processed if it exists
        if article:
            article.is_processed = True
        
        db.session.commit()
        
        flash(f'Event {event_code} created successfully', 'success')
        return redirect(url_for('events.detail', event_code=event_code))
    
    return render_template('events/create.html',
                         form=form,
                         article=article)


@bp.route('/<event_code>/edit', methods=['GET', 'POST'])
def edit(event_code):
    """Edit existing event"""
    event = Event.query.get_or_404(event_code)
    form = EventEditForm(obj=event)
    
    # Populate actor/position choices
    actors = Actor.query.order_by(Actor.surname, Actor.given_name).all()
    positions = Position.query.order_by(Position.position_title).all()
    
    choices = []
    for actor in actors:
        choices.append((f'actor:{actor.actor_id}', f'{actor.actor_id} - {actor.get_display_name()}'))
    for position in positions:
        choices.append((f'position:{position.position_code}', f'{position.position_code} - {position.position_title}'))
    
    form.subject_codes.choices = choices
    form.object_codes.choices = choices
    
    if request.method == 'GET':
        # Pre-populate existing actors
        subjects = [f'{ea.code_type}:{ea.code}' for ea in event.get_subjects()]
        objects = [f'{ea.code_type}:{ea.code}' for ea in event.get_objects()]
        form.subject_codes.data = subjects
        form.object_codes.data = objects
    
    if form.validate_on_submit():
        # Update event fields
        event.event_date = form.event_date.data
        event.core_action = form.core_action.data
        event.cie_description = form.cie_description.data
        event.natural_summary = form.natural_summary.data
        event.created_by = form.created_by.data
        
        # Remove existing event actors
        EventActor.query.filter_by(event_code=event_code).delete()
        
        # Add updated subject actors
        for code in form.subject_codes.data:
            code_type, code_value = code.split(':', 1)
            event_actor = EventActor(
                event_code=event_code,
                code=code_value,
                code_type=code_type,
                role_type='subject'
            )
            db.session.add(event_actor)
        
        # Add updated object actors
        for code in form.object_codes.data:
            code_type, code_value = code.split(':', 1)
            event_actor = EventActor(
                event_code=event_code,
                code=code_value,
                code_type=code_type,
                role_type='object'
            )
            db.session.add(event_actor)
        
        db.session.commit()
        
        flash(f'Event {event_code} updated successfully', 'success')
        return redirect(url_for('events.detail', event_code=event_code))
    
    return render_template('events/edit.html',
                         form=form,
                         event=event)


@bp.route('/<event_code>/delete', methods=['POST'])
def delete(event_code):
    """Delete event"""
    event = Event.query.get_or_404(event_code)
    
    # EventActor entries will be cascade deleted
    db.session.delete(event)
    db.session.commit()
    
    flash(f'Event {event_code} deleted', 'success')
    return redirect(url_for('events.index'))