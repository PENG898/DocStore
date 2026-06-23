import sys
import json
import urllib.request
import subprocess
import time
from pathlib import Path

root = Path(r"C:\Users\PENG\Desktop\workspace\project05_kezi")
port = 18181
proc = subprocess.Popen([sys.executable, str(root / "main.py"), "--port", str(port)], cwd=str(root), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
try:
    deadline = time.time() + 90
    started = False
    while time.time() < deadline:
        line = proc.stdout.readline()
        if not line:
            if proc.poll() is not None:
                break
            time.sleep(0.1)
            continue
        if "Server running at" in line:
            started = True
            break
    if not started:
        out, _ = proc.communicate(timeout=5)
        print("SERVER_DID_NOT_START")
        print((out or "").strip())
        sys.exit(1)

    req = urllib.request.Request(f"http://127.0.0.1:{port}/api/scan", data=b"{}", headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as resp:
        status = resp.status
        body = json.loads(resp.read().decode("utf-8"))
    print("SCAN_STATUS", status)
    print("SCAN_BODY", json.dumps(body, ensure_ascii=False))
finally:
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except Exception:
        proc.kill()
