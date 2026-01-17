from app import db
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from flask_login import UserMixin
from datetime import datetime


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


class ActionCode(db.Model):
    """Action code taxonomy - maps codes to types and categories"""
    __tablename__ = 'action_codes'
    
    action_code = db.Column(db.String(10), primary_key=True)
    action_type = db.Column(db.String(50), nullable=False)
    action_category = db.Column(db.String(50))
    definition = db.Column(db.Text)
    
    def __repr__(self):
        return f'<ActionCode {self.action_code}: {self.action_type}>'


class ControlFrame(db.Model):
    """Control Frame - metadata and parsed content for CIE events"""
    __tablename__ = 'control_frame'
    
    event_code = db.Column(db.String(30), primary_key=True)
    rec_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    event_actor = db.Column(db.Text) 
    action_type = db.Column(db.String(50))
    action_code = db.Column(db.String(10), db.ForeignKey('action_codes.action_code'))
    rel_cred = db.Column(db.String(5)) 
    cie_body = db.Column(db.Text) 

    # CHANGED: Use JSONB for automatic list handling
    # No more manual comma-splitting needed
    identified_subjects = db.Column(JSONB, default=list) 
    identified_objects = db.Column(JSONB, default=list)
    
    source_article_id = db.Column(db.Integer, db.ForeignKey('articles.article_id'))
    
    # CHANGED: Specifically use JSONB for better indexing/performance over standard JSON
    parse_tree_cache = db.Column(JSONB) 
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    action = db.relationship('ActionCode', backref='control_frames')
    source_article = db.relationship('Article', backref='control_frames')
    
    def __repr__(self):
        return f'<ControlFrame {self.event_code}: {self.action_code}>'
    
    # Simplified: JSONB returns a list automatically
    def get_subjects_list(self):
        return self.identified_subjects or []
    
    def get_objects_list(self):
        return self.identified_objects or []

class Institution(db.Model):
    """Organizational entities that contain positions"""
    __tablename__ = 'institutions'
    
    institution_code = db.Column(db.String(100), primary_key=True)
    institution_name = db.Column(db.String(300), nullable=False)
    institution_type = db.Column(db.String(50))
    institution_layer = db.Column(db.String(10))  # e.g., "01", "02", etc.
    institution_subtype = db.Column(db.String(50))  # Optional subtype categorization
    country_code = db.Column(db.String(3))
    
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
    hierarchy_level = db.Column(db.String(12))
    
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


# class Event(db.Model):
#     """CIE-coded events - the primary analytical unit (LEGACY - being replaced by ControlFrame)"""
#     __tablename__ = 'events'
    
#     event_code = db.Column(db.String(50), primary_key=True)
#     event_date = db.Column(db.Date, nullable=False)
#     region = db.Column(db.String(3), nullable=False)
#     ordinal = db.Column(db.Integer, nullable=False)
#     recorded_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
#     core_action = db.Column(db.String(10), nullable=False)
#     cie_description = db.Column(db.String(250), nullable=False)
#     natural_summary = db.Column(db.String(250), nullable=False)
#     article_url = db.Column(db.String(500), nullable=False)
#     article_headline = db.Column(db.String(250))
#     created_by = db.Column(db.String(100))
    
#     # Relationships
#     event_actors = db.relationship('EventActor', back_populates='event', cascade='all, delete-orphan')
    
#     __table_args__ = (
#         db.CheckConstraint(
#             region.in_(['weu', 'eeu', 'nam', 'sam', 'cmb', 'nea', 'sea', 'oce', 'sas', 'mea', 'eaf', 'caf', 'saf', 'waf']),
#             name='chk_region'
#         ),
#         db.UniqueConstraint('event_date', 'region', 'ordinal', name='unique_event_ordinal'),
#     )
    
#     def __repr__(self):
#         return f'<Event {self.event_code}: {self.natural_summary[:50]}>'
    
#     def get_subjects(self):
#         """Get all subject actors/positions for this event"""
#         return EventActor.query.filter_by(
#             event_code=self.event_code,
#             role_type='subject'
#         ).all()
    
#     def get_objects(self):
#         """Get all object actors/positions for this event"""
#         return EventActor.query.filter_by(
#             event_code=self.event_code,
#             role_type='object'
#         ).all()


class Tenure(db.Model):
    """Links actors to positions with time bounds"""
    __tablename__ = 'tenures'
    
    tenure_id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.String(20), db.ForeignKey('actors.actor_id'), nullable=False)
    position_code = db.Column(db.String(100), db.ForeignKey('positions.position_code'), nullable=False)
    tenure_start = db.Column(db.Date, nullable=False)
    tenure_end = db.Column(db.Date)
    notes = db.Column(db.String(100))
    
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

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='analyst')  # 'admin' or 'analyst'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<User {self.username}>'

