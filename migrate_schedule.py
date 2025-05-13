from app import create_app, db
import sqlalchemy as sa

app = create_app()

def upgrade_schedules_table():
    """Add new fields to the schedules table"""
    with app.app_context():
        # Create a connection
        connection = db.engine.connect()
        
        # Check which columns we need to add
        inspector = sa.inspect(db.engine)
        existing_columns = [col['name'] for col in inspector.get_columns('schedules')]
        
        # Add new columns if they don't exist
        if 'title' not in existing_columns:
            connection.execute(sa.text("ALTER TABLE schedules ADD COLUMN title VARCHAR(100)"))
            print("Added title column")
            
        if 'description' not in existing_columns:
            connection.execute(sa.text("ALTER TABLE schedules ADD COLUMN description TEXT"))
            print("Added description column")
            
        if 'start_date' not in existing_columns:
            connection.execute(sa.text("ALTER TABLE schedules ADD COLUMN start_date DATE"))
            # Set default value to existing date column 
            connection.execute(sa.text("UPDATE schedules SET start_date = date"))
            print("Added start_date column")
            
        if 'end_date' not in existing_columns:
            connection.execute(sa.text("ALTER TABLE schedules ADD COLUMN end_date DATE"))
            # Set default value to existing date column
            connection.execute(sa.text("UPDATE schedules SET end_date = date"))
            print("Added end_date column")
            
        if 'is_active' not in existing_columns:
            connection.execute(sa.text("ALTER TABLE schedules ADD COLUMN is_active BOOLEAN DEFAULT 1"))
            print("Added is_active column")
            
        # Commit the transaction
        connection.commit()
        connection.close()
        
        print("Migration completed successfully!")

if __name__ == '__main__':
    print("Running schedule table migrations...")
    upgrade_schedules_table() 