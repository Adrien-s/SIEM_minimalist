import threading
import time
import logging
import win32evtlog

class BacklogAgent(threading.Thread):
    def __init__(self, channel: str, queue, chunk_size: int = 100, pause: float = 0.1):
        super().__init__(daemon=True)
        self.channel    = channel
        self.queue      = queue
        self.chunk_size = chunk_size
        self.pause      = pause
        self.handle     = win32evtlog.OpenEventLog(None, channel)

    def run(self):
        logging.info(f"[{self.channel}] BacklogAgent démarre")
        oldest = win32evtlog.GetOldestEventLogRecord(self.handle)
        total  = win32evtlog.GetNumberOfEventLogRecords(self.handle)
        print(f"[{self.channel}] Backlog : {total} événements à lire")
        
        # RecordNumber du plus récent
        next_rn = oldest + total - 1     

        while next_rn >= oldest:
            try:
                flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEEK_READ
                events = win32evtlog.ReadEventLog(self.handle, flags, next_rn)
            except Exception as e:
                logging.warning(f"[{self.channel}] Backlog terminé ou erreur SEEK_READ : {e}")
                break

            if not events:
                logging.info(f"[{self.channel}] Plus d'événements historiques à lire.")
                break

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

            # on recule de len(events) dans l’historique
            next_rn -= len(events)
            time.sleep(self.pause)

        logging.info(f"[{self.channel}] BacklogAgent terminé")