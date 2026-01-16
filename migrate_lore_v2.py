import sqlite3
import os

DB_PATH = "logs.sqlite"

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found. Skipping migration.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check columns
    cursor.execute("PRAGMA table_info(loreentry)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Current columns: {columns}")

    # Add 'book'
    if 'book' not in columns:
        print("Adding 'book' column...")
        cursor.execute("ALTER TABLE loreentry ADD COLUMN book TEXT DEFAULT 'Default'")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_loreentry_book ON loreentry (book)")
    
    # Add 'secondary_keys'
    if 'secondary_keys' not in columns:
        print("Adding 'secondary_keys' column...")
        cursor.execute("ALTER TABLE loreentry ADD COLUMN secondary_keys TEXT")

    # Add 'constant'
    if 'constant' not in columns:
        print("Adding 'constant' column...")
        cursor.execute("ALTER TABLE loreentry ADD COLUMN constant BOOLEAN DEFAULT 0")

    # Add 'enabled'
    if 'enabled' not in columns:
        print("Adding 'enabled' column...")
        cursor.execute("ALTER TABLE loreentry ADD COLUMN enabled BOOLEAN DEFAULT 1")

    conn.commit()
    conn.close()
    print("Migration V2 completed.")

if __name__ == "__main__":
    migrate()
