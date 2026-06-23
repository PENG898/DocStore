#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DocStore (文存仓) - Main Launcher
"""

import json
import os
import sys
import argparse
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import threading
from pathlib import Path
from urllib.parse import urlparse, parse_qs

PROJECT_DIR = Path(__file__).resolve().parent
SRC_DIR = PROJECT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from config import DB_PATH, OUTPUT_DIR, HTML_PATH, JSON_PATH, TEMPLATE_PATH, SERVER_PORT, SCAN_DIRS
from db import init_db, get_connection
from scanner import full_scan
from search import get_all_files
from suggest import get_all_suggestions

# Global scan state tracker
_scan_lock = threading.Lock()
_is_scanning = False

def get_scan_status():
    with _scan_lock:
        return _is_scanning

def set_scan_status(val):
    global _is_scanning
    with _scan_lock:
        _is_scanning = val

def do_scan():
    print("[1/4] Scanning folders...")
    init_db()
    total, added, _ = full_scan(lambda name, count, _: print(f"  {name}: {count} files"))
    print(f"  Total: {total} files indexed")
    return total


def do_export():
    print("[2/4] Exporting data...")
    data = get_all_files()
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  Exported {len(data)} records")
    return data


def do_suggestions():
    print("[3/4] Generating suggestions...")
    sugs = get_all_suggestions()
    print(f"  {sugs['total_duplicates']} duplicates, {sugs['total_large']} large files")
    return sugs


def do_generate_html(data, suggestions):
    print("[4/4] Generating HTML...")
    if not TEMPLATE_PATH.exists():
        print(f"  ERROR: Template not found at {TEMPLATE_PATH}")
        return None

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    conn = get_connection()
    cat_rows = conn.execute(
        "SELECT category, COUNT(*) as cnt, COALESCE(SUM(file_size),0) as sz FROM files GROUP BY category ORDER BY cnt DESC"
    ).fetchall()
    ext_rows = conn.execute(
        "SELECT COALESCE(file_ext,'') as ext, COUNT(*) as cnt FROM files GROUP BY ext ORDER BY cnt DESC LIMIT 10"
    ).fetchall()
    folder_rows = conn.execute(
        "SELECT fo.name as folder, COUNT(*) as cnt, COALESCE(SUM(f.file_size),0) as sz FROM files f JOIN folders fo ON f.folder_id=fo.id GROUP BY fo.name ORDER BY cnt DESC"
    ).fetchall()
    conn.close()

    cat_stats = [{"name": r["category"] or "Other", "count": r["cnt"], "size": r["sz"]} for r in cat_rows]
    ext_stats = [{"ext": r["ext"], "count": r["cnt"]} for r in ext_rows]
    folder_stats = [{"folder": r["folder"], "count": r["cnt"], "size": r["sz"]} for r in folder_rows]

    dups = suggestions.get("duplicates", [])
    dup_data = [{"name": d["name"], "count": d["count"], "size": d["size"], "paths": d["paths"], "hash": d.get("hash"), "method": d.get("method", "filename")} for d in dups[:50]]
    large = suggestions.get("large_files", [])
    large_data = [{"name": f["name"], "path": f["path"], "size": f["size"]} for f in large[:50]]

    html = html.replace("__ALL_FILES__", json.dumps(data, ensure_ascii=False))
    html = html.replace("__CAT_STATS__", json.dumps(cat_stats, ensure_ascii=False))
    html = html.replace("__EXT_STATS__", json.dumps(ext_stats, ensure_ascii=False))
    html = html.replace("__FOLDER_STATS__", json.dumps(folder_stats, ensure_ascii=False))
    html = html.replace("__DUPLICATES__", json.dumps(dup_data, ensure_ascii=False))
    html = html.replace("__LARGE_FILES__", json.dumps(large_data, ensure_ascii=False))

    top10 = suggestions.get("top10_largest", [])
    top10_data = [{"name": f["name"], "path": f["path"], "size": f["size"]} for f in top10[:10]]
    html = html.replace("__TOP10_LARGEST__", json.dumps(top10_data, ensure_ascii=False))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  Dashboard: {HTML_PATH}")
    return str(HTML_PATH)


def _background_rescan():
    """Run full scan pipeline in background thread."""
    try:
        do_scan()
        data = do_export()
        sugs = do_suggestions()
        do_generate_html(data, sugs)
        print("  Rescan completed.")
    except Exception as e:
        print(f"  Rescan error: {e}")
    finally:
        set_scan_status(False)


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


class DashboardHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _json_response(self, data, code=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path in ("/", "/index.html", "/dashboard"):
            if HTML_PATH.exists():
                with open(HTML_PATH, "rb") as f:
                    body = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", len(body))
                self.end_headers()
                self.wfile.write(body)
            else:
                self._json_response({"error": "Dashboard not generated yet"}, 404)
        elif path == "/api/health":
            self._json_response({"ok": True, "scanning": get_scan_status()})
        elif path == "/api/preview-image":
            self._handle_preview_image()
        else:
            self._json_response({"error": "Not found"}, 404)

    def do_POST(self):
        try:
            parsed = urlparse(self.path)
            path = parsed.path
            content_len = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_len) if content_len else b""
            if path == "/api/scan":
                self._handle_rescan()
            elif path == "/api/open-file":
                self._handle_open_file(body)
            elif path == "/api/show-in-folder":
                self._handle_show_in_folder(body)
            else:
                self._json_response({"error": "Unknown endpoint"}, 404)
        except Exception as e:
            try:
                self._json_response({"error": str(e)}, 500)
            except Exception:
                pass

    def _handle_open_file(self, body):
        try:
            data = json.loads(body)
            filepath = data.get("path", "")
            if not filepath:
                self._json_response({"ok": False, "error": "No path"}, 400)
                return
            if not os.path.exists(filepath):
                self._json_response({"ok": False, "error": "File not found on disk"}, 400)
                return
            os.startfile(filepath)
            self._json_response({"ok": True})
        except Exception as e:
            self._json_response({"ok": False, "error": str(e)}, 500)

    def _handle_show_in_folder(self, body):
        try:
            data = json.loads(body)
            filepath = data.get("path", "")
            if not filepath:
                self._json_response({"ok": False, "error": "No path"}, 400)
                return
            folder = os.path.dirname(filepath)
            if not os.path.exists(folder):
                self._json_response({"ok": False, "error": "Folder not found on disk"}, 400)
                return
            os.startfile(folder)
            self._json_response({"ok": True})
        except Exception as e:
            self._json_response({"ok": False, "error": str(e)}, 500)

    def _handle_preview_image(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        filepath = params.get("path", [""])[0]
        if not filepath or not os.path.exists(filepath):
            self._json_response({"error": "File not found"}, 404)
            return
        ext = os.path.splitext(filepath)[1].lower()
        mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
                    ".gif": "image/gif", ".bmp": "image/bmp", ".svg": "image/svg+xml",
                    ".ico": "image/x-icon", ".webp": "image/webp"}
        mime = mime_map.get(ext, "application/octet-stream")
        try:
            with open(filepath, "rb") as f:
                data = f.read()
            self.send_response(200)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", len(data))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self._json_response({"error": str(e)}, 500)

    def _handle_rescan(self):
        """Start scan in background thread so HTTP response returns immediately."""
        if get_scan_status():
            self._json_response({"ok": True, "status": "already_scanning"})
            return
        set_scan_status(True)
        t = threading.Thread(target=_background_rescan, daemon=True)
        t.start()
        self._json_response({"ok": True, "status": "started"})


def start_server(port):
    server = ThreadingHTTPServer(("127.0.0.1", port), DashboardHandler)
    print()
    print("=" * 50)
    print(f"  Server running at http://localhost:{port}")
    print(f"  Press Ctrl+C to stop")
    print("=" * 50)
    webbrowser.open(f"http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


def main():
    parser = argparse.ArgumentParser(description="DocStore / \u6587\u5b58\u4ed3")
    parser.add_argument("--port", type=int, default=SERVER_PORT, help="HTTP port")
    parser.add_argument("--no-serve", action="store_true", help="Skip server, just scan+generate")
    args = parser.parse_args()

    print("=" * 50)
    print("  DocStore / \u6587\u5b58\u4ed3")
    print("=" * 50)
    print()

    # First-run check: verify SCAN_DIRS exist on this machine
    _missing = [str(p) for p in SCAN_DIRS if not p.exists()]
    if _missing:
        print("  [!] 扫描路径不存在，请先运行 setup.bat 配置：")
        for p in _missing:
            print(f"    - {p}")
        print()
        sys.exit(1)


    do_scan()
    data = do_export()
    suggestions = do_suggestions()
    html_path = do_generate_html(data, suggestions)

    if not args.no_serve and html_path:
        start_server(args.port)
    elif html_path:
        print("\nDone! Open", html_path, "in your browser.")


if __name__ == "__main__":
    main()
