import queue
from datetime import datetime
import win32evtlog
import pytest
from app.data.backlog_agent import BacklogAgent

class DummyEvt:
    def __init__(self, time, source, eid, etype, inserts):
        self.TimeGenerated = time
        self.SourceName    = source
        self.EventID       = eid
        self.EventType     = etype
        self.StringInserts = inserts

def test_backlog_agent_pushes_events(monkeypatch):
    # Prépare un événement dummy
    now = datetime(2025,5,17,12,0,0)
    dummy = DummyEvt(now, 'MACHINE01', 0x10000 + 42, 3, ['foo','bar'])
    calls = {'n': 0}

    # Patch des fonctions win32evtlog
    monkeypatch.setattr(win32evtlog, 'OpenEventLog',    lambda srv, ch: 'HANDLE')
    monkeypatch.setattr(win32evtlog, 'GetOldestEventLogRecord', lambda h: 1)
    monkeypatch.setattr(win32evtlog, 'GetNumberOfEventLogRecords', lambda h: 1)
    def fake_ReadEventLog(handle, flags, recnum):
        calls['n'] += 1
        return [dummy] if calls['n']==1 else []
    monkeypatch.setattr(win32evtlog, 'ReadEventLog', fake_ReadEventLog)

    q = queue.Queue()
    agent = BacklogAgent('Security', q, chunk_size=1, pause=0)
    # On exécute synchronement run()
    agent.run()

    rec = q.get_nowait()
    assert rec['computer'] == 'MACHINE01'
    assert rec['event_id']  == 42        # 0x10000 & 0xFFFF
    assert rec['channel']   == 'Security'
    assert rec['level']     == 3
    assert rec['message']   == 'foo | bar'
    # time au format ISO
    assert rec['time']      == now.isoformat()
