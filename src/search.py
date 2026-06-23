#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Search module - multi-condition search, export, and stats.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from db import get_connection


def search_files(keyword, category=None, ext=None, folder=None, tag=None, limit=100):
    conn = get_connection()
    query = """
        SELECT f.id, f.file_name, f.file_path, f.file_size, f.file_ext,
               f.file_type, f.category, f.modified_time, f.indexed_at,
               fo.name as folder_name
        FROM files f JOIN folders fo ON f.folder_id = fo.id
        WHERE 1=1
    """
    params = []
    if keyword:
        query += " AND f.file_name LIKE ?"
        params.append(f"%{keyword}%")
    if category and category != "全部":
        query += " AND f.category = ?"
        params.append(category)
    if ext and ext != "全部":
        query += " AND f.file_ext = ?"
        params.append(ext)
    if folder and folder != "全部":
        query += " AND fo.name = ?"
        params.append(folder)
    query += " ORDER BY f.modified_time DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_files():
    """Return every indexed file as a list of dicts for HTML export."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT f.file_name as name, f.file_path as path, f.file_size as size,
               f.file_ext as extension, f.file_type as type,
               f.category, fo.name as folder, f.modified_time
        FROM files f JOIN folders fo ON f.folder_id = fo.id
        ORDER BY f.category, f.file_name
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_categories():
    conn = get_connection()
    rows = conn.execute("SELECT DISTINCT category FROM files ORDER BY category").fetchall()
    conn.close()
    return [r["category"] for r in rows]


def get_all_extensions():
    conn = get_connection()
    rows = conn.execute("SELECT DISTINCT file_ext FROM files WHERE file_ext != '' ORDER BY file_ext").fetchall()
    conn.close()
    return [r["file_ext"] for r in rows]


def get_all_folders():
    conn = get_connection()
    rows = conn.execute("SELECT DISTINCT name FROM folders ORDER BY name").fetchall()
    conn.close()
    return [r["name"] for r in rows]
