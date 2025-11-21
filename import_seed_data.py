#!/usr/bin/env python3
"""
Global Narratives v1.1 - Database Import Script
================================================
Populates the database with seed data from CSV files.

CSV Files Required (in ./seed_data/ directory):
- institution_codes.csv
- position_codes.csv
- actor_codes.csv
- tenure_codes.csv

Usage:
    python import_seed_data.py          # Normal import
    python import_seed_data.py --clear  # Clear existing data first

Author: Global Narratives Project
Date: November 20, 2025
"""

import csv
import sys
import os
from datetime import datetime
from sqlalchemy import func

# Add parent directory to path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app, db
    from app.models import Institution, Position, Actor, Tenure
    
    # Create Flask application instance
    app = create_app()
    
except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    print("\nMake sure the 'app' package exists with __init__.py and models.py")
    print("Directory structure should be:")
    print("  project_root/")
    print("    ├── app/")
    print("    │   ├── __init__.py")
    print("    │   └── models.py")
    print("    ├── import_seed_data.py")
    print("    └── seed_data/\n")
    sys.exit(1)


class ImportError(Exception):
    """Custom exception for import errors"""
    pass


def parse_date(date_string):
    """
    Parse date from DD-MM-YY format to Python date object.
    Assumes all years are in 21st century (20XX).
    
    Args:
        date_string: Date in format "DD-MM-YY" (e.g., "21-01-25")
    
    Returns:
        datetime.date object or None if empty
    """
    if not date_string or date_string.strip() == '':
        return None
    
    try:
        # Parse DD-MM-YY format
        day, month, year = date_string.strip().split('-')
        # Convert 2-digit year to 4-digit (assume 20XX)
        full_year = 2000 + int(year)
        return datetime(full_year, int(month), int(day)).date()
    except (ValueError, AttributeError) as e:
        raise ImportError(f"Invalid date format '{date_string}'. Expected DD-MM-YY format (e.g., '21-01-25')")


def clean_value(value):
    """
    Clean CSV value by removing leading apostrophes and whitespace.
    
    Args:
        value: Raw string value from CSV
    
    Returns:
        Cleaned string or None if empty
    """
    if value is None:
        return None
    
    cleaned = str(value).lstrip("'").strip()
    return cleaned if cleaned else None


def validate_csv_files():
    """
    Validate that all required CSV files exist and have correct columns.
    
    Raises:
        ImportError: If any file is missing or has incorrect structure
    """
    print("\n" + "=" * 60)
    print("VALIDATING CSV FILES")
    print("=" * 60)
    
    required_files = {
        'institution_codes.csv': ['country_code', 'institution_name', 'institution_code', 
                                  'institution_layer', 'institution_type', 'institution_subtype_01'],
        'position_codes.csv': ['country_code', 'institution_code', 'position_code', 
                              'position_title', 'hierarchy_level'],
        'actor_codes.csv': ['actor_id', 'surname', 'given_name', 'middle_name', 'birth_year'],
        'tenure_codes.csv': ['actor_id', 'position_code', 'tenure_start', 'tenure_end', 'notes']
    }
    
    seed_data_dir = './seed_data'
    
    if not os.path.exists(seed_data_dir):
        raise ImportError(f"Directory '{seed_data_dir}' not found. Please create it and add CSV files.")
    
    for filename, required_cols in required_files.items():
        filepath = os.path.join(seed_data_dir, filename)
        
        if not os.path.exists(filepath):
            raise ImportError(f"File not found: {filepath}")
        
        # Check file has required columns
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            actual_cols = reader.fieldnames
            
            missing_cols = [col for col in required_cols if col not in actual_cols]
            if missing_cols:
                print(f"\n❌ {filename}")
                print(f"   Expected columns: {required_cols}")
                print(f"   Found columns: {list(actual_cols)}")
                print(f"   Missing: {missing_cols}")
                raise ImportError(f"{filename} missing columns: {missing_cols}")
        
        print(f"✓ {filename}")
    
    print("\nAll CSV files validated successfully!")


def import_institutions():
    """
    Import institutions from institution_codes.csv
    
    CSV Columns:
    - country_code
    - institution_name
    - institution_code
    - institution_layer
    - institution_type
    - institution_subtype_01
    """
    print("\n" + "=" * 60)
    print("IMPORTING INSTITUTIONS")
    print("=" * 60)
    
    filepath = './seed_data/institution_codes.csv'
    count = 0
    
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 (1 is header)
            try:
                country_code = clean_value(row['country_code'])
                institution_code = clean_value(row['institution_code'])
                
                # Prepend country code to institution_code to make it globally unique
                full_institution_code = f"{country_code}.{institution_code}"
                
                institution = Institution(
                    institution_code=full_institution_code,
                    institution_name=clean_value(row['institution_name']),
                    institution_type=clean_value(row['institution_type']),
                    institution_layer=clean_value(row['institution_layer']),
                    institution_subtype_01=clean_value(row['institution_subtype_01']),
                    country_code=country_code,
                    description=None  # Reserved for future use
                )
                
                db.session.add(institution)
                count += 1
                
            except Exception as e:
                raise ImportError(f"Error in {filepath} at row {row_num}: {str(e)}")
    
    db.session.commit()
    print(f"✓ Imported {count} institutions")
    return count


