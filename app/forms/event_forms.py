from flask_wtf import FlaskForm # type: ignore
from wtforms import StringField, TextAreaField, DateField, SelectField, SelectMultipleField, HiddenField # type:ignore
from wtforms.validators import DataRequired, Length, Optional, ValidationError # type: ignore
from datetime import date


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
                        choices=[
                            ('weu', 'Western Europe'),
                            ('eeu', 'Eastern Europe'),
                            ('nam', 'North America'),
                            ('sam', 'South America'),
                            ('nea', 'Northeast Asia'),
                            ('sea', 'Southeast Asia'),
                            ('sas', 'South and Central Asia'),
                            ('mea', 'Middle East and North Africa'),
                            ('ssa', 'Sub-Saharan Africa')
                        ],
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
                        choices=[
                            ('weu', 'Western Europe'),
                            ('eeu', 'Eastern Europe'),
                            ('nam', 'North America'),
                            ('sam', 'South America'),
                            ('nea', 'Northeast Asia'),
                            ('sea', 'Southeast Asia'),
                            ('sas', 'South and Central Asia'),
                            ('mea', 'Middle East and North Africa'),
                            ('ssa', 'Sub-Saharan Africa')
                        ],
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
                        choices=[('', 'All Regions'),
                                ('weu', 'Western Europe'),
                                ('eeu', 'Eastern Europe'),
                                ('nam', 'North America'),
                                ('sam', 'South America'),
                                ('nea', 'Northeast Asia'),
                                ('sea', 'Southeast Asia'),
                                ('sas', 'South and Central Asia'),
                                ('mea', 'Middle East and North Africa'),
                                ('ssa', 'Sub-Saharan Africa')],
                        validators=[Optional()])
    
    core_action = StringField('Core Action',
                             validators=[Optional()],
                             description='Filter by action code')
    
    search_text = StringField('Search Text',
                             validators=[Optional()],
                             description='Search in CIE description or natural summary')