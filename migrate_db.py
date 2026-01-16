import sqlite3

try:
    conn = sqlite3.connect('logs.sqlite')
    cursor = conn.cursor()
    # Add model column to ConversationLog
    # Check if exists first? Or just try/except
    cursor.execute("ALTER TABLE conversationlog ADD COLUMN model VARCHAR")
    conn.commit()
    print("Migration successful: Added model column to conversationlog.")
except Exception as e:
    print(f"Migration failed (maybe already exists?): {e}")

# Check image_path as well just in case (previous step)
try:
    conn = sqlite3.connect('logs.sqlite')
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE charactercard ADD COLUMN image_path VARCHAR")
    conn.commit()
    print("Migration successful: Added image_path column.")
except Exception as e:
    pass # Expected if already done

finally:
    if conn: conn.close()
