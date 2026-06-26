import sqlite3
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import DATABASE_PATH, CXO_DATABASE

def get_db():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    # Create search history table
    c.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            results_count INTEGER DEFAULT 0,
            searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create CXO contacts table
    c.execute('''
        CREATE TABLE IF NOT EXISTS cxo_contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            title TEXT,
            company TEXT,
            email TEXT,
            linkedin TEXT,
            source TEXT DEFAULT 'database',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Seed CXO database if empty
    c.execute('SELECT COUNT(*) FROM cxo_contacts')
    count = c.fetchone()[0]
    
    if count == 0:
        for cxo in CXO_DATABASE:
            c.execute('''
                INSERT INTO cxo_contacts (name, title, company, linkedin, source)
                VALUES (?, ?, ?, ?, 'database')
            ''', (cxo['name'], cxo['title'], cxo['company'], cxo['linkedin']))
    
    conn.commit()
    conn.close()
    print(f"[DB] Initialized at {DATABASE_PATH}")

def log_search(company_name, results_count):
    conn = get_db()
    conn.execute(
        'INSERT INTO search_history (company_name, results_count) VALUES (?, ?)',
        (company_name, results_count)
    )
    conn.commit()
    conn.close()

def get_history(limit=20):
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM search_history ORDER BY searched_at DESC LIMIT ?', (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def search_cxo_in_db(company_name):
    conn = get_db()
    rows = conn.execute(
        '''SELECT * FROM cxo_contacts 
           WHERE LOWER(company) LIKE LOWER(?)
           ORDER BY title''',
        (f'%{company_name}%',)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
