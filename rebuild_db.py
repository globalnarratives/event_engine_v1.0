#!/usr/bin/env python3
"""
Rebuild Database Schema
========================
Drops all tables and recreates them based on current models.py

WARNING: This will delete ALL data in the database!

Usage:
    python rebuild_db.py
"""

from app import create_app, db

app = create_app()

with app.app_context():
    print("Dropping all tables...")
    db.drop_all()
    print("✓ All tables dropped")
    
    print("\nCreating all tables from models.py...")
    db.create_all()
    print("✓ All tables created")
    
    print("\n✓ Database schema rebuilt successfully!")
    print("You can now run: python import_seed_data.py --clear")