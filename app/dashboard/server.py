import http.server
import socketserver
import json
import os
from data import database  # import de vos fonctions de gestion de DB

def run_server(db_conn):
    PORT = 8000

    # Définir le répertoire pour les fichiers statiques du dashboard
    template_dir = os.path.join(os.getcwd(), "dashboard", "template")
    if os.path.isdir(template_dir):
        os.chdir(template_dir)
        print("Répertoire de travail changé vers :", os.getcwd())
    else:
        print("Le répertoire template n'a pas été trouvé :", template_dir)

    class MyHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path.startswith('/data'):
                # Récupération des logs depuis la base SQLite via la connexion passée
                logs = database.query_logs(db_conn)
                response = {"events": logs}
                json_data = json.dumps(response)
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json_data.encode("utf-8"))
            else:
                return http.server.SimpleHTTPRequestHandler.do_GET(self)

    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print("Serving at port", PORT)
        httpd.serve_forever()

if __name__ == '__main__':
    # Pour tester en mode autonome, vous pouvez créer la connexion ici :
    run_server(database.init_db())
