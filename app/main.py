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

#Nom des canal Windows à surveiller
CHANNELS = ["Security", "Application"]  

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

    backlog_agents = []
    tail_agents    = []
    for chan in CHANNELS:
        # Agent historique
        ba = BacklogAgent(
            channel=chan,
            queue=event_queue,
            chunk_size=200,
            pause=0.2
        )
        ba.start()
        backlog_agents.append(ba)
        logging.info("BacklogAgent démarré sur canal %s.", chan)

        # Agent tail 
        ta = TailAgent(
            channel=chan,
            queue=event_queue,
            poll_interval=0.5
        )
        ta.start()
        tail_agents.append(ta)
        logging.info("TailAgent démarré sur canal %s.", chan)

    #arrêt propre ctrl+c
    def shutdown(sig, frame):
        logging.info("Arrêt demandé…")
        # Laisser les backlogAgents finir au plus vite
        for ba in backlog_agents:
            ba.join(0)
            
        # Stop et join des tailAgents 
        for ta in tail_agents:
            ta.stop()
            ta.join()
        # Stop et join du writer
        writer.stop()
        writer.join()
        sys.exit(0)
    signal.signal(signal.SIGINT, shutdown)

    # lance le dashboard
    run_server(db_conn)

if __name__ == "__main__":
    main()