from flask_wtf import FlaskForm # type:ignore
from wtforms import StringField, TextAreaField, DateField, SelectField, IntegerField # type:ignore
from wtforms.validators import DataRequired, Length, Optional, ValidationError # type:ignore
from datetime import date
from app.models import Institution, Position, Actor, Tenure
from app import db


class InstitutionForm(FlaskForm):
    """Form for creating/editing institutions"""
    
    institution_code = StringField('Institution Code',
                                  validators=[DataRequired(), Length(max=100)],
                                  description='CIE code (e.g., vie.cbk, jpn.com.mde.002)')
    
    institution_name = StringField('Institution Name',
                                  validators=[DataRequired(), Length(max=300)],
                                  description='Full name in natural language')
    
    institution_type = StringField('Institution Type',
                                  validators=[Optional(), Length(max=50)],
                                  description='Government, Corporate, NGO, etc. (optional)')
    
    country_code = StringField('Country Code',
                              validators=[Optional(), Length(max=3)],
                              description='ISO 3-letter country code (optional)')
    
    description = TextAreaField('Description',
                               validators=[Optional()],
                               description='Additional context')
    
    def validate_institution_code(self, field):
        """Check if institution code already exists (only for new institutions)"""
        if not hasattr(self, 'edit_mode') or not self.edit_mode:
            existing = Institution.query.get(field.data)
            if existing:
                raise ValidationError('Institution code already exists')


class PositionForm(FlaskForm):
    """Form for creating/editing positions"""
    
    position_code = StringField('Position Code',
                               validators=[DataRequired(), Length(max=100)],
                               description='CIE code (e.g., usa.hos, jpn.com.mde.002.exc.002)')
    
    position_title = StringField('Position Title',
                                validators=[DataRequired(), Length(max=300)],
                                description='Official title in natural language')
    
    institution_code = SelectField('Institution',
                                  validators=[DataRequired()],
                                  choices=[],
                                  description='Parent institution')
    
    hierarchy_level = StringField('Hierarchy Level',
                                 validators=[Optional(), Length(max=50)],
                                 description='hos, hog, min, exc, etc. (optional)')
    
    description = TextAreaField('Description',
                               validators=[Optional()],
                               description='Additional context')
    
    def validate_position_code(self, field):
        """Check if position code already exists (only for new positions)"""
        if not hasattr(self, 'edit_mode') or not self.edit_mode:
            existing = Position.query.get(field.data)
            if existing:
                raise ValidationError('Position code already exists')


class ActorForm(FlaskForm):
    """Form for creating/editing actors"""
    
    # For new actors, these fields generate the actor_id
    country_code = StringField('Country Code',
                              validators=[DataRequired(), Length(min=3, max=3)],
                              description='ISO 3-letter country code (e.g., usa, gbr, jpn)')
    
    birth_year = IntegerField('Birth Year',
                             validators=[DataRequired()],
                             description='4-digit birth year')
    
    surname = StringField('Surname',
                         validators=[DataRequired(), Length(max=150)],
                         description='Family/last name')
    
    given_name = StringField('Given Name',
                            validators=[DataRequired(), Length(max=150)],
                            description='First/given name')
    
    middle_name = StringField('Middle Name',
                             validators=[Optional(), Length(max=150)],
                             description='Middle name(s) (optional)')
    
    biographical_info = TextAreaField('Biographical Info',
                                     validators=[Optional()],
                                     description='Additional context')
    
    def validate_birth_year(self, field):
        """Ensure birth year is reasonable"""
        current_year = date.today().year
        if field.data < 1900 or field.data > current_year:
            raise ValidationError(f'Birth year must be between 1900 and {current_year}')
    
    def validate_country_code(self, field):
        """Ensure country code is lowercase"""
        if field.data != field.data.lower():
            raise ValidationError('Country code must be lowercase')


class ActorEditForm(FlaskForm):
    """Form for editing existing actors (cannot change actor_id components)"""
    
    actor_id = StringField('Actor ID',
                          render_kw={'readonly': True},
                          description='Cannot be changed after creation')
    
    surname = StringField('Surname',
                         validators=[DataRequired(), Length(max=150)])
    
    given_name = StringField('Given Name',
                            validators=[DataRequired(), Length(max=150)])
    
    middle_name = StringField('Middle Name',
                             validators=[Optional(), Length(max=150)])
    
    biographical_info = TextAreaField('Biographical Info',
                                     validators=[Optional()])


class TenureForm(FlaskForm):
    """Form for creating/editing tenures"""
    
    actor_id = SelectField('Actor',
                          validators=[DataRequired()],
                          choices=[],
                          description='Person holding the position')
    
    position_code = SelectField('Position',
                               validators=[DataRequired()],
                               choices=[],
                               description='Position held')
    
    tenure_start = DateField('Start Date',
                            validators=[DataRequired()],
                            description='Date tenure began')
    
    tenure_end = DateField('End Date',
                          validators=[Optional()],
                          description='Date tenure ended (leave blank if current)')
    
    def validate_tenure_end(self, field):
        """Ensure end date is after start date"""
        if field.data and self.tenure_start.data:
            if field.data < self.tenure_start.data:
                raise ValidationError('End date must be after start date')
    
    def validate(self, extra_validators=None):
        """Check for overlapping tenures on the same position"""
        if not super().validate(extra_validators):
            return False
        
        # Check for overlapping tenures
        overlapping = Tenure.query.filter(
            Tenure.position_code == self.position_code.data,
            Tenure.tenure_start <= (self.tenure_end.data or date(9999, 12, 31)),
            db.or_(
                Tenure.tenure_end.is_(None),
                Tenure.tenure_end >= self.tenure_start.data
            )
        )
        
        # Exclude current tenure if editing
        if hasattr(self, 'tenure_id') and self.tenure_id:
            overlapping = overlapping.filter(Tenure.tenure_id != self.tenure_id)
        
        if overlapping.first():
            self.tenure_start.errors.append('This position is already occupied during this time period')
            return False
        
        return True


class ArticleSearchForm(FlaskForm):
    """Form for searching/filtering articles"""
    
    date_from = DateField('Published From', validators=[Optional()])
    date_to = DateField('Published To', validators=[Optional()])
    
    source = StringField('Source', validators=[Optional()])
    
    search_text = StringField('Search Text',
                             validators=[Optional()],
                             description='Search in headline or summary')
    
    status = SelectField('Status',
                        choices=[
                            ('', 'All Articles'),
                            ('unprocessed', 'Unprocessed'),
                            ('processed', 'Processed'),
                            ('junk', 'Junk')
                        ],
                        validators=[Optional()])