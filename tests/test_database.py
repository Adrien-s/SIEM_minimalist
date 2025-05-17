import sqlite3
from app.data.database import init_db


def test_init_db_creates_tables(db_conn):
    cur = db_conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cur.fetchall()}
    assert {'logs','rules','alerts','event_definitions'} <= tables

def test_event_definitions_seeded(db_conn):
    cur = db_conn.execute("SELECT COUNT(*) FROM event_definitions")
    count = cur.fetchone()[0]
    assert count >= 2  # on a inséré au moins 2 définitions
