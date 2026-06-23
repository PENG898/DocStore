#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文存仓 DocStore - 安装配置向导
用法: 双击 setup.bat 自动运行，也可 python setup.py

功能:
1. 检测 Python 环境
2. 交互式选择扫描目标（支持桌面文件夹 + 手动输入其他磁盘路径）
3. 生成 src/config.py 配置文件
4. 创建空白 SQLite 数据库（不携带本机扫描记录）
5. 生成文存仓.bat 启动器（使用检测到的精确 Python 路径）
"""

import ctypes
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
DESKTOP = Path.home() / "Desktop"
CONFIG_PATH = PROJECT_DIR / "src" / "config.py"

CAT_RULES = [
    ("课程", ["课程", "学期", "学习", "物联网", "计算机", "数据结构",
              "操作系统", "英语", "数学", "物理", "网络", "编程",
              "软件", "硬件", "电子", "通信"]),
    ("二课", ["二课", "工作", "活动", "志愿", "社团", "实践", "实习"]),
    ("奖项", ["奖", "竞赛", "比赛", "证书", "荣誉", "获奖"]),
    ("自考", ["自考", "自学考试"]),
    ("项目", ["项目", "设计", "开发", "双创", "创业"]),
]


def guess_category(name):
    for cat, keywords in CAT_RULES:
        for kw in keywords:
            if kw in name:
                return cat
    return "其他"


def _show_warning(title, message):
    try:
        ctypes.windll.user32.MessageBoxW(0, message, title, 0x30)
    except Exception:
        print(f"  [!] {title}: {message}")


def _check_path_access(path):
    if not path.exists():
        return False, f"路径不存在: {path}"
    if not path.is_dir():
        return False, f"不是文件夹: {path}"
    try:
        next(path.iterdir())
    except StopIteration:
        pass
    except PermissionError:
        return False, f"无读取权限: {path}"
    except OSError as e:
        return False, f"无法访问: {path} ({e})"
    test_file = path / ".docstore_test"
    try:
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink()
    except (PermissionError, OSError):
        return False, f"无写入权限: {path}"
    return True, ""


def _get_manual_paths():
    """手动输入其他磁盘文件夹路径"""
    paths = []
    print()
    print("  手动添加其他磁盘文件夹：")
    print("  输入完整路径（每行一个，输入空行结束）")
    print("  路径不存在或无权限时会自动跳过")
    print("  示例: D:\\学习资料")
    print("        E:\\竞赛项目")
    print()
    while True:
        path_str = input("    路径: ").strip().strip('"').strip("'")
        if not path_str:
            break
        path = Path(path_str)
        if not path.is_absolute():
            print(f"    [!] 请输入完整路径（如 D:\\学习资料），已跳过")
            continue
        if path in paths:
            print(f"    [!] 已添加过: {path}，跳过")
            continue
        ok, msg = _check_path_access(path)
        if ok:
            paths.append(path)
            print(f"    [√] 已添加: {path}")
        else:
            print(f"    [!] {msg}，已跳过")
    if paths:
        print(f"\n  共添加 {len(paths)} 个外部文件夹")
    return paths


def _select_with_validation(folders):
    while True:
        print()
        print("  输入编号选择要扫描的文件夹（空格分隔）")
        print("  直接回车 = 全部桌面文件夹")
        print("  输入 0 = 手动添加其他磁盘文件夹（如 D:\\学习资料）")
        print("  示例: 1 3 5（选桌面）| 0（仅手动输入）| 1 3 0（桌面+手动）")
        print()

        choice = input("  选择: ").strip()

        if choice == "":
            selected = list(folders)
        else:
            parts = choice.split()
            ids = []
            manual_requested = False
            for p in parts:
                try:
                    v = int(p)
                    if v == 0:
                        manual_requested = True
                    elif 1 <= v <= len(folders):
                        ids.append(v - 1)
                except ValueError:
                    pass
            selected = [folders[i] for i in ids]
            if manual_requested:
                manual_paths = _get_manual_paths()
                for mp in manual_paths:
                    if mp not in selected:
                        selected.append(mp)
            if not selected:
                print("  [!] 未选择任何文件夹，请重新选择")
                continue

        bad = []
        good = []
        for f in selected:
            ok, msg = _check_path_access(f)
            if ok:
                good.append(f)
            else:
                bad.append(msg)

        if not bad:
            return good

        warn_msg = "以下目录无法访问:\n\n" + "\n".join(f"  - {m}" for m in bad) + "\n\n请重新选择可用目录。"
        print()
        for msg in bad:
            print(f"  [!] {msg}")
        _show_warning("目录校验失败", warn_msg)
        print("  请重新选择...")


def _init_blank_database():
    """创建空白 SQLite 数据库，仅建表不写入扫描记录。"""
    data_dir = PROJECT_DIR / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    # 切换到 src 目录以便 import db 模块
    sys.path.insert(0, str(PROJECT_DIR / "src"))
    from db import init_db, get_connection

    init_db()
    print("  [√] 空白数据库已创建: data/index.db")

    # 确认数据库确实为空
    conn = get_connection()
    file_count = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
    folder_count = conn.execute("SELECT COUNT(*) FROM folders").fetchone()[0]
    conn.close()

    if file_count == 0 and folder_count == 0:
        print("  [√] 数据库状态: 空（无扫描记录）")
    else:
        print(f"  [!] 警告: 数据库非空（{folder_count} 个文件夹, {file_count} 个文件）")


def main():
    print()
    print("=" * 50)
    print("  文存仓 DocStore - 安装配置向导")
    print("=" * 50)
    print()

    if CONFIG_PATH.exists():
        content = CONFIG_PATH.read_text(encoding="utf-8")
        if "SCAN_DIRS" in content and "DESKTOP" in content:
            print("  检测到已有配置。")
            ans = input("  重新配置？(y/N): ").strip().lower()
            if ans != "y":
                print("  跳过配置。")
                # 仍然确保数据库存在
                _init_blank_database()
                return
            print()

    if not DESKTOP.exists():
        print("  [!] 未找到桌面目录")
        print("  请手动编辑 src/config.py 设置扫描路径")
        return

    folders = sorted([
        f for f in DESKTOP.iterdir()
        if f.is_dir() and not f.name.startswith((".", "$"))
    ])

    if not folders:
        print("  桌面上没有找到文件夹")
        return

    print(f"  桌面上找到 {len(folders)} 个文件夹：")
    print()
    for i, f in enumerate(folders, 1):
        print(f"    [{i:2d}] {f.name}")

    print()
    print("  提示: 可勾选桌面文件夹，也可输入 0 添加 D/E/F 盘其他资料目录")

    selected = _select_with_validation(folders)
    if not selected:
        print("  未选择任何文件夹，配置已取消。")
        return

    print()
    print("  分类设置（回车=推荐值，1=课程 2=二课 3=奖项 4=自考 5=项目 6=其他）")
    print()

    CK = {"1": "课程", "2": "二课", "3": "奖项", "4": "自考", "5": "项目", "6": "其他"}
    fc = {}
    for f in selected:
        g = guess_category(f.name)
        a = input(f"    {f.name:<24s} [{g}] -> ").strip()
        fc[f.name] = CK.get(a, g)

    sd_lines = []
    for f in selected:
        if f.parent == DESKTOP:
            sd_lines.append(f'    DESKTOP / "{f.name}",')
        else:
            sd_lines.append(f'    Path(r"{f}"),')
    sd = "\n".join(sd_lines)
    cl = "\n".join(f'    "{n}": "{c}",' for n, c in fc.items())

    cfg = f'''# -*- coding: utf-8 -*-
"""
DocStore (文存仓) - 配置文件
由 setup.py 自动生成，可随时手动修改。
"""

from pathlib import Path

DESKTOP = Path.home() / "Desktop"

SCAN_DIRS = [
{sd}
]

SCAN_PATHS = [str(p) for p in SCAN_DIRS]
MONITORED_FOLDERS = [(p.name, str(p)) for p in SCAN_DIRS]

FOLDER_CATEGORY = {{
{cl}
}}

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
'''

    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(cfg, encoding="utf-8")
    print()
    print("  [√] 配置已保存到 src/config.py")

    # 创建空白数据库（不执行扫描）
    _init_blank_database()

    # 生成启动器（使用检测到的精确 Python 路径）
    python_exe = sys.executable.replace("\\", "\\\\")
    launcher = f'''@echo off
chcp 65001 >nul 2>nul
title 文存仓 DocStore
cd /d "%~dp0"

echo  ============================================
echo        文存仓 DocStore 正在启动中...
echo  ============================================
echo.

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080 ^| findstr LISTENING') do (
    echo  [i] 正在释放端口 8080 (PID: %%a^)...
    taskkill /F /PID %%a >nul 2>nul
)

echo  启动后请在浏览器中使用
echo  访问地址: http://localhost:8080/
echo.
"{python_exe}" main.py
echo.
echo  文存仓已关闭或启动失败。
echo.
pause
'''
    launcher_path = PROJECT_DIR / "\u6587\u5b58\u4ed3.bat"
    launcher_path.write_text(launcher, encoding="utf-8-sig")

    print()
    print("=" * 50)
    print("  配置完成！")
    print("  以后双击「文存仓.bat」即可启动")
    print("=" * 50)


if __name__ == "__main__":
    main()
