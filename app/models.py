from datetime import datetime
from app import db


class Article(db.Model):
    """News articles collected from external sources"""
    __tablename__ = 'articles'
    
    article_id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False, unique=True)
    headline = db.Column(db.String(250), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    source_name = db.Column(db.String(200), nullable=False)
    published_date = db.Column(db.Date, nullable=False)
    collected_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_processed = db.Column(db.Boolean, nullable=False, default=False)
    is_junk = db.Column(db.Boolean, nullable=False, default=False)
    
    def __repr__(self):
        return f'<Article {self.article_id}: {self.headline[:50]}>'


class Institution(db.Model):
    """Organizational entities that contain positions"""
    __tablename__ = 'institutions'
    
    institution_code = db.Column(db.String(100), primary_key=True)
    institution_name = db.Column(db.String(300), nullable=False)
    institution_type = db.Column(db.String(50))
    institution_layer = db.Column(db.String(2))  # e.g., "01", "02", etc.
    institution_subtype_01 = db.Column(db.String(50))  # Optional subtype categorization
    country_code = db.Column(db.String(3))
    description = db.Column(db.Text)
    
    # Relationships
    positions = db.relationship('Position', back_populates='institution', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Institution {self.institution_code}: {self.institution_name}>'


class Position(db.Model):
    """Organizational roles within institutions"""
    __tablename__ = 'positions'
    
    country_code = db.Column(db.String(3))
    institution_name = db.Column(db.String(300), nullable=False)
    position_code = db.Column(db.String(100), primary_key=True)
    position_title = db.Column(db.String(300), nullable=False)
    institution_code = db.Column(db.String(100), db.ForeignKey('institutions.institution_code'), nullable=False)
    hierarchy_level = db.Column(db.String(2))
    description = db.Column(db.Text)
    
    # Relationships
    institution = db.relationship('Institution', back_populates='positions')
    tenures = db.relationship('Tenure', back_populates='position', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Position {self.position_code}: {self.position_title}>'
    
    def get_current_holder(self):
        """Get the actor currently holding this position"""
        current_tenure = Tenure.query.filter_by(
            position_code=self.position_code,
            tenure_end=None
        ).first()
        return current_tenure.actor if current_tenure else None
    
    def get_holder_on_date(self, date):
        """Get the actor holding this position on a specific date"""
        tenure = Tenure.query.filter(
            Tenure.position_code == self.position_code,
            Tenure.tenure_start <= date,
            db.or_(Tenure.tenure_end.is_(None), Tenure.tenure_end >= date)
        ).first()
        return tenure.actor if tenure else None


class Actor(db.Model):
    """Individual people identified by CIE actor codes"""
    __tablename__ = 'actors'
    
    actor_id = db.Column(db.String(20), primary_key=True)
    surname = db.Column(db.String(150), nullable=False)
    given_name = db.Column(db.String(150), nullable=False)
    middle_name = db.Column(db.String(150))
    birth_year = db.Column(db.Integer)
    position_code = db.Column(db.String(100))
    position_title = db.Column(db.String(300), nullable=False)                          
    biographical_info = db.Column(db.Text)
    
    # Relationships
    tenures = db.relationship('Tenure', back_populates='actor', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Actor {self.actor_id}: {self.get_display_name()}>'
    
    def get_display_name(self):
        """Format name as SURNAME, Given Middle"""
        if self.middle_name:
            return f'{self.surname.upper()}, {self.given_name} {self.middle_name}'
        return f'{self.surname.upper()}, {self.given_name}'
    
    def get_current_positions(self):
        """Get all positions currently held by this actor"""
        current_tenures = Tenure.query.filter_by(
            actor_id=self.actor_id,
            tenure_end=None
        ).all()
        return [tenure.position for tenure in current_tenures]
    
    def get_positions_on_date(self, date):
        """Get all positions held by this actor on a specific date"""
        tenures = Tenure.query.filter(
            Tenure.actor_id == self.actor_id,
            Tenure.tenure_start <= date,
            db.or_(Tenure.tenure_end.is_(None), Tenure.tenure_end >= date)
        ).all()
        return [tenure.position for tenure in tenures]


class Event(db.Model):
    """CIE-coded events - the primary analytical unit"""
    __tablename__ = 'events'
    
    event_code = db.Column(db.String(50), primary_key=True)
    event_date = db.Column(db.Date, nullable=False)
    region = db.Column(db.String(3), nullable=False)
    ordinal = db.Column(db.Integer, nullable=False)
    recorded_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    core_action = db.Column(db.String(10), nullable=False)
    cie_description = db.Column(db.String(250), nullable=False)
    natural_summary = db.Column(db.String(250), nullable=False)
    article_url = db.Column(db.String(500), nullable=False)
    article_headline = db.Column(db.String(250))
    created_by = db.Column(db.String(100))
    
    # Relationships
    event_actors = db.relationship('EventActor', back_populates='event', cascade='all, delete-orphan')
    
    __table_args__ = (
        db.CheckConstraint(
            region.in_(['weu', 'eeu', 'nam', 'sam', 'nea', 'sea', 'sas', 'mea', 'ssa']),
            name='chk_region'
        ),
        db.UniqueConstraint('event_date', 'region', 'ordinal', name='unique_event_ordinal'),
    )
    
    def __repr__(self):
        return f'<Event {self.event_code}: {self.natural_summary[:50]}>'
    
    def get_subjects(self):
        """Get all subject actors/positions for this event"""
        return EventActor.query.filter_by(
            event_code=self.event_code,
            role_type='subject'
        ).all()
    
    def get_objects(self):
        """Get all object actors/positions for this event"""
        return EventActor.query.filter_by(
            event_code=self.event_code,
            role_type='object'
        ).all()


class Tenure(db.Model):
    """Links actors to positions with time bounds"""
    __tablename__ = 'tenures'
    
    tenure_id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.String(20), db.ForeignKey('actors.actor_id'), nullable=False)
    position_code = db.Column(db.String(100), db.ForeignKey('positions.position_code'), nullable=False)
    tenure_start = db.Column(db.Date, nullable=False)
    tenure_end = db.Column(db.Date)
    notes = db.Column(db.String(20))
    
    # Relationships
    actor = db.relationship('Actor', back_populates='tenures')
    position = db.relationship('Position', back_populates='tenures')
    
    __table_args__ = (
        db.CheckConstraint(
            'tenure_end IS NULL OR tenure_end >= tenure_start',
            name='chk_tenure_dates'
        ),
        db.UniqueConstraint('actor_id', 'position_code', 'tenure_start', name='unique_tenure'),
    )
    
    def __repr__(self):
        end_str = self.tenure_end.strftime('%Y-%m-%d') if self.tenure_end else 'present'
        return f'<Tenure {self.actor_id} in {self.position_code}: {self.tenure_start.strftime("%Y-%m-%d")} to {end_str}>'
    
    def is_current(self):
        """Check if this tenure is currently active"""
        return self.tenure_end is None
    
    def was_active_on_date(self, date):
        """Check if this tenure was active on a specific date"""
        return (self.tenure_start <= date and 
                (self.tenure_end is None or self.tenure_end >= date))


class EventActor(db.Model):
    """Links events to actors/positions as subjects or objects"""
    __tablename__ = 'event_actors'
    
    event_actor_id = db.Column(db.Integer, primary_key=True)
    event_code = db.Column(db.String(50), db.ForeignKey('events.event_code'), nullable=False)
    code = db.Column(db.String(100), nullable=False)
    code_type = db.Column(db.String(20), nullable=False)
    role_type = db.Column(db.String(20), nullable=False)
    
    # Relationships
    event = db.relationship('Event', back_populates='event_actors')
    
    __table_args__ = (
        db.CheckConstraint(
            code_type.in_(['position', 'actor']),
            name='chk_code_type'
        ),
        db.CheckConstraint(
            role_type.in_(['subject', 'object']),
            name='chk_role_type'
        ),
    )
    
    def __repr__(self):
        return f'<EventActor {self.code} as {self.role_type} in {self.event_code}>'
    
    def resolve_actor(self):
        """Resolve the actual actor, whether directly coded or via position on event date"""
        if self.code_type == 'actor':
            return Actor.query.get(self.code)
        elif self.code_type == 'position':
            position = Position.query.get(self.code)
            if position and self.event:
                return position.get_holder_on_date(self.event.event_date)
        return None
    
    def get_display_info(self):
        """Get display information for this event actor"""
        if self.code_type == 'actor':
            actor = Actor.query.get(self.code)
            if actor:
                return {
                    'code': self.code,
                    'type': 'actor',
                    'display': f'{self.code}: {actor.get_display_name()}'
                }
        elif self.code_type == 'position':
            position = Position.query.get(self.code)
            if position:
                holder = None
                if self.event:
                    holder = position.get_holder_on_date(self.event.event_date)
                holder_name = holder.get_display_name() if holder else 'Vacant'
                return {
                    'code': self.code,
                    'type': 'position',
                    'display': f'{self.code}: {position.position_title} ({holder_name})'
                }
        return {
            'code': self.code,
            'type': self.code_type,
            'display': self.code
        }