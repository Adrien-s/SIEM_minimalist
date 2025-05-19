import http.server
import socketserver
import json
import os
from urllib.parse import urlparse, parse_qs
from data import database
from data.rules_service    import list_rules, add_rule, update_rule, delete_rule
from data.event_service    import list_event_definitions
from datetime import datetime


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

                start_time = qs.get("startTime", [None])[0]
                end_time   = qs.get("endTime",   [None])[0]

                # Récupération des logs avec pagination
                filters = {}
                if search_field and search_value:
                    #
                    filters[search_field] = f"%{search_value}%"
                    
                # On modifie query_logs pour traiter LIKE si la valeur contient '%' ou '=' sinon exact
                logs = database.query_logs(
                    db_conn,
                    limit=limit,
                    offset=offset,
                    start_time=start_time,
                    end_time=end_time,
                    **filters
                )
                response = {"events": logs}
                json_data = json.dumps(response)
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json_data.encode("utf-8"))

            elif parsed_url.path == '/rules':
                rules = list_rules(db_conn)
                self.send_response(200)
                self.send_header('Content-Type','application/json')
                self.end_headers()
                self.wfile.write(json.dumps(rules).encode())
            
            elif parsed_url.path == '/alerts':
                # jointure pour avoir channel et event_id depuis rules
                cur = db_conn.execute("""
                    SELECT a.id, a.rule_id, r.channel, r.event_id, a.count, a.triggered_at
                    FROM alerts a
                    JOIN rules  r ON a.rule_id = r.id
                    ORDER BY a.id DESC
                """)
                cols = [c[0] for c in cur.description]
                rows = [dict(zip(cols, row)) for row in cur.fetchall()]
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(rows).encode())
            
            elif parsed_url.path == '/definitions':
                defs = list_event_definitions(db_conn)
                self.send_response(200)
                self.send_header('Content-Type','application/json')
                self.end_headers()
                self.wfile.write(json.dumps(defs).encode())
            
            elif parsed_url.path == '/analytics':
                qs = parse_qs(parsed_url.query)
                raw_start = qs.get("startTime", [None])[0]
                raw_end   = qs.get("endTime",   [None])[0]

                filters = {}
                sf = qs.get('searchField', [None])[0]
                sv = qs.get('searchValue', [None])[0]

                if sf and sv:
                    #
                    filters[sf] = f"%{sv}%"

                # Récupérer d’abord tous les logs (sans LIMIT ni filtre date)
                logs_all = database.query_logs(db_conn, **filters)

                # Filtrer ensuite en Python
                if raw_start and raw_end:
                    # JS envoie "…Z", on l'enlève pour fromisoformat()
                    st = datetime.fromisoformat(raw_start.rstrip('Z'))
                    ed = datetime.fromisoformat(raw_end.rstrip('Z'))
                    logs = [
                        log for log in logs_all
                        if st <= datetime.fromisoformat(log['time']) <= ed
                    ]
                else:
                    logs = logs_all

                # Debug
                print(f"DEBUG /analytics start={raw_start} end={raw_end}")
                print("DEBUG  nb logs avant envoi:", len(logs))

                # Envoi de la réponse
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"events": logs}).encode())
                
                
            else:
                return http.server.SimpleHTTPRequestHandler.do_GET(self)
        
        def do_POST(self):
            url = urlparse(self.path)
            if url.path == '/rules':
                length = int(self.headers.get('Content-Length', 0))
                payload = json.loads(self.rfile.read(length))
                # payload doit contenir {id?, channel, event_id, threshold, window_min}
                if 'id' in payload:
                    update_rule(
                        db_conn,
                        payload['id'],
                        payload['channel'],
                        payload['event_id'],
                        payload['threshold'],
                        payload['window_min']
                    )
                else:
                    add_rule(
                        db_conn,
                        payload['channel'],
                        payload['event_id'],
                        payload['threshold'],
                        payload['window_min']
                    )
                self.send_response(204)
                self.end_headers()
                return
            else:
                return super().do_POST()

        def do_DELETE(self):
            url = urlparse(self.path)
            if url.path == '/rules':
                qs = parse_qs(url.query)
                rid_str = qs.get('id', [None])[0]
                try:
                    rid = int(rid_str)
                except (TypeError, ValueError):
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b'Invalid rule id')
                    return
                delete_rule(db_conn, rid)
                self.send_response(204)
                self.end_headers()
                return
            return super().do_DELETE()

    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print("Serving at port", PORT)
        httpd.serve_forever()

if __name__ == '__main__':
    run_server(database.init_db())
