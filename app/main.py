import os
import threading
import logging
from collectors.expcollect import logcollector
from data import database
from dashboard.server import run_server

# Chemin vers le fichier d'événements Windows (attention aux échappements)
LOG_FILE_PATH = r"C:\Windows\System32\winevt\Logs\Application.evtx"

# Chemin de la base de données
DB_PATH = "logs.db"

def start_log_collection(db_conn):
    logging.info("Lancement de la collecte des logs.")
    try:
        logs = logcollector(LOG_FILE_PATH, db_conn)  # en passant la connexion à la DB
        logging.info("Collecte terminée : %d logs collectés.", len(logs))
    except Exception as e:
        logging.error("Erreur lors de la collecte des logs : %s", e)

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logging.info("Démarrage de l'application SIEM.")

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        logging.info("Ancienne base de données supprimée.")
    else:
        logging.info("Aucune base de données existante trouvée.")

    # Créer une nouvelle connexion à la base de données
    db_conn = database.init_db(DB_PATH)

    # Lancer la collecte des logs dans un thread séparé en passant la connexion
    collector_thread = threading.Thread(target=start_log_collection, args=(db_conn,), daemon=True)
    collector_thread.start()

    # Démarrer le serveur du dashboard en passant la même connexion
    logging.info("Démarrage du serveur dashboard.")
    run_server(db_conn)

if __name__ == "__main__":
    main()
