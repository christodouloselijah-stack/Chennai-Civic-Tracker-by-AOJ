import sqlite3
import os

def migrate():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tracker.db')
    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if 'type' column exists
    cursor.execute("PRAGMA table_info(civic_updates)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'type' not in columns:
        print("Adding 'type' column to civic_updates...")
        cursor.execute("ALTER TABLE civic_updates ADD COLUMN type VARCHAR DEFAULT 'civic'")
        conn.commit()
    else:
        print("'type' column already exists.")
        
    if 'category' not in columns:
        print("Adding 'category' column to civic_updates...")
        cursor.execute("ALTER TABLE civic_updates ADD COLUMN category VARCHAR")
        conn.commit()
    else:
        print("'category' column already exists.")
        
    # Update any null type to 'civic'
    cursor.execute("UPDATE civic_updates SET type = 'civic' WHERE type IS NULL")
    conn.commit()
    
    print("Database migration complete.")
    conn.close()

if __name__ == '__main__':
    migrate()
