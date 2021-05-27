import sqlite3
DATABASE_NAME = "prodscale.db"


def get_db():
    conn = sqlite3.connect(DATABASE_NAME)
    return conn


def create_tables():
    tables = [
        """CREATE TABLE IF NOT EXISTS prodscale(
                timestamp INTEGER PRIMARY KEY,
                model TEXT NOT NULL,
                answer TEXT NOT NULL,
                question TEXT NOT NULL,
				context TEXT NOT NULL)
            """
    ]
    db = get_db()
    cursor = db.cursor()
    for table in tables:
        cursor.execute(table)
