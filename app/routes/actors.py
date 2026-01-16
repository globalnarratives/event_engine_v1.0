from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Actor, Tenure
from app.forms import ActorForm, ActorEditForm
from app import db
from flask_login import login_required

bp = Blueprint('actors', __name__, url_prefix='/actors')


@bp.route('/')
@login_required
def index():
    """List all actors"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # Search functionality
    search = request.args.get('search', '')
    query = Actor.query
    
    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            db.or_(
                Actor.surname.ilike(search_pattern),
                Actor.given_name.ilike(search_pattern),
                Actor.actor_id.ilike(search_pattern)
            )
        )
    
    # Sort by surname, given name
    query = query.order_by(Actor.surname, Actor.given_name)
    
    actors = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('actors/index.html', actors=actors, search=search)


@bp.route('/<actor_id>')
@login_required
def detail(actor_id):
    """View actor details including tenure history"""
    actor = Actor.query.get_or_404(actor_id)
    
    # Get all tenures for this actor
    tenures = Tenure.query.filter_by(actor_id=actor_id).order_by(
        Tenure.tenure_start.desc()
    ).all()
    
    return render_template('actors/detail.html', actor=actor, tenures=tenures)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new actor"""
    form = ActorForm()
    
    if form.validate_on_submit():
        # Generate actor_id: country.year.ordinal
        country = form.country_code.data.lower()
        year = form.birth_year.data
        
        # Calculate next ordinal for this country/year
        prefix = f'{country}.{year}.'
        existing = Actor.query.filter(Actor.actor_id.like(f'{prefix}%')).all()
        
        if existing:
            # Find highest existing ordinal
            ordinals = []
            for actor in existing:
                parts = actor.actor_id.split('.')
                if len(parts) == 3:
                    try:
                        ordinals.append(int(parts[2]))
                    except ValueError:
                        pass
            next_ordinal = max(ordinals) + 1 if ordinals else 1
        else:
            next_ordinal = 1
        
        actor_id = f'{prefix}{next_ordinal:04d}'
        
        # Create actor
        actor = Actor(
            actor_id=actor_id,
            surname=form.surname.data,
            given_name=form.given_name.data,
            middle_name=form.middle_name.data,
            biographical_info=form.biographical_info.data
        )
        
        db.session.add(actor)
        db.session.commit()
        
        flash(f'Actor {actor.get_display_name()} created with ID {actor_id}', 'success')
        return redirect(url_for('actors.detail', actor_id=actor_id))
    
    return render_template('actors/create.html', form=form)


@bp.route('/<actor_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(actor_id):
    """Edit existing actor"""
    actor = Actor.query.get_or_404(actor_id)
    form = ActorEditForm(obj=actor)
    
    if form.validate_on_submit():
        actor.surname = form.surname.data
        actor.given_name = form.given_name.data
        actor.middle_name = form.middle_name.data
        actor.biographical_info = form.biographical_info.data
        
        db.session.commit()
        
        flash(f'Actor {actor.get_display_name()} updated', 'success')
        return redirect(url_for('actors.detail', actor_id=actor_id))
    
    return render_template('actors/edit.html', form=form, actor=actor)


@bp.route('/<actor_id>/delete', methods=['POST'])
@login_required
def delete(actor_id):
    """Delete actor (will cascade delete tenures)"""
    actor = Actor.query.get_or_404(actor_id)
    name = actor.get_display_name()
    
    db.session.delete(actor)
    db.session.commit()
    
    flash(f'Actor {name} deleted', 'success')
    return redirect(url_for('actors.index'))