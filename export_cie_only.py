# export_cie_only.py

from app import create_app, db
from app.models import Event

app = create_app()

with app.app_context():
    events = Event.query.order_by(Event.event_date, Event.ordinal).all()
    
    with open('cie_descriptions.txt', 'w', encoding='utf-8') as f:
        for event in events:
            f.write(event.cie_description + "\n\n")
    
    print(f"Exported {len(events)} CIE descriptions to cie_descriptions.txt")