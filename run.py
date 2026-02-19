import os
from dotenv import load_dotenv

# Load .env for local development only
if os.environ.get('FLASK_ENV') != 'production':
    from dotenv import load_dotenv
    load_dotenv()

from app import create_app

env = os.environ.get('FLASK_ENV', 'development')
app = create_app(env)

@app.cli.command('generate-synthetic')
def generate_synthetic_command():
    """Generate 105 synthetic events"""
    from generate_synthetic_events import generate_events, write_csv
    events = generate_events()
    write_csv(events)

@app.cli.command('import-events')
def import_events_command():
    """Import control frame events from CSV"""
    from import_events import load_control_frame_events
    load_control_frame_events()

if __name__ == '__main__':
    app.run(debug=True)