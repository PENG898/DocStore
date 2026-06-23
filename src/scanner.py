#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scanner engine - walk configured folders, compute MD5 for potential
duplicates, and upsert everything into the SQLite index.
"""

import hashlib
import os
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from db import upsert_folder, add_files_to_folder, get_folder, clear_hash_for_folder, remove_stale_files
from config import SCAN_DIRS, MONITORED_FOLDERS, FOLDER_CATEGORY, MD5_MAX_SIZE

# ── Directories to skip (SDK / library noise) ──────────────────
SKIP_DIRS = {
    "CMSIS", "STM32F1xx_HAL_Driver", "STM32F1xx", "STM32_NNExamples",
    "DSP_Lib", "FAT", "FreeRTOS", "MAM", "MDK-ARM", "Objects",
    "Startup", "Drivers", "Core", "Inc", "Src", "Legacy", "RTE",
    "DebugConfig", "Listings", "libs", "lib", "include", "Source",
    "Micrium", "Doc", "Common", "RefLibs",
    "arm_common_tests", "arm_const_structs", "arm_matrix_example",
    "arm_convolution_example", "arm_dotproduct_example", "arm_fft_bin_example",
    "arm_fir_example", "arm_graphic_equalizer_example", "arm_linear_interp_example",
    "arm_signal_converge_example", "arm_sin_cos_example",
    "arm_variance_example", "BasicMathFunctions", "ComplexMathFunctions",
    "ControllerFunctions", "FastMathFunctions", "FilteringFunctions",
    "HelperFunctions", "Intrinsics", "MatrixFunctions", "StatisticsFunctions",
    "SupportFunctions", "TransformFunctions", "arm_class_marks_example",
    "cifar10", "gru", "nn_test", "Ref_Implementations",
    "arm_nn_examples", "ucos", "uCOS-II", "uCOSIII", "micrium",
    "ARM", "GCC", "IAR", "linker", "gcc", "iar", "arm",
    "JTest", "platform", "basic_math_tests",
    "complex_math_tests", "controller_tests", "fast_math_tests",
    "filtering_tests", "intrinsics_tests", "matrix_tests",
    "statistics_tests", "support_tests", "transform_tests",
    "arr_desc", "opt_arg", "util", "ARMCC", "ARMCLANG",
    "DspLibTest_FVP", "DspLibTest_MPS2",
    "activation_tests", "convolution_tests", "fully_connected_tests",
    "nnsupport_tests", "pooling_tests", "softmax_tests",
    "Template", "arm_cm", "arm_cmse",
    "proteus", "keil", "uvprojx", "uvoptx", "project", "cproject",
    "workspace", ".project", ".cproject", ".setting",
}

# ── Extension -> human-readable type ────────────────────────────
EXT_TYPE_MAP = {
    ".c": "C源码", ".h": "C头文件",
    ".cpp": "C++源码", ".hpp": "C++头文件",
    ".s": "汇编", ".asm": "汇编",
    ".py": "Python", ".java": "Java",
    ".doc": "Word文档", ".docx": "Word文档",
    ".ppt": "PPT", ".pptx": "PPT",
    ".xls": "Excel", ".xlsx": "Excel",
    ".pdf": "PDF",
    ".zip": "压缩包", ".rar": "压缩包",
    ".7z": "压缩包", ".tar": "压缩包", ".gz": "压缩包",
    ".mp4": "视频", ".avi": "视频", ".mkv": "视频",
    ".mov": "视频", ".wmv": "视频",
    ".mp3": "音频", ".wav": "音频",
    ".jpg": "图片", ".jpeg": "图片", ".png": "图片",
    ".bmp": "图片", ".gif": "图片",
    ".svg": "矢量图", ".ico": "图标",
    ".iso": "镜像", ".vbox": "虚拟机配置", ".vdi": "虚拟机磁盘",
    ".uvprojx": "Keil工程", ".uvoptx": "Keil配置",
    ".mxproject": "Proteus工程", ".pdsprj": "Proteus工程", ".pdsbak": "Proteus备份",
    ".uproj": "STM32CubeIDE工程", ".epro": "立创EDA工程",
    ".xmind": "思维导图", ".md": "Markdown",
    ".cfg": "配置文件", ".ini": "配置文件", ".conf": "配置文件",
    ".db": "数据库", ".sql": "SQL",
    ".exe": "可执行文件", ".dll": "动态库",
    ".apk": "安卓应用",
    ".hex": "HEX固件", ".bin": "二进制固件",
    ".axf": "ELF固件", ".elf": "ELF固件",
    ".step": "3D模型", ".stp": "3D模型",
    ".psd": "Photoshop",
}

# Category for grouping in advanced filter
EXT_CATEGORY_MAP = {}
_doc_exts = {".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".pdf", ".txt", ".md", ".rtf"}
_vid_exts = {".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv"}
_img_exts = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".svg", ".psd", ".ico"}
_audio_exts = {".mp3", ".wav", ".flac", ".aac"}
_code_exts = {".c", ".h", ".cpp", ".hpp", ".py", ".java", ".js", ".ts", ".go", ".rs"}
_archive_exts = {".zip", ".rar", ".7z", ".tar", ".gz"}

for e in _doc_exts: EXT_CATEGORY_MAP[e] = "document"
for e in _vid_exts: EXT_CATEGORY_MAP[e] = "video"
for e in _img_exts: EXT_CATEGORY_MAP[e] = "image"
for e in _audio_exts: EXT_CATEGORY_MAP[e] = "audio"
for e in _code_exts: EXT_CATEGORY_MAP[e] = "code"
for e in _archive_exts: EXT_CATEGORY_MAP[e] = "archive"


def get_file_type(ext):
    if not ext:
        return "未知"
    return EXT_TYPE_MAP.get(ext.lower(), "其他")


def should_skip_dir(dirname):
    return dirname in SKIP_DIRS


def compute_md5(filepath, chunk_size=8192):
    """Compute MD5 hash of a file, reading in chunks to handle large files."""
    h = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()
    except (OSError, PermissionError):
        return None


def scan_folder(folder_name, folder_path):
    """Walk a folder tree and return a list of file dicts."""
    files = []
    if not os.path.exists(folder_path):
        return files

    for root, dirs, filenames in os.walk(folder_path):
        dirs[:] = [d for d in dirs if not should_skip_dir(d)]

        for fname in filenames:
            fpath = os.path.join(root, fname)
            try:
                stat = os.stat(fpath)
                fsize = stat.st_size
                ext = Path(fname).suffix
                ftype = get_file_type(ext)
                category = FOLDER_CATEGORY.get(folder_name, "其他")

                if fsize > 2 * 1024 * 1024 * 1024:
                    continue

                files.append({
                    "file_path": fpath,
                    "file_name": fname,
                    "file_ext": ext,
                    "file_size": fsize,
                    "file_type": ftype,
                    "category": category,
                    "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                })
            except (OSError, PermissionError):
                continue

    return files


def _hash_matching_files(all_files):
    """
    Two-pass duplicate detection:
    1. Group files by (size, basename) -- cheap pre-filter.
    2. Compute MD5 only for files in groups with 2+ members.
    This avoids hashing every single file.
    """
    # Group by size (files with unique sizes cannot be duplicates)
    size_groups = defaultdict(list)
    for f in all_files:
        size_groups[f["file_size"]].append(f)

    # Only hash files in size-groups with 2+ members and under size threshold
    to_hash = []
    for size, group in size_groups.items():
        if len(group) >= 2 and size <= MD5_MAX_SIZE and size > 0:
            to_hash.extend(group)

    for f in to_hash:
        f["file_hash"] = compute_md5(f["file_path"])


def full_scan(progress_callback=None):
    """Full scan of all configured folders."""
    total_files = 0
    total_added = 0

    # Phase 1: Collect all files
    all_files = []
    folder_data = []
    for folder_name, folder_path in MONITORED_FOLDERS:
        fid = upsert_folder(folder_name, folder_path)
        files = scan_folder(folder_name, folder_path)
        all_files.extend(files)
        folder_data.append((fid, files))
        if progress_callback:
            progress_callback(folder_name, len(files), 0)

    # Phase 2: Hash potential duplicates
    _hash_matching_files(all_files)

    # Phase 3: Insert into DB and clean stale entries
    for fid, files in folder_data:
        folder_files = [f for f in all_files if f in files]
        added = add_files_to_folder(fid, folder_files)
        total_added += added
        total_files += len(folder_files)
        # Remove files from DB that no longer exist on disk
        current_paths = [f["file_path"] for f in folder_files]
        stale_removed = remove_stale_files(fid, current_paths)
        if stale_removed:
            print(f"  Cleaned {stale_removed} stale entries")

    return total_files, total_added, 0


def get_scan_summary():
    import db
    stats = db.get_folder_stats()
    total_files = db.get_file_count()
    db_size = db.get_db_size()
    categories = db.get_files_by_category(20)
    extensions = db.get_files_by_extension(20)
    return {
        "folders": stats,
        "total_files": total_files,
        "db_size": db_size,
        "categories": categories,
        "extensions": extensions,
    }
