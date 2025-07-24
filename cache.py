import sqlite3
import os

CACHE_DB = "datasets/cache.db"

def init_cache():
    if not os.path.exists(CACHE_DB):
        conn = sqlite3.connect(CACHE_DB)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt TEXT,
                response TEXT,
                session_id TEXT
            )
        """)
        conn.commit()
        conn.close()

def get_cached_response(prompt, session_id=None):
    conn = sqlite3.connect(CACHE_DB)
    c = conn.cursor()
    if session_id:
        c.execute("SELECT response FROM cache WHERE prompt = ? AND session_id = ?", (prompt, session_id))
    else:
        c.execute("SELECT response FROM cache WHERE prompt = ?", (prompt,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def cache_response(prompt, response, session_id=None):
    conn = sqlite3.connect(CACHE_DB)
    c = conn.cursor()
    if session_id:
        c.execute("INSERT INTO cache (prompt, response, session_id) VALUES (?, ?, ?)", (prompt, response, session_id))
    else:
        c.execute("INSERT INTO cache (prompt, response) VALUES (?, ?)", (prompt, response))
    conn.commit()
    conn.close()
