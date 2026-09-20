#!/usr/bin/env python3
"""
AquaTrack — mini serveur de suivi d'hydratation.
Aucune dépendance externe : uniquement la bibliothèque standard Python.

Lancement :
    python3 server.py
Puis ouvrir : http://localhost:8421
Ou depuis un autre appareil du même réseau : http://<IP-de-cette-machine>:8421
"""

import json
import os
from datetime import datetime, date
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

HOST = "0.0.0.0"  # écoute sur toutes les interfaces réseau (accessible depuis le LAN)
PORT = 8421

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.json")
INDEX_FILE = os.path.join(BASE_DIR, "index.html")


# ---------------------------------------------------------------------------
# Stockage JSON
# ---------------------------------------------------------------------------

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"entries": [], "goal_ml": 2000}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            data.setdefault("entries", [])
            data.setdefault("goal_ml", 2000)
            return data
    except (json.JSONDecodeError, OSError):
        return {"entries": [], "goal_ml": 2000}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Aide : calcul des statistiques par jour
# ---------------------------------------------------------------------------

def compute_daily_stats(entries):
    """Retourne une liste [{date, total_ml}] triée du plus ancien au plus récent."""
    totals = {}
    for e in entries:
        d = e["date"]
        totals[d] = totals.get(d, 0) + e["amount_ml"]
    days = sorted(totals.keys())
    return [{"date": d, "total_ml": totals[d]} for d in days]


# ---------------------------------------------------------------------------
# HTTP Handler
# ---------------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    server_version = "AquaTrack/1.0"

    # ---- utilitaires de réponse -------------------------------------------------
    def _send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path, content_type):
        try:
            with open(path, "rb") as f:
                body = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except FileNotFoundError:
            self._send_json({"error": "not found"}, 404)

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def log_message(self, format, *args):
        # Log minimal et silencieux
        pass

    # ---- routes -------------------------------------------------------------
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            self._send_file(INDEX_FILE, "text/html; charset=utf-8")

        elif path == "/api/data":
            data = load_data()
            self._send_json(data)

        elif path == "/api/stats":
            data = load_data()
            stats = compute_daily_stats(data["entries"])
            self._send_json({"days": stats, "goal_ml": data["goal_ml"]})

        else:
            self._send_json({"error": "not found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        body = self._read_json_body()

        if path == "/api/add":
            amount_ml = body.get("amount_ml")
            if not isinstance(amount_ml, (int, float)) or amount_ml <= 0:
                self._send_json({"error": "amount_ml invalide"}, 400)
                return

            data = load_data()
            now = datetime.now()
            entry = {
                "id": int(now.timestamp() * 1000),
                "date": now.strftime("%Y-%m-%d"),
                "time": now.strftime("%H:%M"),
                "amount_ml": int(amount_ml),
            }
            data["entries"].append(entry)
            save_data(data)
            self._send_json({"ok": True, "entry": entry, "data": data})

        elif path == "/api/delete":
            entry_id = body.get("id")
            data = load_data()
            data["entries"] = [e for e in data["entries"] if e["id"] != entry_id]
            save_data(data)
            self._send_json({"ok": True, "data": data})

        elif path == "/api/goal":
            goal_ml = body.get("goal_ml")
            if not isinstance(goal_ml, (int, float)) or goal_ml <= 0:
                self._send_json({"error": "goal_ml invalide"}, 400)
                return
            data = load_data()
            data["goal_ml"] = int(goal_ml)
            save_data(data)
            self._send_json({"ok": True, "data": data})

        else:
            self._send_json({"error": "not found"}, 404)


def main():
    if not os.path.exists(DATA_FILE):
        save_data({"entries": [], "goal_ml": 2000})

    httpd = HTTPServer((HOST, PORT), Handler)
    print(f"AquaTrack lancé :")
    print(f"  - Sur cet ordinateur : http://localhost:{PORT}")
    print(f"  - Depuis le réseau local : http://<IP-de-cette-machine>:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt du serveur.")
        httpd.server_close()


if __name__ == "__main__":
    main()
