import sqlite3
import bcrypt

DB_NAME = "weather.db"


# ===========================
# Database Connection
# ===========================
def create_connection():
    return sqlite3.connect(DB_NAME)


# ===========================
# Create Users Table
# ===========================
def create_table():
    conn = create_connection()
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


# Create table automatically
create_table()


# ===========================
# Signup
# ===========================
def signup(name, email, password):

    conn = create_connection()
    cursor = conn.cursor()

    try:
        # Check if email already exists
        cursor.execute(
            "SELECT id FROM users WHERE email=?",
            (email,)
        )

        if cursor.fetchone():
            return False

        # Hash password
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        cursor.execute(
            """
            INSERT INTO users(name, email, password)
            VALUES(?,?,?)
            """,
            (name, email, hashed_password)
        )

        conn.commit()

        return True

    except Exception as e:
        print("Signup Error:", e)
        return False

    finally:
        conn.close()


# ===========================
# Login
# ===========================
def login(email, password):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id,name,email,password
        FROM users
        WHERE email=?
        """,
        (email,)
    )

    user = cursor.fetchone()

    conn.close()

    if user is None:
        return None

    stored_password = user[3]

    # If SQLite returns string instead of bytes
    if isinstance(stored_password, str):
        stored_password = stored_password.encode("utf-8")

    if bcrypt.checkpw(
        password.encode("utf-8"),
        stored_password
    ):
        return user

    return None


# ===========================
# Get User by Email
# ===========================
def get_user(email):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id,name,email
        FROM users
        WHERE email=?
        """,
        (email,)
    )

    user = cursor.fetchone()

    conn.close()

    return user


# ===========================
# Change Password
# ===========================
def change_password(email, new_password):

    conn = create_connection()
    cursor = conn.cursor()

    hashed_password = bcrypt.hashpw(
        new_password.encode("utf-8"),
        bcrypt.gensalt()
    )

    cursor.execute(
        """
        UPDATE users
        SET password=?
        WHERE email=?
        """,
        (hashed_password, email)
    )

    conn.commit()
    conn.close()

    return True