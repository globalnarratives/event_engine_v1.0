from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from app.models import Article, ControlFrame, ActionCode
from app.forms import EventCFCreationForm, EventSearchForm
from app import db
from app.parser import CIEParser
from app.cie_highlighter import highlight_cie_syntax
import json

bp = Blueprint('events', __name__, url_prefix='/events')
parser = CIEParser()

@bp.route('/')
@login_required
def index():
    """List all events with search/filter"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    query = ControlFrame.query
    search_form = EventSearchForm(request.args)
    
    events = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('events/index.html', 
                         events=events,
                         search_form=search_form)

@bp.route('/create', methods=['GET', 'POST'])
@bp.route('/create/<int:article_id>', methods=['GET', 'POST'])
@login_required
def create(article_id=None):
    """Redirect to Control Frame event creation"""
    if article_id:
        return redirect(url_for('events.create_cf_route', article_id=article_id))
    return redirect(url_for('events.create_cf_route'))


@bp.route('/create-cf', methods=['GET', 'POST'])
@bp.route('/create-cf/<int:article_id>', methods=['GET', 'POST'])
@login_required
def create_cf_route(article_id=None):
    """
    Create new event using Control Frame with parser integration.
    
    JSONB columns automatically handle Python list serialization,
    so conversion is straightforward.
    """
    form = EventCFCreationForm()
    article = None
    
    # Load article if specified
    if article_id:
        article = Article.query.get_or_404(article_id)
        form.source_article_id.data = article_id
        form.source_article_url.data = article.url
    
    # Populate action code choices from database
    action_codes = ActionCode.query.order_by(ActionCode.action_category, ActionCode.action_code).all()
    
    # Group action codes by category for better UX
    grouped_choices = []
    current_category = None
    for ac in action_codes:
        if ac.action_category != current_category:
            if current_category is not None:
                grouped_choices.append(('---', '---'))  # Separator
            current_category = ac.action_category
        grouped_choices.append((ac.action_code, f"{ac.action_code} - {ac.action_type}"))
    
    form.action_code.choices = grouped_choices
    
    if form.validate_on_submit():
        # Get form data
        event_date = form.event_date.data
        region = form.region.data
        
        # Calculate ordinal for this date and region
        date_str = event_date.strftime('%d%m%Y')
        pattern = f'e.{date_str}.{region}.%'
        
        existing_events = ControlFrame.query.filter(
            ControlFrame.event_code.like(pattern)
        ).all()
        
        if existing_events:
            # Extract ordinals and find max
            ordinals = []
            for event in existing_events:
                # event_code format: e.DDMMYYYY.RRR.NNN
                parts = event.event_code.split('.')
                if len(parts) == 4:
                    try:
                        ordinals.append(int(parts[3]))
                    except ValueError:
                        pass
            ordinal = max(ordinals) + 1 if ordinals else 1
        else:
            ordinal = 1
        
        # Format event code
        event_code = f"e.{event_date.strftime('%d%m%Y')}.{region}.{ordinal:03d}"
        
        # Get action category from selected action code
        action = ActionCode.query.get(form.action_code.data)
        action_type = action.action_category if action else None
        
        # ================================================================
        # SIMPLIFIED JSONB HANDLING
        # ================================================================
        # Convert comma-separated strings to Python lists
        # JSONB columns automatically serialize these - no special handling needed!
        
        subjects_str = form.identified_subjects.data or ''
        if subjects_str.strip():
            identified_subjects = [s.strip() for s in subjects_str.split(',') if s.strip()]
        else:
            identified_subjects = []

        objects_str = form.identified_objects.data or ''
        if objects_str.strip():
            identified_objects = [s.strip() for s in objects_str.split(',') if s.strip()]
        else:
            identified_objects = []
        
        # Optional: Keep minimal debug output during testing
        print(f"Creating event {event_code}")
        print(f"  Subjects: {identified_subjects}")
        print(f"  Objects: {identified_objects}")
        
        # ================================================================
        # END SIMPLIFIED HANDLING
        # ================================================================

        # Parse tree cache handling
        parse_tree_data = None
        if form.parse_tree_cache.data:
            try:
                parse_tree_data = json.loads(form.parse_tree_cache.data)
            except json.JSONDecodeError:
                flash('Invalid parse tree data', 'error')
                return render_template('events/create_cf.html', form=form, article=article)

        # Create Control Frame record
        # JSONB columns accept Python lists directly - SQLAlchemy handles conversion
        control_frame = ControlFrame(
            event_code=event_code,
            event_actor=form.event_actor.data,
            action_code=form.action_code.data,
            action_type=action_type,
            rel_cred=form.rel_cred.data,
            cie_body=form.cie_body.data,
            identified_subjects=identified_subjects,  # Python list → JSONB automatically
            identified_objects=identified_objects,    # Python list → JSONB automatically
            source_article_id=form.source_article_id.data or None,
            parse_tree_cache=parse_tree_data          # Python dict → JSONB automatically
        )
        
        db.session.add(control_frame)
        
        # Mark article as processed if it exists
        if article:
            article.is_processed = True
        
        try:
            db.session.commit()
            print(f"✓ Event {event_code} saved successfully!")
            flash(f'Event {event_code} created successfully', 'success')
            return redirect(url_for('events.detail_cf_route', event_code=event_code))
        except Exception as e:
            db.session.rollback()
            print(f"✗ Database error: {e}")
            flash(f'Error saving event: {str(e)}', 'error')
            return render_template('events/create_cf.html', form=form, article=article)
    
    return render_template('events/create_cf.html',
                         form=form,
                         article=article)


@bp.route('/parse-cie', methods=['POST'])
@login_required
def parse_cie_route():
    """AJAX endpoint to parse CIE body and extract entities"""
    try:
        data = request.get_json()
        cie_body = data.get('cie_body', '')
        
        if not cie_body:
            return jsonify({
                'success': False,
                'error': 'No CIE body provided'
            })
        
        # Parse the CIE body
        result = parser.parse_safe(cie_body)
        
        if not result['success']:
            return jsonify({
                'success': False,
                'error': result['error']
            })
        
        # Extract entities from parse tree
        tree = result['tree']
        subjects = set()
        objects = set()
        
        # Walk the parse tree to find entity codes
        def extract_entities(node):
            if hasattr(node, 'data'):
                for child in node.children:
                    if hasattr(child, 'type'):
                        if child.type in ['POSITION_CODE', 'ACTOR_CODE', 'INSTITUTION_CODE']:
                            if len(subjects) == 0:
                                subjects.add(child.value)
                            else:
                                objects.add(child.value)
                    elif hasattr(child, 'children'):
                        extract_entities(child)
        
        extract_entities(tree)
        
        # Convert parse tree to JSON for storage
        def tree_to_dict(node):
            if hasattr(node, 'data'):
                return {
                    'type': 'rule',
                    'data': node.data,
                    'children': [tree_to_dict(child) for child in node.children]
                }
            else:
                return {
                    'type': 'token',
                    'token_type': node.type if hasattr(node, 'type') else 'unknown',
                    'value': str(node)
                }
        
        parse_tree_json = tree_to_dict(tree)
        
        return jsonify({
            'success': True,
            'subjects': list(subjects),
            'objects': list(objects),
            'parse_tree': parse_tree_json
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@bp.route('/cf/<event_code>')
@login_required
def detail_cf_route(event_code):
    """View Control Frame event details"""
    cf = ControlFrame.query.get_or_404(event_code)
    
    # Get subjects and objects as lists
    subjects = cf.get_subjects_list()
    objects = cf.get_objects_list()
    
    cie_html = highlight_cie_syntax(cf.cie_body)  # Fixed: use cf, not control_frame
    
    return render_template('events/detail_cf.html',
                          control_frame=cf,
                          subjects=subjects,
                          objects=objects,
                          cie_html=cie_html)


@bp.route('/get-action-type/<action_code>')
@login_required
def get_action_type_route(action_code):
    """AJAX endpoint to get action type for a given action code"""
    action = ActionCode.query.get(action_code)
    if action:
        return jsonify({
            'success': True,
            'action_type': action.action_category
        })
    return jsonify({
        'success': False,
        'error': 'Action code not found'
    })