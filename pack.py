#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DocStore pack script

Usage: python pack.py
Generates DocStore.zip containing only core distributable files.
Excludes .db, scan_log.txt, *.tmp, Excel/ZIP backups, legacy .bat launchers,
and any temp folders whose names contain CJK characters or spaces.
"""

import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath

PROJECT = Path(__file__).resolve().parent
ZIP_PATH = PROJECT / "DocStore.zip"

CORE_TOP_LEVEL = {
    "main.py",
    "setup.py",
    "setup.bat",
    "README.md",
    "DIST_README.md",
}


def _has_non_ascii_or_space(value: str) -> bool:
    return bool(re.search(r"[\s\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]", value))


def _should_skip_path(rel: Path) -> bool:
    parts = rel.parts
    if not parts:
        return True

    # Skip any path component with CJK or spaces (temp folders)
    for part in parts:
        if _has_non_ascii_or_space(part):
            return True

    # Top-level: only allow core files + src/ + templates/
    if len(parts) == 1:
        return parts[0] not in CORE_TOP_LEVEL

    # src/*.py only (no __pycache__)
    if parts[0] == "src":
        if any(p == "__pycache__" for p in parts):
            return True
        return not (len(parts) == 2 and parts[1].endswith(".py"))

    # templates/* only
    if parts[0] == "templates":
        return not (len(parts) == 2)

    return True


SKIP_EXTENSIONS = {".db", ".tmp", ".xlsx", ".xls", ".csv", ".zip"}
SKIP_BASENAMES = {"scan_log.txt"}


def _should_skip_file(file_path: Path) -> bool:
    lower = file_path.name.lower()
    if lower in {n.lower() for n in SKIP_BASENAMES}:
        return True
    if file_path.suffix.lower() in SKIP_EXTENSIONS:
        return True
    return False


def _show_popup(message: str) -> None:
    """Show a Windows message box via PowerShell (non-blocking)."""
    escaped = message.replace("'", "''")
    ps_script = (
        f"Add-Type -AssemblyName System.Windows.Forms; "
        f"[System.Windows.Forms.MessageBox]::Show('{escaped}', 'DocStore pack done', 'OK', 'Information')"
    )
    subprocess.Popen(
        ["powershell", "-NoProfile", "-Command", ps_script],
        creationflags=subprocess.CREATE_NO_WINDOW,
    )


def main():
    # Remove old zip if present
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()

    collected = []
    for path in sorted(PROJECT.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(PROJECT)
        if _should_skip_path(rel):
            continue
        if _should_skip_file(path):
            continue
        collected.append(path)

    if not collected:
        raise RuntimeError("No files matched the DocStore packing rules.")

    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in collected:
            rel = file_path.relative_to(PROJECT)
            arcname = str(PurePosixPath("DocStore", *rel.parts))
            zf.write(file_path, arcname)

    size_kb = ZIP_PATH.stat().st_size // 1024
    message = f"DocStore.zip packed successfully\nPath: {ZIP_PATH}\nSize: {size_kb} KB"
    print(message)
    _show_popup(message)


if __name__ == "__main__":
    main()
