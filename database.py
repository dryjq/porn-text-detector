import sqlite3


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            status TEXT NOT NULL,
            model TEXT,
            priority INTEGER DEFAULT 10,
            attempts INTEGER DEFAULT 0,
            score REAL,
            is_porn INTEGER,
            message TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS seeds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT NOT NULL,
            last_scanned_at TEXT,
            created_at TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url_id INTEGER,
            event TEXT NOT NULL,
            payload TEXT,
            created_at TEXT,
            FOREIGN KEY(url_id) REFERENCES urls(id)
        )
        """
    )
    conn.commit()
