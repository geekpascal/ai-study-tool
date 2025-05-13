from app import create_app, db
from app.models.user import User
from flask_migrate import Migrate
import sqlalchemy as sa

app = create_app()
migrate = Migrate(app, db)

def upgrade_users_table():
    """Add new profile columns to the users table"""
    with app.app_context():
        # Create a connection
        connection = db.engine.connect()
        
        # Check which columns we need to add
        inspector = sa.inspect(db.engine)
        existing_columns = [col['name'] for col in inspector.get_columns('users')]
        
        # Add new columns if they don't exist
        if 'name' not in existing_columns:
            connection.execute(sa.text("ALTER TABLE users ADD COLUMN name VARCHAR(100)"))
            print("Added name column")
            
        if 'time_zone' not in existing_columns:
            connection.execute(sa.text("ALTER TABLE users ADD COLUMN time_zone VARCHAR(50) DEFAULT 'UTC'"))
            print("Added time_zone column")
            
        if 'study_goal' not in existing_columns:
            connection.execute(sa.text("ALTER TABLE users ADD COLUMN study_goal VARCHAR(200)"))
            print("Added study_goal column")
            
        if 'bio' not in existing_columns:
            connection.execute(sa.text("ALTER TABLE users ADD COLUMN bio VARCHAR(500)"))
            print("Added bio column")
            
        if 'last_login' not in existing_columns:
            connection.execute(sa.text("ALTER TABLE users ADD COLUMN last_login DATETIME"))
            print("Added last_login column")
            
        # Commit the transaction
        connection.commit()
        connection.close()
        
        print("Migration completed successfully!")

if __name__ == '__main__':
    print("Running database migrations...")
    upgrade_users_table() 