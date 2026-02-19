from app import db, create_app
from app.models import ControlFrame
import csv
from datetime import datetime

def load_control_frame_events():
    """Load control frame events from CSV"""
    print("\n=== Loading Control Frame Events ===")
    
    filepath = 'seed_data/synthetic_events.csv'
    
    count = 0
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            subjects = row.get('identified_subjects', '').split(',') if row.get('identified_subjects') else []
            objects = row.get('identified_objects', '').split(',') if row.get('identified_objects') else []
            
            subjects = [s.strip() for s in subjects if s.strip()]
            objects = [o.strip() for o in objects if o.strip()]
            
            rec_timestamp = datetime.strptime(row['rec_timestamp'], '%Y-%m-%d %H:%M:%S')
            
            cf = ControlFrame(
                event_code=row['event_code'],
                rec_timestamp=rec_timestamp,
                event_actor=row['event_actor'],
                action_code=row['action_code'],
                action_type=row['action_type'],
                rel_cred=row['rel_cred'],
                cie_body=row['cie_body'],
                identified_subjects=subjects,
                identified_objects=objects,
                source_article_id=int(row['source_article_id']) if row.get('source_article_id') else None
            )
            db.session.add(cf)
            count += 1
    
    db.session.commit()
    print(f"✓ Loaded {count} control frame events")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        load_control_frame_events()
        print(f"Total events in database: {ControlFrame.query.count()}")