def import_positions():
    """
    Import positions from position_codes.csv
    
    CSV Columns:
    - country_code
    - institution_code (used to link to institutions)
    - position_code
    - position_title
    - hierarchy_level
    - description
    """
    print("\n" + "=" * 60)
    print("IMPORTING POSITIONS")
    print("=" * 60)
    
    filepath = './seed_data/position_codes.csv'
    count = 0
    
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        for row_num, row in enumerate(reader, start=2):
            try:
                # DEBUG: Print raw row data for first 2 rows
                if row_num <= 3:
                    print(f"\n=== ROW {row_num} RAW DATA ===")
                    print(f"All columns: {list(row.keys())}")
                    print(f"institution_name RAW: '{row['institution_name']}'")
                    print(f"institution_code RAW: '{row['institution_code']}'")
                
                country_code = clean_value(row['country_code'])
                institution_code = clean_value(row['institution_code'])
                
                # Prepend country code to match how institutions were stored
                full_institution_code = f"{country_code}.{institution_code}"
                
                if row_num <= 3:
                    print(f"Constructed full_institution_code: '{full_institution_code}'")
                
                # Verify institution exists
                institution = Institution.query.filter_by(institution_code=full_institution_code).first()
                if not institution:
                    # Print what institutions DO exist
                    sample_institutions = Institution.query.limit(3).all()
                    print(f"\nSample institutions in DB: {[i.institution_code for i in sample_institutions]}")
                    raise ImportError(f"Institution '{full_institution_code}' not found. Import institutions first.")
                
                position = Position(
                    position_code=clean_value(row['position_code']),
                    country_code=country_code,
                    institution_code=full_institution_code,
                    institution_name=clean_value(row['institution_name']),
                    position_title=clean_value(row['position_title']),
                    hierarchy_level=clean_value(row['hierarchy_level']),
                    description=clean_value(row.get('description'))  # May not exist in CSV
                )
                
                db.session.add(position)
                count += 1
                
            except Exception as e:
                raise ImportError(f"Error in {filepath} at row {row_num}: {str(e)}")
    
    db.session.commit()
    print(f"✓ Imported {count} positions")
    return count


def import_actors():
    """
    Import actors from actor_codes.csv
    
    CSV Columns:
    - actor_id
    - surname
    - given_name
    - middle_name (may be empty)
    - birth_year
    - position_code (reference only, imported to actors table)
    - position_title (reference only, imported to actors table)
    
    Note: position_code and position_title are stored in Actor model
    for quick reference to current primary position.
    """
    print("\n" + "=" * 60)
    print("IMPORTING ACTORS")
    print("=" * 60)
    
    filepath = './seed_data/actor_codes.csv'
    count = 0
    
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        for row_num, row in enumerate(reader, start=2):
            try:
                birth_year = clean_value(row['birth_year'])
                
                actor = Actor(
                    actor_id=clean_value(row['actor_id']),
                    surname=clean_value(row['surname']),
                    given_name=clean_value(row['given_name']),
                    middle_name=clean_value(row.get('middle_name')),  # May be empty
                    birth_year=int(birth_year) if birth_year else None,
                    position_code=clean_value(row.get('position_code')),  # Current position reference
                    position_title=clean_value(row.get('position_title')),  # Current position reference
                    biographical_info=None  # Reserved for future use
                )
                
                db.session.add(actor)
                count += 1
                
            except Exception as e:
                raise ImportError(f"Error in {filepath} at row {row_num}: {str(e)}")
    
    db.session.commit()
    print(f"✓ Imported {count} actors")
    return count


