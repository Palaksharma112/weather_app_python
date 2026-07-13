import sqlite3

conn = sqlite3.connect("weather.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password BLOB NOT NULL
)
""")

conn.commit()
conn.close()

print("Database created successfully.")