import threading
import time
from queue import Queue

class DBWriter(threading.Thread):
    def __init__(self, queue: Queue, db_conn, batch_size: int = 50, flush_interval: float = 0.5):
        """
        queue         : queue.Queue() dans laquelle les agents poussent les dicts d'événement
        db_conn       : sqlite3.Connection
        batch_size    : nombre max d'événements à insérer en un executemany
        flush_interval: intervalle (sec) pour flush même si batch pas plein
        """
        super().__init__(daemon=True)
        self.queue          = queue
        self.db_conn        = db_conn
        self.batch_size     = batch_size
        self.flush_interval = flush_interval
        self._stop_event    = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        cursor = self.db_conn.cursor()
        buffer = []
        last_flush = time.time()

        while not self._stop_event.is_set():
            try:
                # attend jusqu'à flush_interval pour récupérer au moins un événement
                evt = self.queue.get(timeout=self.flush_interval)
                buffer.append(evt)
            except Exception:
                #timeout 
                pass

            now = time.time()
            # 1)Si buffer plein _ou_ timeout écoulé
            if buffer and (len(buffer) >= self.batch_size or now - last_flush >= self.flush_interval):
                #Prépare les tuples pour executemany
                rows = [
                    (
                        e["time"],
                        e["computer"],
                        e["event_id"],
                        e["channel"],
                        e.get("process_id"),
                        e.get("thread_id"),
                        e["level"],
                        e.get("message", "")
                    )
                    for e in buffer
                ]
                cursor.executemany(
                    "INSERT INTO logs(time, computer, event_id, channel, process_id, thread_id, level, message) "
                    "VALUES (?,?,?,?,?,?,?,?)",
                    rows
                )
                self.db_conn.commit()
                buffer.clear()
                last_flush = now

        #a l’arrêt on vide le buffer
        if buffer:
            rows = [(
                e["time"], e["computer"], e["event_id"], e["channel"],
                e.get("process_id"), e.get("thread_id"), e["level"], e.get("message","")
            ) for e in buffer]
            cursor.executemany(
                "INSERT INTO logs(time, computer, event_id, channel, process_id, thread_id, level, message) "
                "VALUES (?,?,?,?,?,?,?,?)",
                rows
            )
            self.db_conn.commit()