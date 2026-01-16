import sqlite3

try:
    conn = sqlite3.connect('logs.sqlite')
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE charactercard ADD COLUMN image_path VARCHAR")
    conn.commit()
    print("Migration successful: Added image_path column.")
except Exception as e:
    print(f"Migration failed (maybe already exists?): {e}")
finally:
    if conn: conn.close()
