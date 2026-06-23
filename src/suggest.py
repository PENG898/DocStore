#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suggestions module - duplicates (MD5-based), large files, category stats.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from db import get_duplicate_files, get_duplicates_by_hash, get_large_files, get_files_by_category, get_top10_largest


def suggest_duplicates():
    """MD5-based duplicate detection (primary) with filename fallback."""
    results = []

    # Primary: MD5 hash duplicates (exact byte-for-byte matches)
    hash_rows = get_duplicates_by_hash()
    for r in hash_rows:
        paths = r["paths"].split(",")
        names = r["names"].split(",")
        if len(paths) >= 2:
            results.append({
                "name": names[0] if names else r["file_hash"][:12],
                "size": r["file_size"],
                "count": r["cnt"],
                "paths": paths,
                "hash": r["file_hash"],
                "waste": r["file_size"] * (r["cnt"] - 1),
                "method": "md5",
            })

    # Fallback: filename-based duplicates (for files too large to hash)
    hashed_paths = set()
    for r in results:
        hashed_paths.update(r["paths"])

    name_rows = get_duplicate_files()
    for r in name_rows:
        paths = r["paths"].split(",")
        # Skip if already covered by MD5 detection
        if all(p in hashed_paths for p in paths):
            continue
        if len(paths) >= 2:
            results.append({
                "name": r["file_name"],
                "size": r["file_size"],
                "count": r["cnt"],
                "paths": paths,
                "hash": None,
                "waste": r["file_size"] * (r["cnt"] - 1),
                "method": "filename",
            })

    return sorted(results, key=lambda x: x["waste"], reverse=True)


def suggest_large_files():
    rows = get_large_files(limit=30, size_threshold=50 * 1024 * 1024)
    return [{"name": r["file_name"], "path": r["file_path"], "size": r["file_size"],
             "ext": r["file_ext"], "folder": r["folder_name"]} for r in rows]


def suggest_by_category():
    cats = get_files_by_category(20)
    total_size = sum(c["total_size"] for c in cats) or 1
    results = []
    for c in cats:
        cat = c["category"] or "(empty)"
        results.append({
            "category": cat,
            "count": c["cnt"],
            "total_size": c["total_size"],
            "total_size_mb": round(c["total_size"] / (1024 * 1024), 1),
            "percent": round(c["total_size"] / total_size * 100, 1),
        })
    return sorted(results, key=lambda x: x["total_size"], reverse=True)



def suggest_top10_largest():
    """Top 10 largest files by absolute size, no threshold."""
    rows = get_top10_largest()
    return [{"name": r["file_name"], "path": r["file_path"], "size": r["file_size"],
             "ext": r["file_ext"], "folder": r["folder_name"]} for r in rows]


def get_all_suggestions():
    dups = suggest_duplicates()
    large = suggest_large_files()
    top10 = suggest_top10_largest()
    return {
        "duplicates": dups,
        "large_files": large,
        "top10_largest": top10,
        "by_category": suggest_by_category(),
        "total_duplicates": len(dups),
        "total_large": len(large),
        "total_duplicate_waste": sum(d["waste"] for d in dups),
    }
