import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List

DB_PATH = "C:/djfiore/data/agent_history.db"

def init_db():
    """Initialize SQLite DB."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mixes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            input_state TEXT,
            llm_output TEXT,
            tokens_used INTEGER,
            mix_success BOOLEAN
        )
    ''')
    conn.commit()
    conn.close()

def save_mix(input_state: Dict[str, Any], llm_output: Dict[str, Any], tokens_used: int = 0, mix_success: bool = False):
    """Save mix decision to DB."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO mixes (timestamp, input_state, llm_output, tokens_used, mix_success)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        datetime.now().isoformat(),
        json.dumps(input_state),
        json.dumps(llm_output),
        tokens_used,
        mix_success
    ))
    conn.commit()
    conn.close()

def get_history(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent mix history."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM mixes ORDER BY timestamp DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    history = []
    for row in rows:
        history.append({
            'id': row[0],
            'timestamp': row[1],
            'input_state': json.loads(row[2]),
            'llm_output': json.loads(row[3]),
            'tokens_used': row[4],
            'mix_success': bool(row[5])
        })
    return history

# Call init_db on import
init_db()
