import sqlite3
import os

os.makedirs("data", exist_ok=True)

DB_PATH = "data/conversations.db"


def initialize_database():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_message TEXT,
        ai_response TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def save_conversation(user_message, ai_response):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO conversations
        (user_message, ai_response)
        VALUES (?,?)
        """,
        (user_message, ai_response)
    )

    conn.commit()
    conn.close()