import sqlite3

def list_event_definitions(conn: sqlite3.Connection) -> list[dict]:
    """
    Renvoie [{event_id, name, description}, …]
    """
    cur = conn.execute("SELECT event_id, name, description FROM event_definitions")
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]

def get_event_definition(conn: sqlite3.Connection, event_id: int) -> dict | None:
    cur = conn.execute(
        "SELECT event_id, name, description FROM event_definitions WHERE event_id = ?",
        (event_id,)
    )
    row = cur.fetchone()
    if not row:
        return None
    cols = [c[0] for c in cur.description]
    return dict(zip(cols, row))