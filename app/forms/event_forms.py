from flask_wtf import FlaskForm # type: ignore
from wtforms import StringField, TextAreaField, DateField, SelectField, SelectMultipleField, HiddenField # type:ignore
from wtforms.validators import DataRequired, Length, Optional, ValidationError, Regexp # type: ignore
from datetime import date
import re

# Define regions once - DRY principle
REGION_CHOICES = [
    ('weu', 'Western Europe'),
    ('eeu', 'Eastern Europe'),
    ('nam', 'North America'),
    ('sam', 'South America'),
    ('cmb', 'Central America & Caribbean'),
    ('nea', 'Northeast Asia'),
    ('sea', 'Southeast Asia'),
    ('oce', 'Oceania'),
    ('sas', 'South and Central Asia'),
    ('mea', 'Middle East and North Africa'),
    ('eaf', 'East Africa'),
    ('caf', 'Central Africa'),
    ('saf', 'Southern Africa'),
    ('waf', 'West Africa')
]

# For search forms that need an "All" option
REGION_CHOICES_WITH_ALL = [('', 'All Regions')] + REGION_CHOICES


class EventCFCreationForm(FlaskForm):
    """Control Frame form for creating CIE-coded events with parser integration"""
    
    # Event Code Components (analyst enters date and region, system generates full code)
    event_date = DateField('Event Date',
                          validators=[DataRequired()],
                          description='Date the event occurred (DDMMYYYY in event code)')
    
    region = SelectField('Region',
                        choices=REGION_CHOICES,
                        validators=[DataRequired()],
                        description='Geographic region (3-letter code)')
    
    # Control Frame Metadata
    event_actor = StringField('Event Actor',
                             validators=[DataRequired(), Length(max=100)],
                             description='Primary actor (position/actor code, e.g., rus.hos.spx)')
    
    action_code = SelectField('Action Code',
                             validators=[DataRequired()],
                             choices=[],  # Will be populated from action_codes table
                             description='Main action code')
    
    action_type = StringField('Action Type',
                             render_kw={'readonly': True},
                             description='Auto-populated from action code')
    
    rel_cred = StringField('Reliability/Credibility',
                          validators=[
                              DataRequired(),
                              Regexp(r'^[1-6]-[A-F]$', message='Format must be: [1-6]-[A-F] (e.g., 1-A, 3-C)')
                          ],
                          description='Reliability (1-6) and Credibility (A-F), e.g., 1-A')
    
    # Source Article
    source_article_id = HiddenField('Source Article ID')  # For events created from articles
    source_article_url = StringField('Source Article URL',
                                    validators=[Optional(), Length(max=500)],
                                    description='Article URL (for manual entry or paste)')
    
    # CIE Event Body
    cie_body = TextAreaField('Event Body (CIE)',
                        validators=[DataRequired()],
                        description='Enter event in CIE syntax (use Tab for subordination bullet ▪)',
                        render_kw={'spellcheck': 'false'})
    
    # Identified Subjects/Objects (populated after parsing, editable)
    identified_subjects = TextAreaField('Identified Subjects',
                                       validators=[Optional()],
                                       description='Auto-extracted from CIE body, editable')
    
    identified_objects = TextAreaField('Identified Objects',
                                      validators=[Optional()],
                                      description='Auto-extracted from CIE body, editable')
    
    # Parse tree cache (hidden, stores JSON parse tree)
    parse_tree_cache = HiddenField('Parse Tree Cache')
    
    def validate_event_date(self, field):
        """Ensure event date is not in the future"""
        if field.data > date.today():
            raise ValidationError('Event date cannot be in the future')
    
    def validate_event_actor(self, field):
        """Basic validation of event actor code format"""
        # Should match pattern like: xxx.yyy.zzz or xxx.yyy.zzz.nnn
        # We'll do database validation in the route
        if not re.match(r'^[a-z]{3}(\.[a-z0-9]+)+$', field.data.lower()):
            raise ValidationError('Event actor must be a valid CIE code (e.g., rus.hos.spx)')


class EventCreationForm(FlaskForm):
    """Form for creating CIE-coded events from articles"""
    
    # Hidden field to track source article
    article_id = HiddenField('Article ID')
    
    # Event identification
    event_date = DateField('Event Date', 
                          validators=[DataRequired()],
                          default=date.today,
                          description='Date the event occurred')
    
    region = SelectField('Region',
                        choices=REGION_CHOICES,
                        validators=[DataRequired()],
                        description='Geographic region')
    
    # CIE coding fields
    core_action = StringField('Core Action',
                             validators=[DataRequired(), Length(max=10)],
                             description='CIE action code (e.g., [s-tr], [sn])')
    
    cie_description = TextAreaField('CIE Description',
                                   validators=[DataRequired(), Length(max=250)],
                                   description='Full CIE expression (250 char max)')
    
    natural_summary = TextAreaField('Natural Summary',
                                   validators=[DataRequired(), Length(max=250)],
                                   description='Human-readable event summary (250 char max)')
    
    # Actor/Position selection - will be populated dynamically
    subject_codes = SelectMultipleField('Subject Actors/Positions',
                                       choices=[],
                                       description='Entities initiating/driving the action')
    
    object_codes = SelectMultipleField('Object Actors/Positions',
                                      choices=[],
                                      description='Entities receiving/targeted by the action')
    
    # Analyst tracking
    created_by = StringField('Created By',
                            validators=[Optional(), Length(max=100)],
                            description='Analyst name (optional)')
    
    def validate_event_date(self, field):
        """Ensure event date is not in the future"""
        if field.data > date.today():
            raise ValidationError('Event date cannot be in the future')


class EventEditForm(FlaskForm):
    """Form for editing existing events"""
    
    # Event code is displayed but not editable
    event_code = StringField('Event Code',
                            render_kw={'readonly': True},
                            description='Cannot be changed after creation')
    
    event_date = DateField('Event Date',
                          validators=[DataRequired()],
                          description='Date the event occurred')
    
    region = SelectField('Region',
                        choices=REGION_CHOICES,
                        validators=[DataRequired()],
                        render_kw={'readonly': True},
                        description='Cannot be changed (embedded in event code)')
    
    core_action = StringField('Core Action',
                             validators=[DataRequired(), Length(max=10)],
                             description='CIE action code')
    
    cie_description = TextAreaField('CIE Description',
                                   validators=[DataRequired(), Length(max=250)],
                                   description='Full CIE expression')
    
    natural_summary = TextAreaField('Natural Summary',
                                   validators=[DataRequired(), Length(max=250)],
                                   description='Human-readable event summary')
    
    subject_codes = SelectMultipleField('Subject Actors/Positions',
                                       choices=[])
    
    object_codes = SelectMultipleField('Object Actors/Positions',
                                      choices=[])
    
    created_by = StringField('Created By',
                            validators=[Optional(), Length(max=100)])


class EventSearchForm(FlaskForm):
    """Form for searching/filtering events"""
    
    date_from = DateField('Date From', validators=[Optional()])
    date_to = DateField('Date To', validators=[Optional()])
    
    region = SelectField('Region',
                        choices=REGION_CHOICES_WITH_ALL,
                        validators=[Optional()])
    
    core_action = StringField('Core Action',
                             validators=[Optional()],
                             description='Filter by action code')
    
    search_text = StringField('Search Text',
                             validators=[Optional()],
                             description='Search in CIE description or natural summary')