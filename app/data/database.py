import sqlite3

def init_db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)

    #Active le WAL (Write-Ahead Logging)
    conn.execute("PRAGMA journal_mode = WAL;")

    #Réduit la synchronisation disque pour moins de fsync
    conn.execute("PRAGMA synchronous = NORMAL;")

    #Crée la table logs si nécessaire
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

def query_logs(dbinitialisation, limit=None, offset=None, **filters):
    query = "SELECT * FROM logs WHERE 1=1"
    params = []
    for field, val in filters.items():
        if isinstance(val, str) and ('%' in val or '_' in val):
            query += f" AND {field} LIKE ?"
        else:
            query += f" AND {field} = ?"
        params.append(val)


    cursor = dbinitialisation.cursor()
    cursor.execute(query, params)

    # Récupère les noms de colonne
    col_names = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    #Pour chaque ligne, créer un dict
    results = []
    for row in rows:
        # si c'est déjà un Row, on peut aussi faire row[col] mais zip marche pour les deux
        results.append(dict(zip(col_names, row)))
    return results


