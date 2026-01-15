from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

app = create_app(os.environ.get('FLASK_ENV', 'development'))

with app.app_context():
    # Check if admin already exists
    admin = User.query.filter_by(email='editor@mondium.org').first()
    
    if admin:
        print("Admin user already exists!")
    else:
        # Create admin user
        admin = User(
            username='editor',
            email='editor@mondium.org',
            password_hash=generate_password_hash('59Danderson&'),
            role='admin',
            is_active=True
        )
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"Admin user created successfully!")
        print(f"Email: {admin.email}")
        print(f"Username: {admin.username}")
        print(f"Role: {admin.role}")