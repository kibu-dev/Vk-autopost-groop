import sqlite3

DB_NAME = "bot_posts.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Опубликованные посты
    cur.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        post_id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        publish_date TEXT NOT NULL,
        is_anonymous INTEGER DEFAULT 0,
        post_text TEXT
    )
    """)

    # Логи действий
    cur.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        action TEXT NOT NULL,
        post_id INTEGER,
        action_date TEXT NOT NULL
    )
    """)

    # Ограничения пользователей
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_limits (
        user_id INTEGER PRIMARY KEY,
        daily_posts INTEGER DEFAULT 0,
        last_post_date TEXT,
        warning_count INTEGER DEFAULT 0,
        is_blocked INTEGER DEFAULT 0,
        block_until TEXT
    )
    """)

    # Черный список
    cur.execute("""
    CREATE TABLE IF NOT EXISTS blacklist (
        user_id INTEGER PRIMARY KEY,
        reason TEXT,
        blocked_date TEXT
    )
    """)

    # История публикаций для поиска дублей
    cur.execute("""
    CREATE TABLE IF NOT EXISTS post_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        post_hash TEXT NOT NULL,
        post_date TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


def execute(query, params=()):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(query, params)

    conn.commit()
    conn.close()


def fetchone(query, params=()):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(query, params)
    row = cur.fetchone()

    conn.close()
    return row


def fetchall(query, params=()):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(query, params)
    rows = cur.fetchall()

    conn.close()
    return rows
