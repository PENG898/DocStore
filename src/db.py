# -*- coding: utf-8 -*-
"""
Database layer - file index, tags, metadata.
SQLite with WAL mode for concurrent read performance.
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime

DB_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DB_DIR / "index.db"


def get_connection():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS folders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE, path TEXT NOT NULL UNIQUE,
        file_count INTEGER DEFAULT 0, total_size INTEGER DEFAULT 0,
        last_scan TEXT, enabled INTEGER DEFAULT 1)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        folder_id INTEGER NOT NULL, file_path TEXT NOT NULL UNIQUE,
        file_name TEXT NOT NULL, file_ext TEXT, file_size INTEGER DEFAULT 0,
        file_type TEXT, category TEXT, file_hash TEXT,
        modified_time TEXT, created_time TEXT,
        indexed_at TEXT NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (folder_id) REFERENCES folders(id) ON DELETE CASCADE)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE, color TEXT DEFAULT '#4A90D9',
        created_at TEXT NOT NULL DEFAULT (datetime('now')))""")
    cur.execute("""CREATE TABLE IF NOT EXISTS file_tags (
        file_id INTEGER NOT NULL, tag_id INTEGER NOT NULL,
        PRIMARY KEY (file_id, tag_id),
        FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE,
        FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS scan_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        folder_id INTEGER, scan_time TEXT NOT NULL DEFAULT (datetime('now')),
        files_added INTEGER DEFAULT 0, files_removed INTEGER DEFAULT 0,
        files_updated INTEGER DEFAULT 0, status TEXT DEFAULT 'success',
        error_msg TEXT)""")
    # Indexes
    cur.execute("CREATE INDEX IF NOT EXISTS idx_files_name ON files(file_name)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_files_ext ON files(file_ext)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_files_category ON files(category)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_files_size ON files(file_size)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_files_folder ON files(folder_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_files_path ON files(file_path)")
    # Migrate: add file_hash column if missing (must be before index creation)
    try:
        cur.execute("SELECT file_hash FROM files LIMIT 1")
    except sqlite3.OperationalError:
        cur.execute("ALTER TABLE files ADD COLUMN file_hash TEXT")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_files_hash ON files(file_hash)")
    conn.commit()
    conn.close()


def init_default_tags():
    conn = get_connection()
    cur = conn.cursor()
    default_tags = [
        ('课程', '#4A90D9'), ('二课', '#50C878'), ('自考', '#FF6B6B'),
        ('奖项', '#FFA500'), ('项目', '#9B59B6'), ('代码', '#1ABC9C'),
        ('文档', '#34495E'), ('图片', '#E67E22'), ('视频', '#E74C3C'),
        ('PPT', '#F39C12'), ('PDF', '#C0392B'), ('工具', '#2ECC71'),
    ]
    for name, color in default_tags:
        cur.execute("INSERT OR IGNORE INTO tags (name, color) VALUES (?, ?)", (name, color))
    conn.commit()
    conn.close()


def get_folder(path):
    conn = get_connection()
    row = conn.execute("SELECT * FROM folders WHERE path=?", (path,)).fetchone()
    conn.close()
    return dict(row) if row else None


