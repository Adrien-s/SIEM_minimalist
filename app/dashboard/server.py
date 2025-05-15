import http.server
import socketserver
import json
import os
from urllib.parse import urlparse, parse_qs
from data import database

def run_server(db_conn):
    PORT = 8000

    # Définir le répertoire pour servir les fichiers statiques du dashboard
    template_dir = os.path.join(os.getcwd(), "dashboard", "template")
    if os.path.isdir(template_dir):
        os.chdir(template_dir)
        print("Répertoire de travail changé vers :", os.getcwd())
    else:
        print("Le répertoire template n'a pas été trouvé :", template_dir)

    class MyHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            parsed_url = urlparse(self.path)
            if parsed_url.path == '/data':
                qs = parse_qs(parsed_url.query)
                try:
                    limit = int(qs.get("limit", [100])[0])
                except ValueError:
                    limit = 100
                try:
                    offset = int(qs.get("offset", [0])[0])
                except ValueError:
                    offset = 0

                search_field = qs.get('searchField', [None])[0]
                search_value = qs.get('searchValue', [None])[0]

                # Récupération des logs avec pagination
                filters = {}
                if search_field and search_value:
                    # Pour le champ 'time' ou 'event_id', comme ils sont stockés en TEXT on pourra faire un LIKE
                    filters[search_field] = f"%{search_value}%"
                    
                # On modifie query_logs pour traiter LIKE si la valeur contient '%' ou '=' sinon exact
                logs = database.query_logs(db_conn, limit=limit, offset=offset, **filters)
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
    run_server(database.init_db())
