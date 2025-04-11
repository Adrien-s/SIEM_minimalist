import sqlite3

def init_db(db_path="logs.db"):
    dbinitialisation = sqlite3.connect(db_path, check_same_thread=False)
    # Configure pour renvoyer des dictionnaires via Row Factory
    dbinitialisation.row_factory = sqlite3.Row
    cursor = dbinitialisation.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT,
            computer TEXT,
            event_id TEXT,
            channel TEXT,
            process_id TEXT,
            thread_id TEXT,
            level TEXT
        )
    ''')
    dbinitialisation.commit()
    return dbinitialisation

def insert_log(dbinitialisation, log):
    cursor = dbinitialisation.cursor()
    cursor.execute('''
        INSERT INTO logs (time, computer, event_id, channel, process_id, thread_id, level)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        log["time"],
        log["computer"],
        log["event_id"],
        log["channel"],
        log["process_id"],
        log["thread_id"],
        log["level"]
    ))
    dbinitialisation.commit()

def query_logs(dbinitialisation, limit=None, offset=None, **filters):
    query = "SELECT * FROM logs WHERE 1=1"
    params = []
    if 'level' in filters:
        query += " AND level = ?"
        params.append(filters['level'])
    query += " ORDER BY id ASC"
    if limit is not None:
        query += " LIMIT ?"
        params.append(limit)
    if offset is not None:
        query += " OFFSET ?"
        params.append(offset)
    cursor = dbinitialisation.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    # Convertir chaque ligne en dictionnaire
    return [dict(row) for row in rows]