def import_tenures():
    """
    Import tenures from tenure_codes.csv
    
    CSV Columns:
    - actor_id
    - position_code
    - tenure_start (DD-MM-YY format)
    - tenure_end (DD-MM-YY format, empty for current holders)
    - notes
    """
    print("\n" + "=" * 60)
    print("IMPORTING TENURES")
    print("=" * 60)
    
    filepath = './seed_data/tenure_codes.csv'
    count = 0
    
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        for row_num, row in enumerate(reader, start=2):
            try:
                actor_id = clean_value(row['actor_id'])
                position_code = clean_value(row['position_code'])
                
                # Verify actor exists
                actor = Actor.query.filter_by(actor_id=actor_id).first()
                if not actor:
                    raise ImportError(f"Actor '{actor_id}' not found. Import actors first.")
                
                # Verify position exists
                position = Position.query.filter_by(position_code=position_code).first()
                if not position:
                    raise ImportError(f"Position '{position_code}' not found. Import positions first.")
                
                # Parse dates
                tenure_start = parse_date(clean_value(row['tenure_start']))
                tenure_end = parse_date(clean_value(row.get('tenure_end')))
                
                if not tenure_start:
                    raise ImportError(f"tenure_start is required but missing")
                
                tenure = Tenure(
                    actor_id=actor_id,
                    position_code=position_code,
                    tenure_start=tenure_start,
                    tenure_end=tenure_end,  # NULL for current holders
                    notes=clean_value(row.get('notes'))
                )
                
                db.session.add(tenure)
                count += 1
                
            except Exception as e:
                raise ImportError(f"Error in {filepath} at row {row_num}: {str(e)}")
    
    db.session.commit()
    print(f"✓ Imported {count} tenures")
    return count


def clear_database():
    """
    Clear all data from database tables.
    Use with caution!
    """
    print("\n" + "=" * 60)
    print("CLEARING DATABASE")
    print("=" * 60)
    
    with app.app_context():
        # Delete in reverse order of dependencies
        print("Deleting tenures...")
        Tenure.query.delete()
        
        print("Deleting actors...")
        Actor.query.delete()
        
        print("Deleting positions...")
        Position.query.delete()
        
        print("Deleting institutions...")
        Institution.query.delete()
        
        db.session.commit()
        print("✓ Database cleared")


def print_summary():
    """
    Print summary statistics after import.
    """
    print("\n" + "=" * 60)
    print("IMPORT SUMMARY")
    print("=" * 60)
    
    with app.app_context():
        institution_count = Institution.query.count()
        position_count = Position.query.count()
        actor_count = Actor.query.count()
        tenure_count = Tenure.query.count()
        
        # Count vacant positions (positions with no current tenure)
        current_tenures = Tenure.query.filter(Tenure.tenure_end.is_(None)).count()
        vacant_count = position_count - current_tenures
        
        print(f"\nDatabase Contents:")
        print(f"  Institutions:     {institution_count}")
        print(f"  Positions:        {position_count}")
        print(f"  Actors:           {actor_count}")
        print(f"  Tenures:          {tenure_count}")
        print(f"  Current tenures:  {current_tenures}")
        print(f"  Vacant positions: {vacant_count}")
        
        # Find actors holding multiple positions
        multiple_positions = db.session.query(
            Actor.actor_id, 
            Actor.surname, 
            Actor.given_name,
            func.count(Tenure.tenure_id).label('position_count')
        ).join(Tenure).filter(
            Tenure.tenure_end.is_(None)
        ).group_by(
            Actor.actor_id, Actor.surname, Actor.given_name
        ).having(
            func.count(Tenure.tenure_id) > 1
        ).all()
        
        if multiple_positions:
            print(f"\n  Actors holding multiple positions: {len(multiple_positions)}")
            for actor_id, surname, given_name, count in multiple_positions:
                print(f"    - {given_name} {surname} ({actor_id}): {count} positions")


def main():
    """
    Main import process.
    """
    print("\n" + "=" * 60)
    print("GLOBAL NARRATIVES v1.1 - DATABASE IMPORT")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check for --clear flag
    clear_first = '--clear' in sys.argv
    
    if clear_first:
        response = input("\n⚠️  WARNING: This will delete ALL existing data. Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Import cancelled.")
            sys.exit(0)
    
    try:
        # Step 1: Validate CSV files
        validate_csv_files()
        
        # Step 2: Clear database if requested
        if clear_first:
            with app.app_context():
                clear_database()
        
        # Step 3: Import data in correct order (respecting foreign keys)
        with app.app_context():
            import_institutions()
            import_positions()
            import_actors()
            import_tenures()
        
        # Step 4: Print summary
        print_summary()
        
        print("\n" + "=" * 60)
        print("✓ IMPORT COMPLETED SUCCESSFULLY")
        print("=" * 60 + "\n")
        
    except ImportError as e:
        print(f"\n❌ IMPORT FAILED")
        print(f"Error: {str(e)}")
        print("\nNo data was imported (transaction rolled back).\n")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\nNo data was imported (transaction rolled back).\n")
        sys.exit(1)


if __name__ == "__main__":
    main()