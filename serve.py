"""
serve.py — Local dev server for Axiom CS Tutor
Serves the web/ directory and proxies /api/* to Ollama.

Usage:
    python serve.py

Then open: http://localhost:5000
"""

import http.server
import urllib.request
import urllib.error
import json
import os
import sys

PORT = 5000
WEB_DIR = os.path.join(os.path.dirname(__file__), "web")
OLLAMA_BASE = "http://localhost:11434"


class AxiomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    # ── Proxy /api/* to Ollama ────────────────────────────
    def do_POST(self):
        if self.path.startswith("/api/"):
            self._proxy_to_ollama()
        else:
            self.send_error(405, "Method Not Allowed")

    def _proxy_to_ollama(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        target = OLLAMA_BASE + self.path
        req = urllib.request.Request(
            target,
            data=body,
            method="POST",
            headers={"Content-Type": "application/json"},
        )

        try:
            with urllib.request.urlopen(req) as resp:
                self.send_response(resp.status)
                # Forward content-type
                ct = resp.headers.get("Content-Type", "application/json")
                self.send_header("Content-Type", ct)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()

                # Stream chunks straight through
                while True:
                    chunk = resp.read(1024)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    self.wfile.flush()

        except urllib.error.URLError as e:
            self.send_error(502, f"Ollama unreachable: {e.reason}")

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, fmt, *args):
        # Cleaner output
        if "/api/" in (args[0] if args else ""):
            print(f"  [proxy] {args[0]}")
        else:
            super().log_message(fmt, *args)


if __name__ == "__main__":
    os.chdir(WEB_DIR)
    print(f"\n  Axiom CS Tutor")
    print(f"  Running at:   http://localhost:{PORT}")
    print(f"  Proxying to:  {OLLAMA_BASE}")
    print(f"  Press Ctrl+C to stop\n")

    server = http.server.HTTPServer(("", PORT), AxiomHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
        sys.exit(0)
