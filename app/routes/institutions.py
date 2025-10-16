from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Institution, Position
from app.forms import InstitutionForm
from app import db

bp = Blueprint('institutions', __name__, url_prefix='/institutions')


@bp.route('/')
def index():
    """List all institutions"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # Search functionality
    search = request.args.get('search', '')
    query = Institution.query
    
    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            db.or_(
                Institution.institution_code.ilike(search_pattern),
                Institution.institution_name.ilike(search_pattern),
                Institution.country_code.ilike(search_pattern)
            )
        )
    
    # Sort by institution name
    query = query.order_by(Institution.institution_name)
    
    institutions = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('institutions/index.html', 
                         institutions=institutions, 
                         search=search)


@bp.route('/<institution_code>')
def detail(institution_code):
    """View institution details including all positions"""
    institution = Institution.query.get_or_404(institution_code)
    
    # Get all positions in this institution
    positions = Position.query.filter_by(
        institution_code=institution_code
    ).order_by(Position.position_title).all()
    
    return render_template('institutions/detail.html',
                         institution=institution,
                         positions=positions)


@bp.route('/create', methods=['GET', 'POST'])
def create():
    """Create new institution"""
    form = InstitutionForm()
    
    if form.validate_on_submit():
        institution = Institution(
            institution_code=form.institution_code.data,
            institution_name=form.institution_name.data,
            institution_type=form.institution_type.data,
            country_code=form.country_code.data,
            description=form.description.data
        )
        
        db.session.add(institution)
        db.session.commit()
        
        flash(f'Institution {institution.institution_name} created', 'success')
        return redirect(url_for('institutions.detail', 
                              institution_code=institution.institution_code))
    
    return render_template('institutions/create.html', form=form)


@bp.route('/<institution_code>/edit', methods=['GET', 'POST'])
def edit(institution_code):
    """Edit existing institution"""
    institution = Institution.query.get_or_404(institution_code)
    form = InstitutionForm(obj=institution)
    form.edit_mode = True
    
    if form.validate_on_submit():
        institution.institution_name = form.institution_name.data
        institution.institution_type = form.institution_type.data
        institution.country_code = form.country_code.data
        institution.description = form.description.data
        
        db.session.commit()
        
        flash(f'Institution {institution.institution_name} updated', 'success')
        return redirect(url_for('institutions.detail', 
                              institution_code=institution_code))
    
    return render_template('institutions/edit.html', form=form, institution=institution)


@bp.route('/<institution_code>/delete', methods=['POST'])
def delete(institution_code):
    """Delete institution (will cascade delete positions and tenures)"""
    institution = Institution.query.get_or_404(institution_code)
    name = institution.institution_name
    
    # Check if institution has positions
    position_count = Position.query.filter_by(institution_code=institution_code).count()
    
    if position_count > 0:
        flash(f'Cannot delete {name}: institution has {position_count} positions. Delete positions first.', 'error')
        return redirect(url_for('institutions.detail', institution_code=institution_code))
    
    db.session.delete(institution)
    db.session.commit()
    
    flash(f'Institution {name} deleted', 'success')
    return redirect(url_for('institutions.index'))