#!/usr/bin/env python
"""Complete database reset with model verification"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def reset_database():
    try:
        print("🔧 Resetting database completely...")
        
        # Import app
        from app import app
        from apps.extensions import db
        
        with app.app_context():
            print("📋 Creating application context...")
            
            # Check if models import correctly
            try:
                from apps.user.models import User, Message, Notification
                print("✅ User, Message, Notification models imported successfully")
                
                # Check the User model has required fields
                if hasattr(User, 'id'):
                    print("✅ User model has id field")
                else:
                    print("❌ User model missing id field!")
                    return False
                    
                from apps.blog.models import Post  
                print("✅ Post model imported successfully")
            except Exception as e:
                print(f"❌ Model import error: {e}")
                return False
            
            # Delete the old database file completely
            print("🗑️  Removing old database file...")
            import os
            db_path = 'db/app.db'
            if os.path.exists(db_path):
                os.remove(db_path)
                print("✅ Old database file removed")
            
            # Create all tables from scratch
            print("🏗️  Creating all tables from scratch...")
            db.create_all()
            
            # Verify tables exist using proper SQLAlchemy method
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"✅ Created tables: {tables}")
            
            # Test User model by creating a user
            print("👤 Testing User model by creating admin user...")
            admin = User(
                username='admin',
                email='admin@example.com'
            )
            admin.set_password('admin123')
            
            # Test adding to session (this will fail if model is broken)
            db.session.add(admin)
            db.session.commit()
            
            print("✅ Admin user created successfully!")
            
            # Create your user
            user = User(
                username='Jermarcus', 
                email='jermarcuslewis4313@gmail.com'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            print("✅ Your user created successfully!")
            
            # Final verification
            user_count = User.query.count()
            print(f"✅ Total users in database: {user_count}")
            
            # Test messaging functionality
            print("💬 Testing messaging functionality...")
            test_message = Message(
                author=admin,
                recipient=user,
                body="Welcome to the messaging system!"
            )
            db.session.add(test_message)
            db.session.commit()
            print("✅ Test message created successfully!")
            
            print("🎉 Database reset completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error during reset: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if reset_database():
        print("\n🚀 Database is completely reset and ready!")
        print("Test by running: python app.py")
        print("\nLogin credentials:")
        print("- Username: admin, Password: admin123") 
        print("- Username: Jermarcus, Password: password123")
        print("\n💬 Messaging system is ready!")
        print("- Send messages between users")
        print("- Real-time notification badges")
    else:
        print("\n❌ Database reset failed!")
