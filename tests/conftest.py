import pytest
from app.data.database import init_db


@pytest.fixture
def db_conn(tmp_path):
    # crée une DB temporaire
    db_file = tmp_path / "test.db"
    conn = init_db(str(db_file))  # importe init_db de database.py :contentReference[oaicite:0]{index=0}:contentReference[oaicite:1]{index=1}
    yield conn
    conn.close()
