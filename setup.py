#!/usr/bin/env python3
"""
Global Narratives System - Database Setup Script
Initializes database and creates test data
"""

import os
import sys
from datetime import date

def setup_database():
    """Initialize database and create test data"""
    
    # Import after ensuring we're in the right directory
    from app import create_app, db
    from app.models import Institution, Position, Actor, Tenure
    
    print("="*70)
    print(" Global Narratives System v1.0 - Database Setup")
    print("="*70)
    
    # Create Flask app
    print("\n[1/5] Creating Flask application...")
    try:
        app = create_app('development')
        print("✓ Flask app created successfully")
    except Exception as e:
        print(f"✗ Failed to create Flask app: {e}")
        return False
    
    with app.app_context():
        # Drop existing tables
        print("\n[2/5] Dropping existing tables (if any)...")
        try:
            db.drop_all()
            print("✓ Existing tables dropped")
        except Exception as e:
            print(f"✗ Warning: {e}")
        
        # Create all tables
        print("\n[3/5] Creating database tables...")
        try:
            db.create_all()
            print("✓ Database tables created:")
            print("  - articles")
            print("  - institutions")
            print("  - positions")
            print("  - actors")
            print("  - events")
            print("  - tenures")
            print("  - event_actors")
        except Exception as e:
            print(f"✗ Failed to create tables: {e}")
            return False
        
        # Create test data
        print("\n[4/5] Creating test data...")
        
        try:
            # Institutions
            print("  Creating institutions...")
            institutions = [
                Institution(
                    institution_code='usa.gov',
                    institution_name='United States Government',
                    institution_type='Government',
                    country_code='usa',
                    description='Federal government of the United States of America'
                ),
                Institution(
                    institution_code='gbr.gov',
                    institution_name='United Kingdom Government',
                    institution_type='Government',
                    country_code='gbr',
                    description='Her Majesty\'s Government of the United Kingdom'
                ),
                Institution(
                    institution_code='jpn.gov',
                    institution_name='Government of Japan',
                    institution_type='Government',
                    country_code='jpn',
                    description='Government of Japan'
                ),
                Institution(
                    institution_code='fra.gov',
                    institution_name='Government of France',
                    institution_type='Government',
                    country_code='fra',
                    description='Government of the French Republic'
                ),
                Institution(
                    institution_code='deu.gov',
                    institution_name='Government of Germany',
                    institution_type='Government',
                    country_code='deu',
                    description='Federal Government of Germany'
                )
            ]
            
            for inst in institutions:
                db.session.add(inst)
            
            db.session.commit()
            print(f"  ✓ Created {len(institutions)} institutions")
            
            # Positions
            print("  Creating positions...")
            positions = [
                Position(
                    position_code='usa.hos',
                    position_title='President of the United States',
                    institution_code='usa.gov',
                    hierarchy_level='hos',
                    description='Head of State and Head of Government'
                ),
                Position(
                    position_code='gbr.hog',
                    position_title='Prime Minister of the United Kingdom',
                    institution_code='gbr.gov',
                    hierarchy_level='hog',
                    description='Head of Government'
                ),
                Position(
                    position_code='jpn.hog',
                    position_title='Prime Minister of Japan',
                    institution_code='jpn.gov',
                    hierarchy_level='hog',
                    description='Head of Government'
                ),
                Position(
                    position_code='fra.hos',
                    position_title='President of France',
                    institution_code='fra.gov',
                    hierarchy_level='hos',
                    description='Head of State'
                ),
                Position(
                    position_code='deu.hog',
                    position_title='Chancellor of Germany',
                    institution_code='deu.gov',
                    hierarchy_level='hog',
                    description='Head of Government'
                )
            ]
            
            for pos in positions:
                db.session.add(pos)
            
            db.session.commit()
            print(f"  ✓ Created {len(positions)} positions")
            
            # Actors
            print("  Creating actors...")
            actors = [
                Actor(
                    actor_id='usa.1942.0001',
                    surname='Biden',
                    given_name='Joseph',
                    middle_name='Robinette',
                    biographical_info='46th President of the United States (2021-2025)'
                ),
                Actor(
                    actor_id='gbr.1965.0001',
                    surname='Starmer',
                    given_name='Keir',
                    middle_name='Rodney',
                    biographical_info='Prime Minister of the United Kingdom (2024-present)'
                ),
                Actor(
                    actor_id='jpn.1957.0001',
                    surname='Kishida',
                    given_name='Fumio',
                    middle_name='',
                    biographical_info='Prime Minister of Japan (2021-2024)'
                ),
                Actor(
                    actor_id='fra.1977.0001',
                    surname='Macron',
                    given_name='Emmanuel',
                    middle_name='Jean-Michel',
                    biographical_info='President of France (2017-present)'
                ),
                Actor(
                    actor_id='deu.1954.0001',
                    surname='Scholz',
                    given_name='Olaf',
                    middle_name='',
                    biographical_info='Chancellor of Germany (2021-present)'
                )
            ]
            
            for actor in actors:
                db.session.add(actor)
            
            db.session.commit()
            print(f"  ✓ Created {len(actors)} actors")
            
            # Tenures
            print("  Creating tenures...")
            tenures = [
                Tenure(
                    actor_id='usa.1942.0001',
                    position_code='usa.hos',
                    tenure_start=date(2021, 1, 20),
                    tenure_end=date(2025, 1, 20)
                ),
                Tenure(
                    actor_id='gbr.1965.0001',
                    position_code='gbr.hog',
                    tenure_start=date(2024, 7, 5),
                    tenure_end=None  # Current
                ),
                Tenure(
                    actor_id='jpn.1957.0001',
                    position_code='jpn.hog',
                    tenure_start=date(2021, 10, 4),
                    tenure_end=date(2024, 10, 1)
                ),
                Tenure(
                    actor_id='fra.1977.0001',
                    position_code='fra.hos',
                    tenure_start=date(2017, 5, 14),
                    tenure_end=None  # Current
                ),
                Tenure(
                    actor_id='deu.1954.0001',
                    position_code='deu.hog',
                    tenure_start=date(2021, 12, 8),
                    tenure_end=None  # Current
                )
            ]
            
            for tenure in tenures:
                db.session.add(tenure)
            
            db.session.commit()
            print(f"  ✓ Created {len(tenures)} tenures")
            
        except Exception as e:
            print(f"  ✗ Failed to create test data: {e}")
            db.session.rollback()
            return False
        
        # Verify
        print("\n[5/5] Verifying database...")
        try:
            inst_count = Institution.query.count()
            pos_count = Position.query.count()
            actor_count = Actor.query.count()
            tenure_count = Tenure.query.count()
            
            print(f"  ✓ Institutions: {inst_count}")
            print(f"  ✓ Positions: {pos_count}")
            print(f"  ✓ Actors: {actor_count}")
            print(f"  ✓ Tenures: {tenure_count}")
            
        except Exception as e:
            print(f"  ✗ Verification failed: {e}")
            return False
    
    print("\n" + "="*70)
    print(" Setup Complete!")
    print("="*70)
    print("\nTest Data Summary:")
    print("  • 5 Institutions (USA, UK, Japan, France, Germany)")
    print("  • 5 Positions (Presidents/Prime Ministers/Chancellor)")
    print("  • 5 Actors (Biden, Starmer, Kishida, Macron, Scholz)")
    print("  • 5 Tenures (3 current, 2 ended)")
    print("\nNext Steps:")
    print("  1. Run: python run.py")
    print("  2. Visit: http://localhost:5000")
    print("  3. Navigate to: Articles, Events, Actors, Positions, Institutions")
    print("\n" + "="*70)
    
    return True


if __name__ == '__main__':
    try:
        success = setup_database()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)