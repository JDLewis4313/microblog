#!/usr/bin/env python
"""Force fix database with current model"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def force_fix():
    print("🔧 Force fixing database...")
    
    # Remove ALL database files
    db_files = ['db/app.db', 'instance/app.db', 'app.db']
    for db_file in db_files:
        if os.path.exists(db_file):
            os.remove(db_file)
            print(f"🗑️  Removed {db_file}")
    
    # Import and create fresh
    from app import app
    from apps.extensions import db
    from apps.user.models import User, Message, Notification
    from apps.blog.models import Post
    
    with app.app_context():
        print("🏗️  Creating fresh database from current models...")
        
        # Create all tables from current model definitions
        db.create_all()
        
        # Verify the user table has the correct structure
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        user_columns = [col['name'] for col in inspector.get_columns('user')]
        print(f"📋 User table columns: {user_columns}")
        
        if 'last_message_read_time' not in user_columns:
            print("❌ Still missing last_message_read_time!")
            return False
        
        print("✅ All columns present!")
        
        # Create test users
        admin = User(username='admin', email='admin@example.com')
        admin.set_password('admin123')
        
        user = User(username='Jermarcus', email='jermarcuslewis4313@gmail.com')
        user.set_password('password123')
        
        db.session.add(admin)
        db.session.add(user)
        db.session.commit()
        
        print("✅ Users created!")
        
        # Test messaging
        msg = Message(author=admin, recipient=user, body="Test message!")
        db.session.add(msg)
        db.session.commit()
        
        print("✅ Test message created!")
        print("🎉 Database is ready!")
        return True

if __name__ == "__main__":
    if force_fix():
        print("\n🚀 Success! Your database is ready!")
        print("Run: python app.py")
    else:
        print("\n❌ Fix failed!")
