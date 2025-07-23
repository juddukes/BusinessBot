import sqlite3
import hashlib

DB_FILE = "prompt_cache.db"

def init_cache():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cache (
        prompt_hash TEXT PRIMARY KEY,
        prompt TEXT,
        response TEXT
    )''')
    conn.commit()
    conn.close()

def get_cached_response(prompt):
    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT response FROM cache WHERE prompt_hash = ?", (prompt_hash,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def cache_response(prompt, response):
    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO cache (prompt_hash, prompt, response) VALUES (?, ?, ?)",
              (prompt_hash, prompt, response))
    conn.commit()
    conn.close()
