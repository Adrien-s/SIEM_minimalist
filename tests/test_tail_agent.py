import queue
from datetime import datetime
import win32evtlog
import pytest
from app.data.tail_agent import TailAgent

class DummyEvt:
    def __init__(self, time, source, eid, etype, inserts):
        self.TimeGenerated = time
        self.SourceName    = source
        self.EventID       = eid
        self.EventType     = etype
        self.StringInserts = inserts

def test_tail_agent_pushes_new_events(monkeypatch):
    now = datetime(2025,5,17,12,30,0)
    dummy = DummyEvt(now, 'HOST123', 0x10000 + 99, 4, ['alpha','beta'])
    calls = {'n': 0}

    # Patch Open/GetOldest/GetNumber to set initial offset
    monkeypatch.setattr(win32evtlog, 'OpenEventLog',    lambda srv, ch: 'HANDLE')
    monkeypatch.setattr(win32evtlog, 'GetOldestEventLogRecord', lambda h: 5)
    monkeypatch.setattr(win32evtlog, 'GetNumberOfEventLogRecords', lambda h: 5)

    def fake_ReadEventLog(handle, flags, offset):
        calls['n'] += 1
        # 1ère boucle renvoie l’événement + déclenche stop
        if calls['n'] == 1:
            agent._stop_event.set()
            return [dummy]
        # ensuite, on ne renvoie plus rien
        return []
    monkeypatch.setattr(win32evtlog, 'ReadEventLog', fake_ReadEventLog)

    q = queue.Queue()
    agent = TailAgent('Application', q, poll_interval=0)
    # On démarre run() (bloquant) : se stoppe rapidement car _stop_event set
    agent.run()

    rec = q.get_nowait()
    assert rec['computer'] == 'HOST123'
    assert rec['event_id']  == 99
    assert rec['channel']   == 'Application'
    assert rec['level']     == 4
    assert rec['message']   == 'alpha | beta'
    assert rec['time']      == now.isoformat()
