import sqlite3

def init_db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)

    #Active le WAL (Write-Ahead Logging)
    conn.execute("PRAGMA journal_mode = WAL;")

    #Réduit la synchronisation disque pour moins de fsync
    conn.execute("PRAGMA synchronous = NORMAL;")
    
    conn.execute("""
      CREATE TABLE IF NOT EXISTS logs (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        time        TEXT,
        computer    TEXT,
        event_id    INTEGER,
        channel     TEXT,
        process_id  INTEGER,
        thread_id   INTEGER,
        level       INTEGER,
        message     TEXT
      );
    """)


    #Crée les index pour accélérer les filtres + tris
    conn.execute("CREATE INDEX IF NOT EXISTS idx_logs_time      ON logs(time);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_logs_event_id  ON logs(event_id);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_logs_level     ON logs(level);")
    # 4) Nouvelle table “rules”
    conn.execute("""
      CREATE TABLE IF NOT EXISTS rules (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        channel      TEXT    NOT NULL,
        event_id     INTEGER NOT NULL,
        threshold    INTEGER NOT NULL,
        window_min   INTEGER NOT NULL,
        last_checked TEXT
      );
    """)

    conn.execute("""
      CREATE TABLE IF NOT EXISTS alerts (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        rule_id      INTEGER NOT NULL,
        triggered_at TEXT    NOT NULL,
        count        INTEGER NOT NULL
      );
    """)
    conn.commit()
    return conn

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

def query_logs(conn, limit=None, offset=None, **filters):
    query = "SELECT * FROM logs WHERE 1=1"
    params = []

    # filtres existants
    for field, val in filters.items():
        if isinstance(val, str) and ('%' in val or '_' in val):
            query += f" AND {field} LIKE ?"
        else:
            query += f" AND {field} = ?"
        params.append(val)

    # ordonner du plus récent au plus ancien
    query += " ORDER BY time DESC"

    # pagination
    if limit is not None:
        query += " LIMIT ?"
        params.append(limit)
    if offset is not None:
        query += " OFFSET ?"
        params.append(offset)

    cur = conn.cursor()
    cur.execute(query, params)

    col_names = [d[0] for d in cur.description]
    rows = cur.fetchall()
    return [dict(zip(col_names, row)) for row in rows]



