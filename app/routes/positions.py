from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Position, Institution, Tenure, Actor
from app.forms import PositionForm, TenureForm
from app import db
from datetime import date

bp = Blueprint('positions', __name__, url_prefix='/positions')


@bp.route('/')
def index():
    """List all positions"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # Search functionality
    search = request.args.get('search', '')
    query = Position.query
    
    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            db.or_(
                Position.position_code.ilike(search_pattern),
                Position.position_title.ilike(search_pattern)
            )
        )
    
    # Sort by position title
    query = query.order_by(Position.position_title)
    
    positions = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('positions/index.html', positions=positions, search=search)


@bp.route('/<position_code>')
def detail(position_code):
    """View position details including tenure history"""
    position = Position.query.get_or_404(position_code)
    
    # Get all tenures for this position
    tenures = Tenure.query.filter_by(position_code=position_code).order_by(
        Tenure.tenure_start.desc()
    ).all()
    
    # Get current holder
    current_holder = position.get_current_holder()
    
    return render_template('positions/detail.html',
                         position=position,
                         tenures=tenures,
                         current_holder=current_holder)


@bp.route('/create', methods=['GET', 'POST'])
def create():
    """Create new position"""
    form = PositionForm()
    
    # Populate institution choices
    institutions = Institution.query.order_by(Institution.institution_name).all()
    form.institution_code.choices = [
        (inst.institution_code, f'{inst.institution_code} - {inst.institution_name}')
        for inst in institutions
    ]
    
    if form.validate_on_submit():
        position = Position(
            position_code=form.position_code.data,
            position_title=form.position_title.data,
            institution_code=form.institution_code.data,
            hierarchy_level=form.hierarchy_level.data,
            description=form.description.data
        )
        
        db.session.add(position)
        db.session.commit()
        
        flash(f'Position {position.position_title} created', 'success')
        return redirect(url_for('positions.detail', position_code=position.position_code))
    
    return render_template('positions/create.html', form=form)


@bp.route('/<position_code>/edit', methods=['GET', 'POST'])
def edit(position_code):
    """Edit existing position"""
    position = Position.query.get_or_404(position_code)
    form = PositionForm(obj=position)
    form.edit_mode = True
    
    # Populate institution choices
    institutions = Institution.query.order_by(Institution.institution_name).all()
    form.institution_code.choices = [
        (inst.institution_code, f'{inst.institution_code} - {inst.institution_name}')
        for inst in institutions
    ]
    
    if form.validate_on_submit():
        position.position_title = form.position_title.data
        position.institution_code = form.institution_code.data
        position.hierarchy_level = form.hierarchy_level.data
        position.description = form.description.data
        
        db.session.commit()
        
        flash(f'Position {position.position_title} updated', 'success')
        return redirect(url_for('positions.detail', position_code=position_code))
    
    return render_template('positions/edit.html', form=form, position=position)


@bp.route('/<position_code>/delete', methods=['POST'])
def delete(position_code):
    """Delete position (will cascade delete tenures)"""
    position = Position.query.get_or_404(position_code)
    title = position.position_title
    
    db.session.delete(position)
    db.session.commit()
    
    flash(f'Position {title} deleted', 'success')
    return redirect(url_for('positions.index'))


@bp.route('/<position_code>/assign', methods=['GET', 'POST'])
def assign_tenure(position_code):
    """Assign an actor to this position (create tenure)"""
    position = Position.query.get_or_404(position_code)
    form = TenureForm()
    
    # Populate actor choices
    actors = Actor.query.order_by(Actor.surname, Actor.given_name).all()
    form.actor_id.choices = [
        (actor.actor_id, f'{actor.actor_id} - {actor.get_display_name()}')
        for actor in actors
    ]
    
    # Set position (readonly)
    form.position_code.choices = [(position.position_code, position.position_title)]
    form.position_code.data = position.position_code
    
    if form.validate_on_submit():
        tenure = Tenure(
            actor_id=form.actor_id.data,
            position_code=position.position_code,
            tenure_start=form.tenure_start.data,
            tenure_end=form.tenure_end.data
        )
        
        db.session.add(tenure)
        db.session.commit()
        
        actor = Actor.query.get(form.actor_id.data)
        flash(f'{actor.get_display_name()} assigned to {position.position_title}', 'success')
        return redirect(url_for('positions.detail', position_code=position_code))
    
    return render_template('positions/assign.html', form=form, position=position)


@bp.route('/tenure/<int:tenure_id>/edit', methods=['GET', 'POST'])
def edit_tenure(tenure_id):
    """Edit existing tenure"""
    tenure = Tenure.query.get_or_404(tenure_id)
    form = TenureForm(obj=tenure)
    form.tenure_id = tenure_id
    
    # Populate actor choices
    actors = Actor.query.order_by(Actor.surname, Actor.given_name).all()
    form.actor_id.choices = [
        (actor.actor_id, f'{actor.actor_id} - {actor.get_display_name()}')
        for actor in actors
    ]
    
    # Populate position choices
    positions = Position.query.order_by(Position.position_title).all()
    form.position_code.choices = [
        (pos.position_code, f'{pos.position_code} - {pos.position_title}')
        for pos in positions
    ]
    
    if form.validate_on_submit():
        tenure.actor_id = form.actor_id.data
        tenure.position_code = form.position_code.data
        tenure.tenure_start = form.tenure_start.data
        tenure.tenure_end = form.tenure_end.data
        
        db.session.commit()
        
        flash('Tenure updated', 'success')
        return redirect(url_for('positions.detail', position_code=tenure.position_code))
    
    return render_template('positions/edit_tenure.html', form=form, tenure=tenure)


@bp.route('/tenure/<int:tenure_id>/delete', methods=['POST'])
def delete_tenure(tenure_id):
    """Delete tenure"""
    tenure = Tenure.query.get_or_404(tenure_id)
    position_code = tenure.position_code
    
    db.session.delete(tenure)
    db.session.commit()
    
    flash('Tenure deleted', 'success')
    return redirect(url_for('positions.detail', position_code=position_code))