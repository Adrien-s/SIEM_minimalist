import http.server
import socketserver
import json
import os
from app.collectors.expcollect import logcollector

PORT = 8000

# Définir le répertoire à partir duquel servir les fichiers
template_dir = os.path.join(os.getcwd(), "app", "dashboard", "template")
if os.path.isdir(template_dir):
    os.chdir(template_dir)
    print("Répertoire de travail changé vers :", os.getcwd())
else:
    print("Le répertoire template n'a pas été trouvé :", template_dir)

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/data':
            data = logcollector("C:\\Windows\\System32\\winevt\\Logs\\Application.evtx")
            response = {"events": data}
            json_data = json.dumps(response)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json_data.encode("utf-8"))
        else:
            # Pour toutes les autres requêtes, on laisse le serveur servir les fichiers depuis le répertoire courant
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print("Serving at port", PORT)
    httpd.serve_forever()
