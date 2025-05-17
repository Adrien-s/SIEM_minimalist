import pytest
import datetime as dt
from datetime import timedelta
import app.data.rules_engine as re_module

# Helpers pour insérer en base
def insert_rule(conn, channel, event_id, threshold, window_min):
    cur = conn.execute(
        "INSERT INTO rules(channel,event_id,threshold,window_min) VALUES (?,?,?,?)",
        (channel, event_id, threshold, window_min)
    )
    conn.commit()
    return cur.lastrowid

def insert_log(conn, **fields):
    cols, vals = zip(*fields.items())
    q = f"INSERT INTO logs({','.join(cols)}) VALUES ({','.join('?'*len(vals))})"
    conn.execute(q, vals)
    conn.commit()

# Classe factice pour piloter datetime.utcnow()  
class FakeDateTime:
    @classmethod
    def now(cls):
        return cls._now

    @staticmethod
    def timedelta(**kwargs):
        return timedelta(**kwargs)

    @staticmethod
    def fromisoformat(timestr: str):
        return dt.datetime.fromisoformat(timestr)

@pytest.fixture(autouse=True)
def patch_datetime(monkeypatch):
    # On remplace datetime (du module rules_engine) par FakeDateTime
    monkeypatch.setattr(re_module, 'datetime', FakeDateTime)
    yield

def test_evaluate_rules_triggers(db_conn):
    # 1) Définir "now" contrôlé
    fake_now = dt.datetime(2025, 5, 17, 12, 0, 0)
    FakeDateTime._now = fake_now

    # 2) Créer la règle (threshold=2 en 10min)
    rid = insert_rule(db_conn, 'Test', 1234, threshold=2, window_min=10)

    # 3) Insérer deux logs à fake_now - 5min
    t0 = (fake_now - timedelta(minutes=5)).isoformat()
    insert_log(db_conn,
        time=t0, computer='pc1', event_id=1234,
        channel='Test', level=1
    )
    insert_log(db_conn,
        time=t0, computer='pc1', event_id=1234,
        channel='Test', level=1
    )

    # Exécuter le moteur de règles
    re_module.evaluate_rules(db_conn)

    # Vérifier qu'une alerte a bien été créée
    cnt = db_conn.execute(
        "SELECT COUNT(*) FROM alerts WHERE rule_id=?",
        (rid,)
    ).fetchone()[0]
    assert cnt == 1

def test_evaluate_rules_no_trigger(db_conn):
    # Now fixe
    fake_now = dt.datetime(2025, 5, 17, 12, 0, 0)
    FakeDateTime._now = fake_now

    # Règle seuil trop élevé pour 1 seul log
    rid = insert_rule(db_conn, 'Test', 1234, threshold=5, window_min=10)

    # Un seul log hors seuil
    t0 = (fake_now - timedelta(minutes=5)).isoformat()
    insert_log(db_conn,
        time=t0, computer='pc1', event_id=1234,
        channel='Test', level=1
    )

    re_module.evaluate_rules(db_conn)

    cnt = db_conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
    assert cnt == 0
