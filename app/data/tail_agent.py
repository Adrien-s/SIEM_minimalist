import threading
import time
import logging
import win32evtlog

class TailAgent(threading.Thread):
    def __init__(self, channel: str, queue, poll_interval: float = 0.5):
        super().__init__(daemon=True)
        self.channel       = channel
        self.queue         = queue
        self.poll_interval = poll_interval
        self.handle        = win32evtlog.OpenEventLog(None, channel)
        self.flags         = win32evtlog.EVENTLOG_FORWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        # on commence au bout de l’historique, sinon on relira tout
        oldest          = win32evtlog.GetOldestEventLogRecord(self.handle)
        total           = win32evtlog.GetNumberOfEventLogRecords(self.handle)
        self.offset_rn  = oldest + total   # le prochain RN à lire
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        logging.info(f"[{self.channel}] TailAgent démarre")
        while not self._stop_event.is_set():
            events = win32evtlog.ReadEventLog(self.handle, self.flags, self.offset_rn)
            if events:
                for evt in events:
                    rec = {
                        "time":     evt.TimeGenerated.Format(),
                        "computer": evt.SourceName,
                        "event_id": evt.EventID & 0xFFFF,
                        "channel":  self.channel,
                        "level":    evt.EventType,
                        "message":  " | ".join(evt.StringInserts or [])
                    }
                    self.queue.put(rec)
                # advance RN by number of events read
                self.offset_rn += len(events)
            time.sleep(self.poll_interval)
        logging.info(f"[{self.channel}] TailAgent arrêté")