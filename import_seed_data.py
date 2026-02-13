"""
Master Seed Script - Load all reference data from CSVs
Run this after db.create_all() to populate the fresh database
"""

from app import db, create_app
from app.models import ActionCode, Actor, Institution, Position, Tenure
import csv
import os
from datetime import datetime

def load_action_codes():
    """Load action codes from CSV"""
    print("\n=== Loading Action Codes ===")
    if ActionCode.query.count() > 0:
        print(f"⚠ Action codes already loaded ({ActionCode.query.count()} found). Skipping.")
        return
    filepath = 'seed_data/action_codes.csv'
    
    if not os.path.exists(filepath):
        print(f"ERROR: {filepath} not found")
        return
    
    count = 0
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ac = ActionCode(
                action_code=row['action_code'],
                action_type=row['action_type'],
                action_category=row['action_category'],
                definition=row.get('definition', '')
            )
            db.session.add(ac)
            count += 1
    
    db.session.commit()
    print(f"✓ Loaded {count} action codes")


def load_actors():
    """Load actors from CSV"""
    print("\n=== Loading Actors ===")
    if Actor.query.count() > 0:
        print(f"⚠ Actors already loaded ({Actor.query.count()} found). Skipping.")
        return
    filepath = 'seed_data/actor_codes.csv'
    
    if not os.path.exists(filepath):
        print(f"ERROR: {filepath} not found")
        return
    
    count = 0
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            actor = Actor(
                actor_id=row['actor_id'],
                surname=row['surname'],
                given_name=row['given_name'],
                middle_name=row.get('middle_name', ''),
                birth_year=int(row['birth_year']) if row.get('birth_year') else None
            )
            db.session.add(actor)
            count += 1
    
    db.session.commit()
    print(f"✓ Loaded {count} actors")


def load_institutions():
    """Load institutions from CSV"""
    print("\n=== Loading Institutions ===")
    if Institution.query.count() > 0:
        print(f"⚠ Institutions already loaded ({Institution.query.count()} found). Skipping.")
        return
    filepath = 'seed_data/institution_codes.csv'
    
    if not os.path.exists(filepath):
        print(f"ERROR: {filepath} not found")
        return
    
    count = 0
    parent_map = {}  # institution_code -> parent_institution_code
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            institution = Institution(
                country_code=row['country_code'],
                institution_name=row['institution_name'],
                institution_code=row['institution_code'],
                institution_layer=row.get('institution_layer', ''),
                institution_type=row.get('institution_type', ''),
                institution_subtype=row.get('institution_subtype', '')
            )
            db.session.add(institution)
            # Store parent mapping for second pass
            parent_code = row.get('parent_institution_code', '').strip()
            if parent_code:
                parent_map[row['institution_code']] = parent_code
            count += 1

    db.session.commit()

    # Second pass: set parent_institution_code now that all institutions exist
    updated = 0
    for inst_code, parent_code in parent_map.items():
        # Skip self-references
        if inst_code == parent_code:
            continue
        # Only set if parent exists in DB
        parent = Institution.query.filter_by(institution_code=parent_code).first()
        if parent:
            inst = Institution.query.filter_by(institution_code=inst_code).first()
            if inst:
                inst.parent_institution_code = parent_code
                updated += 1

    db.session.commit()
    print(f"✓ Loaded {count} institutions ({updated} with parent links)")


def load_positions():
    """Load positions from CSV"""
    print("\n=== Loading Positions ===")
    if Position.query.count() > 0:
        print(f"⚠ Positions already loaded ({Position.query.count()} found). Skipping.")
        return
    filepath = 'seed_data/position_codes.csv'
    
    if not os.path.exists(filepath):
        print(f"ERROR: {filepath} not found")
        return
    
    count = 0
    reports_map = {}  # position_code -> reports_to_position_code
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            position = Position(
                country_code=row['country_code'],
                institution_name=row['institution_name'],
                institution_code=row['institution_code'],
                position_code=row['position_code'],
                position_title=row['position_title'],
                hierarchy_level=row.get('hierarchy_level', '')
            )
            db.session.add(position)
            # Store reports_to mapping for second pass
            reports_to = row.get('reports_to_position_code', '').strip()
            if reports_to:
                reports_map[row['position_code']] = reports_to
            count += 1

    db.session.commit()

    # Second pass: set reports_to_position_code now that all positions exist
    updated = 0
    for pos_code, reports_to in reports_map.items():
        # Skip self-references
        if pos_code == reports_to:
            continue
        # Only set if target position exists in DB
        target = Position.query.filter_by(position_code=reports_to).first()
        if target:
            pos = Position.query.filter_by(position_code=pos_code).first()
            if pos:
                pos.reports_to_position_code = reports_to
                updated += 1

    db.session.commit()
    print(f"✓ Loaded {count} positions ({updated} with reporting links)")


def load_tenures():
    """Load tenures from CSV"""
    print("\n=== Loading Tenures ===")
    if Tenure.query.count() > 0:
        print(f"⚠ Tenures already loaded ({Tenure.query.count()} found). Skipping.")
        return
    filepath = 'seed_data/tenure_codes.csv'
    
    if not os.path.exists(filepath):
        print(f"ERROR: {filepath} not found")
        return
    
    count = 0
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Parse dates if present
            tenure_start = None
            tenure_end = None
            
            if row.get('tenure_start'):
                try:
                    tenure_start = datetime.strptime(row['tenure_start'], '%d-%m-%y').date()
                except:
                    pass
            
            if row.get('tenure_end'):
                try:
                    tenure_end = datetime.strptime(row['tenure_end'], '%d-%m-%y').date()
                except:
                    pass
            
            tenure = Tenure(
                actor_id=row['actor_id'],
                position_code=row['position_code'],
                tenure_start=tenure_start,
                tenure_end=tenure_end,
                notes=row.get('notes', '')
            )
            db.session.add(tenure)
            count += 1
    
    db.session.commit()
    print(f"✓ Loaded {count} tenures")


def main():
    app = create_app() # Initialize the app instance
    with app.app_context(): # Manually push the context
        print("="*60)
        print("LOADING SEED DATA")
        print("="*60)
        
        # Load in dependency order
        load_action_codes()
        load_institutions()
        load_positions()
        load_actors()
        load_tenures()
        
        print("\n" + "="*60)
        print("SEED DATA LOADED SUCCESSFULLY")
        print("="*60)
        
        # Verify counts
        print(f"\nFinal counts:")
        print(f"  Action Codes: {ActionCode.query.count()}")
        print(f"  Institutions: {Institution.query.count()}")
        print(f"  Positions: {Position.query.count()}")
        print(f"  Actors: {Actor.query.count()}")
        print(f"  Tenures: {Tenure.query.count()}")

if __name__ == '__main__':
    main()