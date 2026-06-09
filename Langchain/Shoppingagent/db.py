import sqlite3

conn = sqlite3.connect(
    "memory.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS conversations(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT,
    answer TEXT
)
""")

conn.commit()


def save_memory(question, answer):

    cursor.execute(
        """
        INSERT INTO conversations(
        question,
        answer
        )
        VALUES (?,?)
        """,
        (
            question,
            answer
        )
    )

    conn.commit()


def get_last_memories(limit=10):

    cursor.execute(
        """
        SELECT question,answer
        FROM conversations
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    )

    return cursor.fetchall()