from datetime import datetime
import sqlite3

def list_rules(conn: sqlite3.Connection) -> list[dict]:
    cur = conn.execute("""
      SELECT id, channel, event_id, threshold, window_min
        FROM rules
       ORDER BY id
    """)
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]

def add_rule(conn: sqlite3.Connection, channel: str, event_id: int,
             threshold: int, window_min: int) -> None:
    conn.execute("""
      INSERT INTO rules(channel, event_id, threshold, window_min)
           VALUES (?,?,?,?)
    """, (channel, event_id, threshold, window_min))
    conn.commit()

def update_rule(conn: sqlite3.Connection, rule_id: int, channel: str,
                event_id: int, threshold: int, window_min: int) -> None:
    conn.execute("""
      UPDATE rules
         SET channel=?, event_id=?, threshold=?, window_min=?
       WHERE id=?
    """, (channel, event_id, threshold, window_min, rule_id))
    conn.commit()

def delete_rule(conn: sqlite3.Connection, rule_id: int) -> None:
    conn.execute("DELETE FROM rules WHERE id=?", (rule_id,))
    conn.commit()