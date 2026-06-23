# -*- coding: utf-8 -*-
"""
DocStore (文存仓) - 配置文件
⚠️ 请根据你自己的文件夹修改下面的 SCAN_DIRS 和 FOLDER_CATEGORY。
首次使用建议运行 setup.bat 自动生成配置，或手动修改此文件。
"""

from pathlib import Path

DESKTOP = Path.home() / "Desktop"
EXAMPLE = Path.home() / "Documents"  # ← 替换为你的文件夹根目录

# ↓↓↓ 请替换为你自己的文件夹路径 ↓↓↓
SCAN_DIRS = [
    EXAMPLE / "课程资料",
    EXAMPLE / "项目文件",
    EXAMPLE / "学习笔记",
    EXAMPLE / "获奖证书",
]
# ↑↑↑ 请替换为你自己的文件夹路径 ↑↑↑

SCAN_PATHS = [str(p) for p in SCAN_DIRS]
MONITORED_FOLDERS = [(Path(p).name, p) for p in SCAN_DIRS]

# ↓↓↓ 请替换为你自己的文件夹名 → 分类映射 ↓↓↓
FOLDER_CATEGORY = {
    "课程资料": "课程",
    "项目文件": "项目",
    "学习笔记": "课程",
    "获奖证书": "奖项",
}
# ↑↑↑ 请替换为你自己的文件夹名 → 分类映射 ↑↑↑

SERVER_PORT = 8080

MD5_MAX_SIZE = 500 * 1024 * 1024  # 500 MB

PROJECT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR     = PROJECT_DIR / "src"
DATA_DIR    = PROJECT_DIR / "data"
OUTPUT_DIR  = PROJECT_DIR / "output"
DB_PATH     = DATA_DIR / "index.db"
HTML_PATH   = OUTPUT_DIR / "index.html"
JSON_PATH   = OUTPUT_DIR / "data.json"
TEMPLATE_PATH = PROJECT_DIR / "templates" / "dashboard.html"
