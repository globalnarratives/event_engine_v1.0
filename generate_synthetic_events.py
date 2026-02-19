"""
Generate synthetic Control Frame events for testing
Creates 105 events (15 per CIE template) with randomized components
"""

import random
from datetime import datetime, timedelta
import csv
import json
from app import create_app, db
from app.models import Position, Actor, ActionCode

# Your 7 CIE body templates
CIE_TEMPLATES = [
    """$ usa.hos {s-pr} / rus<>ukr
  ▪ {s-st} rus.hos x[rv] {s-pr}""",
    
    """$ jpn.com.soe.55105050.001 {nv}
  ▪ jpn.min.fisc.exc.01 [a-in] $ {nt}""",
    
    """$ e.21112025.waf.001
  ▪ nga.org.rlg.xtn.mmb.001 [s-es] $ {ab} / qty""",
    
    """$ gnb.min.dfns.ary {rm} gnb.1972.001 ! gnb.hos""",
    
    """$ {ak} # (dig) @ isr.com.ind.50202010
  ▪ [s-as] $ {ak} / irn.min.intl""",
    
    """$ rwa.hos <{mt}> cod.hos @ usa.cpl
  ▪ {s-rp} rwa.hos [ag] cod.hos""",
    
    """$ gbr.cpl.exc.01 {ag} gbr.lh.318-2024-26.lex
  ▪ {s-op} $ sbs.imp.lex"""
]

# Configuration
EVENTS_PER_TEMPLATE = 20
START_DATE = datetime(2025, 11, 1)  # November 1, 2025
END_DATE = datetime(2026, 1, 31)    # Today
TOTAL_DAYS = (END_DATE - START_DATE).days

# Sample data pools (replace with actual database queries)
app = create_app()
with app.app_context():
    # Get all position codes
    positions = Position.query.all()
    position_codes = [p.position_code for p in positions]
    
    # Get all actor codes
    actors = Actor.query.all()
    actor_codes = [a.actor_id for a in actors]
    
    # Combine into one pool
    EVENT_ACTORS = position_codes + actor_codes
    
    print(f"Loaded {len(position_codes)} positions and {len(actor_codes)} actors")

with app.app_context():
    action_codes_db = ActionCode.query.all()
    print(f"Loaded {len(action_codes_db)} action codes")

REGIONS = [
    'weu', 'eeu', 'nam', 'sam', 'nea', 'sea', 'oce', 
    'sas', 'cas', 'mea', 'waf', 'eaf', 'caf', 'saf', 'cmb'
]

RELIABILITY = ['1', '2', '3', '4', '5', '6']
CREDIBILITY = ['A', 'B', 'C', 'D', 'E', 'F']

def generate_rel_cred():
    """Generate random reliability-credibility code"""
    return f"{random.choice(RELIABILITY)}-{random.choice(CREDIBILITY)}"

def generate_random_date():
    """Generate random date within range"""
    random_days = random.randint(0, TOTAL_DAYS)
    return START_DATE + timedelta(days=random_days)

def get_ordinal_for_date_region(date, region, existing_events):
    """Calculate next ordinal for given date and region"""
    date_str = date.strftime('%d%m%Y')
    pattern = f"e.{date_str}.{region}."
    
    # Find existing events with this date/region
    matching = [e for e in existing_events if e['event_code'].startswith(pattern)]
    
    if not matching:
        return 1
    
    # Extract ordinals and find max
    ordinals = []
    for event in matching:
        parts = event['event_code'].split('.')
        if len(parts) == 4:
            try:
                ordinals.append(int(parts[3]))
            except ValueError:
                pass
    
    return max(ordinals) + 1 if ordinals else 1

def extract_subjects_objects(cie_body):
    """
    Simple extraction - just find all entity codes
    Split roughly half to subjects, half to objects
    """
    import re
    # Match xxx.yyy.zzz or xxx.yyy patterns
    entities = re.findall(r'\b[a-z]{3}(?:\.[a-z]{3,4})+(?:\.\d{2,4})?\b', cie_body)
    
    # Remove duplicates while preserving order
    unique_entities = []
    for e in entities:
        if e not in unique_entities:
            unique_entities.append(e)
    
    # Split roughly in half
    mid = len(unique_entities) // 2
    subjects = unique_entities[:mid] if mid > 0 else []
    objects = unique_entities[mid:] if mid < len(unique_entities) else []
    
    return subjects, objects

def generate_events():
    """Generate all synthetic events"""
    events = []
    
    for template_idx, cie_template in enumerate(CIE_TEMPLATES):
        for i in range(EVENTS_PER_TEMPLATE):
            event_actor = random.choice(EVENT_ACTORS)
            action_code_obj = random.choice(action_codes_db)  # Pick the full object, not just the code
            action_code = action_code_obj.action_code
            action_type = action_code_obj.action_category  # Get the category
            region = random.choice(REGIONS)
            rel_cred = generate_rel_cred()
            event_date = generate_random_date()
            hours_after = random.randint(1, 48)
            minutes_after = random.randint(0, 59)
            seconds_after = random.randint(0, 59)
            rec_timestamp = event_date + timedelta(hours=hours_after, minutes=minutes_after, seconds=seconds_after)

            # Generate event code
            ordinal = get_ordinal_for_date_region(event_date, region, events)
            event_code = f"e.{event_date.strftime('%d%m%Y')}.{region}.{ordinal:03d}"
            
            # Extract entities
            subjects, objects = extract_subjects_objects(cie_template)
            
            # Create event record
            event = {
                'event_code': event_code,
                'rec_timestamp': rec_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'event_actor': event_actor,
                'action_type': action_type,
                'action_code': action_code,  
                'rel_cred': rel_cred,
                'cie_body': cie_template,
                'identified_subjects': json.dumps(subjects), 
                'identified_objects': json.dumps(objects),
                'source_article_id': '' 
            }
            
            events.append(event)
    
    return events

def write_csv(events, filename='seed_data/synthetic_events.csv'):
    """Write events to CSV file"""
    fieldnames = [
        'event_code', 'rec_timestamp', 'event_actor', 'action_code', 'action_type',
        'rel_cred', 'cie_body', 'identified_subjects', 
        'identified_objects', 'source_article_id'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(events)
    
    print(f"✓ Generated {len(events)} synthetic events")
    print(f"✓ Written to {filename}")
    print(f"✓ Date range: {START_DATE.date()} to {END_DATE.date()}")
    print(f"✓ Regions: {len(REGIONS)}")
    print(f"✓ Templates: {len(CIE_TEMPLATES)}")

if __name__ == '__main__':
    events = generate_events()
    write_csv(events)
    
    # Print sample
    print("\nSample events:")
    for event in events[:3]:
        print(f"  {event['event_code']} | {event['event_actor']} | {event['action_code']} | {event['rel_cred']}")