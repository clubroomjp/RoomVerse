import sqlite3
import os

# Connect to the database
db_path = 'logs.sqlite'
if not os.path.exists(db_path):
    print(f"Database {db_path} not found.")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def add_column_if_not_exists(table, column, col_type):
    try:
        # Check if column exists
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [info[1] for info in cursor.fetchall()]
        
        if column not in columns:
            print(f"Adding column '{column}' to table '{table}'...")
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
            print(f"Column '{column}' added.")
        else:
            print(f"Column '{column}' already exists in table '{table}'.")
            
    except Exception as e:
        print(f"Error adding column '{column}': {e}")

# Add missing columns
add_column_if_not_exists('loreentry', 'keyword_en', 'VARCHAR')
add_column_if_not_exists('loreentry', 'content_en', 'VARCHAR')

conn.commit()

# Verify
cursor.execute("PRAGMA table_info(loreentry)")
print("Current columns:", [row[1] for row in cursor.fetchall()])

conn.close()
