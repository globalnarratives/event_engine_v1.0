"""
One-time migration: Backfill parent_institution_code and reports_to_position_code
from the CSV seed data into the existing database.

Run once: python backfill_hierarchy.py
"""

from app import db, create_app
from app.models import Institution, Position
import csv

def backfill_institutions():
    """Read parent_institution_code from CSV and update existing institutions."""
    print("\n=== Backfilling Institution Parent Links ===")
    filepath = 'seed_data/institution_codes.csv'

    parent_map = {}
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            parent_code = row.get('parent_institution_code', '').strip()
            if parent_code:
                parent_map[row['institution_code']] = parent_code

    print(f"  CSV has {len(parent_map)} institutions with parent codes")

    updated = 0
    skipped_self = 0
    skipped_missing_parent = 0
    skipped_missing_inst = 0

    for inst_code, parent_code in parent_map.items():
        # Skip self-references
        if inst_code == parent_code:
            skipped_self += 1
            continue

        # Check parent exists
        parent = Institution.query.filter_by(institution_code=parent_code).first()
        if not parent:
            skipped_missing_parent += 1
            print(f"  WARN: Parent '{parent_code}' not found for '{inst_code}'")
            continue

        inst = Institution.query.filter_by(institution_code=inst_code).first()
        if not inst:
            skipped_missing_inst += 1
            continue

        inst.parent_institution_code = parent_code
        updated += 1

    db.session.commit()
    print(f"  Updated: {updated}")
    print(f"  Skipped (self-ref): {skipped_self}")
    print(f"  Skipped (parent not in DB): {skipped_missing_parent}")
    print(f"  Skipped (institution not in DB): {skipped_missing_inst}")


def backfill_positions():
    """Read reports_to_position_code from CSV and update existing positions."""
    print("\n=== Backfilling Position Reporting Links ===")
    filepath = 'seed_data/position_codes.csv'

    reports_map = {}
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            reports_to = row.get('reports_to_position_code', '').strip()
            if reports_to:
                reports_map[row['position_code']] = reports_to

    print(f"  CSV has {len(reports_map)} positions with reports_to codes")

    updated = 0
    skipped_self = 0
    skipped_missing_target = 0
    skipped_missing_pos = 0

    for pos_code, reports_to in reports_map.items():
        # Skip self-references
        if pos_code == reports_to:
            skipped_self += 1
            print(f"  WARN: Self-reference skipped for '{pos_code}'")
            continue

        # Check target position exists
        target = Position.query.filter_by(position_code=reports_to).first()
        if not target:
            skipped_missing_target += 1
            print(f"  WARN: Target position '{reports_to}' not found for '{pos_code}'")
            continue

        pos = Position.query.filter_by(position_code=pos_code).first()
        if not pos:
            skipped_missing_pos += 1
            continue

        pos.reports_to_position_code = reports_to
        updated += 1

    db.session.commit()
    print(f"  Updated: {updated}")
    print(f"  Skipped (self-ref): {skipped_self}")
    print(f"  Skipped (target not in DB): {skipped_missing_target}")
    print(f"  Skipped (position not in DB): {skipped_missing_pos}")


def verify():
    """Print summary counts after backfill."""
    print("\n=== Verification ===")
    total_inst = Institution.query.count()
    with_parent = Institution.query.filter(Institution.parent_institution_code.isnot(None)).count()
    print(f"  Institutions: {with_parent}/{total_inst} have parent_institution_code")

    total_pos = Position.query.count()
    with_reports = Position.query.filter(Position.reports_to_position_code.isnot(None)).count()
    print(f"  Positions: {with_reports}/{total_pos} have reports_to_position_code")


def main():
    app = create_app()
    with app.app_context():
        print("=" * 60)
        print("BACKFILLING HIERARCHY DATA")
        print("=" * 60)

        backfill_institutions()
        backfill_positions()
        verify()

        print("\n" + "=" * 60)
        print("BACKFILL COMPLETE")
        print("=" * 60)


if __name__ == '__main__':
    main()
