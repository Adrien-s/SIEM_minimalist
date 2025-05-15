#A mettre en main.py une fois fonctionnel
import os
import signal
import sys
import logging
from queue import Queue

from data.database import init_db
from data.backlog_agent   import BacklogAgent
from data.tail_agent      import TailAgent
from data.db_writer  import DBWriter
from dashboard.server import run_server

#Nom du canal Windows à surveiller
LOG_CHANNEL = "Security"

#Chemin vers la base SQLite
DB_PATH = "logs.db"

def main():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")

    # recrée la base
    if os.path.exists(DB_PATH): os.remove(DB_PATH)
    db_conn = init_db(DB_PATH)

    event_queue = Queue()

    #Démarre le writer
    writer = DBWriter(queue=event_queue, db_conn=db_conn,
                      batch_size=100, flush_interval=0.5)
    writer.start()

    #Démarre l’agent historique
    backlog = BacklogAgent(channel=LOG_CHANNEL, queue=event_queue,
                           chunk_size=200, pause=0.2)
    backlog.start()

    #Démarre l’agent tail pour les nouveaux logs
    tail = TailAgent(channel=LOG_CHANNEL, queue=event_queue,
                     poll_interval=0.5)
    tail.start()

    #arrêt propre ctrl+c
    def shutdown(sig, frame):
        logging.info("Arrêt demandé…")
        backlog.join(0)  # on laisse backlog finir son historique
        tail.stop();    tail.join()
        writer.stop();  writer.join()
        sys.exit(0)
    signal.signal(signal.SIGINT, shutdown)

    # lance le dashboard
    run_server(db_conn)

if __name__ == "__main__":
    main()