def upsert_folder(name, path):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""INSERT INTO folders (name, path, last_scan)
        VALUES (?, ?, ?) ON CONFLICT(path) DO UPDATE SET last_scan=excluded.last_scan""",
        (name, path, datetime.now().isoformat()))
    conn.commit()
    fid = cur.execute("SELECT id FROM folders WHERE path=?", (path,)).fetchone()[0]
    conn.close()
    return fid


def add_files_to_folder(folder_id, files):
    conn = get_connection()
    cur = conn.cursor()
    added = 0
    for f in files:
        cur.execute("""INSERT INTO files (folder_id, file_path, file_name, file_ext,
            file_size, file_type, category, file_hash, modified_time, created_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(file_path) DO UPDATE SET
                file_size=excluded.file_size, file_type=excluded.file_type,
                category=excluded.category, file_hash=excluded.file_hash,
                modified_time=excluded.modified_time, indexed_at=datetime('now')""",
            (folder_id, f["file_path"], f["file_name"], f["file_ext"],
             f["file_size"], f["file_type"], f["category"],
             f.get("file_hash"), f["modified_time"], f.get("created_time", "")))
        if cur.rowcount:
            added += 1
    cur.execute("SELECT COUNT(*), COALESCE(SUM(file_size),0) FROM files WHERE folder_id=?", (folder_id,))
    count, size = cur.fetchone()
    cur.execute("UPDATE folders SET file_count=?, total_size=? WHERE id=?", (count, size, folder_id))
    conn.commit()
    conn.close()
    return added


def remove_files(folder_id, file_paths):
    conn = get_connection()
    cur = conn.cursor()
    ph = ",".join(["?"] * len(file_paths))
    cur.execute(f"DELETE FROM files WHERE folder_id=? AND file_path IN ({ph})", file_paths)
    removed = cur.rowcount
    cur.execute("SELECT COUNT(*), COALESCE(SUM(file_size),0) FROM files WHERE folder_id=?", (folder_id,))
    count, size = cur.fetchone()
    cur.execute("UPDATE folders SET file_count=?, total_size=? WHERE id=?", (count, size, folder_id))
    conn.commit()
    conn.close()
    return removed


def get_all_folders():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM folders ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_file_count():
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
    conn.close()
    return count


def get_db_size():
    try:
        return os.path.getsize(str(DB_PATH))
    except OSError:
        return 0


def get_files_by_category(limit=50):
    conn = get_connection()
    rows = conn.execute("""
        SELECT category, COUNT(*) as cnt, COALESCE(SUM(file_size),0) as total_size
        FROM files GROUP BY category ORDER BY cnt DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_files_by_extension(limit=50):
    conn = get_connection()
    rows = conn.execute("""
        SELECT COALESCE(file_ext, '(none)') as ext, COUNT(*) as cnt, COALESCE(SUM(file_size),0) as total_size
        FROM files GROUP BY ext ORDER BY cnt DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_folder_stats():
    conn = get_connection()
    rows = conn.execute("""
        SELECT name, path, file_count, total_size, last_scan, enabled
        FROM folders ORDER BY file_count DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_duplicate_files():
    conn = get_connection()
    rows = conn.execute("""
        SELECT file_name, COUNT(*) as cnt, GROUP_CONCAT(file_path) as paths, file_size
        FROM files GROUP BY LOWER(file_name) HAVING cnt > 1
        ORDER BY cnt DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_duplicates_by_hash():
    """Group files by MD5 hash. Only returns groups with 2+ identical files."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT file_hash, COUNT(*) as cnt,
               GROUP_CONCAT(file_path) as paths,
               GROUP_CONCAT(file_name) as names,
               file_size
        FROM files
        WHERE file_hash IS NOT NULL AND file_hash != ''
        GROUP BY file_hash HAVING cnt > 1
        ORDER BY file_size * cnt DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_large_files(limit=20, size_threshold=100*1024*1024):
    conn = get_connection()
    rows = conn.execute("""
        SELECT f.file_name, f.file_path, f.file_size, f.file_ext, fo.name as folder_name
        FROM files f JOIN folders fo ON f.folder_id = fo.id
        WHERE f.file_size > ?
        ORDER BY file_size DESC LIMIT ?
    """, (size_threshold, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]



def get_top10_largest():
    """Return the absolute top 10 largest files regardless of any size threshold."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT f.file_name, f.file_path, f.file_size, f.file_ext, fo.name as folder_name
        FROM files f JOIN folders fo ON f.folder_id = fo.id
        ORDER BY f.file_size DESC LIMIT 10
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def clear_hash_for_folder(folder_id):
    """Clear hashes before re-scanning so stale entries are removed."""
    conn = get_connection()
    conn.execute("UPDATE files SET file_hash=NULL WHERE folder_id=?", (folder_id,))
    conn.commit()
    conn.close()



def remove_stale_files(folder_id, current_paths):
    """Remove files from DB that no longer exist on disk for a given folder."""
    conn = get_connection()
    rows = conn.execute("SELECT id, file_path FROM files WHERE folder_id=?", (folder_id,)).fetchall()
    current_set = set(current_paths)
    stale = [dict(r) for r in rows if r["file_path"] not in current_set]
    if stale:
        ids = [s["id"] for s in stale]
        ph = ",".join(["?"] * len(ids))
        conn.execute(f"DELETE FROM files WHERE id IN ({ph})", ids)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*), COALESCE(SUM(file_size),0) FROM files WHERE folder_id=?", (folder_id,))
        count, size = cur.fetchone()
        cur.execute("UPDATE folders SET file_count=?, total_size=? WHERE id=?", (count, size, folder_id))
        conn.commit()
    conn.close()
    return len(stale)
