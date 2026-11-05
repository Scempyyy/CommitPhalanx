"""HTTP server and REST API for CommitPhalanx studio."""

import http.server
import json
import os
import socketserver
import urllib.parse
from typing import Any
from .synthesizer import GitAnalyzer, CommitSynthesizer

STATIC_DIR = os.path.join(os.path.dirname(__file__), "web")


class CommitPhalanxHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler serving git commit synthesizer API and studio UI."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    @property
    def analyzer(self) -> GitAnalyzer:
        if not hasattr(self.server, "analyzer"):
            self.server.analyzer = GitAnalyzer()
        return self.server.analyzer

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/api/status":
            self.send_json(200, {"status": "active", "service": "CommitPhalanx"})
            return

        elif parsed.path == "/api/diff":
            diff = self.analyzer.get_diff()
            files = self.analyzer.get_status_summary()
            self.send_json(200, {"diff": diff, "files": files})
            return

        elif parsed.path == "/api/changelog":
            commits = self.analyzer.get_commit_history(limit=50)
            changelog_md = CommitSynthesizer.generate_changelog(commits)
            self.send_json(200, {"changelog": changelog_md, "commit_count": len(commits)})
            return

        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"

        try:
            data = json.loads(post_body)
        except Exception:
            data = {}

        if parsed.path == "/api/synthesize/commit":
            diff = data.get("diff") or self.analyzer.get_diff()
            files = data.get("files") or self.analyzer.get_status_summary()
            commit_res = CommitSynthesizer.synthesize_commit(diff, files)
            self.send_json(200, commit_res)
            return

        elif parsed.path == "/api/synthesize/pr":
            branch = data.get("branch", "feature-branch")
            diff = data.get("diff") or self.analyzer.get_diff()
            files = data.get("files") or self.analyzer.get_status_summary()
            pr_res = CommitSynthesizer.synthesize_pull_request(branch, diff, files)
            self.send_json(200, pr_res)
            return

        self.send_json(404, {"error": "Endpoint not found"})

    def send_json(self, status: int, payload: Any):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def log_message(self, format, *args):
        pass


def run_server(port: int = 7099, host: str = "127.0.0.1", repo_path: str = None):
    """Starts the CommitPhalanx web studio."""
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer((host, port), CommitPhalanxHandler)
    server.analyzer = GitAnalyzer(repo_path)
    print(f"[*] CommitPhalanx Studio active at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Stopping CommitPhalanx server.")