#class EventActor(db.Model):
    # """Links events to actors/positions as subjects or objects"""
    # __tablename__ = 'event_actors'
    
    # event_actor_id = db.Column(db.Integer, primary_key=True)
    # event_code = db.Column(db.String(50), db.ForeignKey('events.event_code'), nullable=False)
    # code = db.Column(db.String(100), nullable=False)
    # code_type = db.Column(db.String(20), nullable=False)
    # role_type = db.Column(db.String(20), nullable=False)
    
    # # Relationships
    # event = db.relationship('Event', back_populates='event_actors')
    
    # __table_args__ = (
    #     db.CheckConstraint(
    #         code_type.in_(['position', 'actor']),
    #         name='chk_code_type'
    #     ),
    #     db.CheckConstraint(
    #         role_type.in_(['subject', 'object']),
    #         name='chk_role_type'
    #     ),
    # )
    
    # def __repr__(self):
    #     return f'<EventActor {self.code} as {self.role_type} in {self.event_code}>'
    
    # def resolve_actor(self):
    #     """Resolve the actual actor, whether directly coded or via position on event date"""
    #     if self.code_type == 'actor':
    #         return Actor.query.get(self.code)
    #     elif self.code_type == 'position':
    #         position = Position.query.get(self.code)
    #         if position and self.event:
    #             return position.get_holder_on_date(self.event.event_date)
    #     return None
    
    # def get_display_info(self):
    #     """Get display information for this event actor"""
    #     if self.code_type == 'actor':
    #         actor = Actor.query.get(self.code)
    #         if actor:
    #             return {
    #                 'code': self.code,
    #                 'type': 'actor',
    #                 'display': f'{self.code}: {actor.get_display_name()}'
    #             }
    #     elif self.code_type == 'position':
    #         position = Position.query.get(self.code)
    #         if position:
    #             holder = None
    #             if self.event:
    #                 holder = position.get_holder_on_date(self.event.event_date)
    #             holder_name = holder.get_display_name() if holder else 'Vacant'
    #             return {
    #                 'code': self.code,
    #                 'type': 'position',
    #                 'display': f'{self.code}: {position.position_title} ({holder_name})'
    #             }
    #     return {
    #         'code': self.code,
    #         'type': self.code_type,
    #         'display': self.code
    #     }

    # Add these models to your existing app/models.py file

class Scenario(db.Model):
    """Shared scenario template - the proposition/question"""
    __tablename__ = 'scenarios'
    
    id = db.Column(db.Integer, primary_key=True)
    scenario_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    close_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    created_by = db.relationship('User', backref='created_scenarios')
    marked_scenarios = db.relationship('MarkedScenario', back_populates='scenario', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Scenario {self.scenario_code}>'


class MarkedScenario(db.Model):
    """Analyst's assessment of a scenario - the work product"""
    __tablename__ = 'marked_scenarios'
    
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey('scenarios.id', ondelete='CASCADE'), nullable=False)
    analyst_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.Text)  # Optional custom label like "Conservative Estimate"
    description = db.Column(db.Text)  # Analyst's notes
    
    # Probability tracking
    current_probability = db.Column(db.Numeric(4, 3))  # 0.000 to 1.000
    initial_probability = db.Column(db.Numeric(4, 3))  # Starting assessment
    probability_history = db.Column(db.JSON)  # Array of {probability, timestamp, reason, event_code, user_id}
    
    # Status and metadata
    status = db.Column(db.String(20), default='active')  # active, resolved_true, resolved_false, deprecated
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Future: narratives
    # narrative_id = db.Column(db.Integer, db.ForeignKey('narratives.id'))
    
    # Relationships
    scenario = db.relationship('Scenario', back_populates='marked_scenarios')
    analyst = db.relationship('User', backref='marked_scenarios')
    event_links = db.relationship('ScenarioEvent', back_populates='marked_scenario', cascade='all, delete-orphan')
    
    @property
    def display_name(self):
        """Auto-generated display name: analyst-scenario_code [optional title]"""
        base = f"{self.analyst.username}-{self.scenario.scenario_code}"
        if self.title:
            return f"{base} [{self.title}]"
        return base
    
    def add_event(self, event_code, weight, user_id, notes=None):
        """Link an event with weight and recalculate probability"""
        # Create the link
        link = ScenarioEvent(
            marked_scenario_id=self.id,
            event_code=event_code,
            weight=weight,
            notes=notes,
            linked_by_id=user_id
        )
        db.session.add(link)
        
        # Recalculate probability (placeholder - implement your calculation logic)
        self.recalculate_probability(event_code, weight, user_id)
        
        return link
    
    def recalculate_probability(self, event_code, weight, user_id):
        """Update probability based on new event (implement your formula here)"""
        # Placeholder: Simple additive model
        previous_prob = float(self.current_probability) if self.current_probability else float(self.initial_probability)
        new_prob = previous_prob + float(weight)
        
        # Clamp to [0, 1]
        new_prob = max(0.0, min(1.0, new_prob))
        
        # Update current probability
        self.current_probability = new_prob
        
        # Add to history
        if not self.probability_history:
            self.probability_history = []
        
        self.probability_history.append({
            'probability': float(new_prob),
            'timestamp': datetime.utcnow().isoformat(),
            'reason': f'Event {event_code} linked with weight {weight}',
            'event_code': event_code,
            'user_id': user_id
        })
        
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<MarkedScenario {self.display_name}>'


class ScenarioEvent(db.Model):
    """Junction table: Links events to marked scenarios with weights"""
    __tablename__ = 'scenario_events'
    
    id = db.Column(db.Integer, primary_key=True)
    marked_scenario_id = db.Column(db.Integer, db.ForeignKey('marked_scenarios.id', ondelete='CASCADE'), nullable=False, index=True)
    event_code = db.Column(db.String(50), db.ForeignKey('control_frame.event_code', ondelete='CASCADE'), nullable=False, index=True)
    weight = db.Column(db.Numeric(5, 3))  # -9.999 to 9.999
    notes = db.Column(db.Text)  # Analyst's explanation for linking
    linked_at = db.Column(db.DateTime, default=datetime.utcnow)
    linked_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    marked_scenario = db.relationship('MarkedScenario', back_populates='event_links')
    event = db.relationship('ControlFrame', backref='scenario_links')
    linked_by = db.relationship('User')
    
    # Prevent duplicate links
    __table_args__ = (
        db.UniqueConstraint('marked_scenario_id', 'event_code', name='uq_marked_scenario_event'),
    )
    
    def __repr__(self):
        return f'<ScenarioEvent {self.marked_scenario_id}:{self.event_code} w={self.weight}>'