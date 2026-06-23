# 文存仓 DocStore

<div align="center">

**一款零依赖的桌面文件管理仪表盘**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)]()

> 扫描指定文件夹，将文件索引到 SQLite，生成一个自包含的单页 HTML 仪表盘。
> 支持搜索、筛选、重复文件检测、大文件雷达、暗色模式等功能。
> **纯 Python 标准库，零第三方依赖，开箱即用。**

</div>

---

## 预览

<p align="center">
  <img src="output/radar_check.png" alt="大文件雷达 TOP 10 预览" width="600" />
</p>

---

## 功能特点

| 功能 | 说明 |
|---|---|
| 全文搜索 | 支持文件名、路径关键词，按分类、类型、大小筛选 |
| 统计仪表盘 | 文件分类分布、类型 TOP 10、文件夹概览 |
| 重复文件检测 | 按文件名 + MD5 双重检测，自动计算浪费空间 |
| 大文件雷达 TOP 10 | 金银铜牌排名，一目了然的大文件清单 |
| 一键刷新 | 点击按钮即可重新扫描，无需重启服务 |
| 暗色模式 | 跟随系统主题自动切换 |
| 文件夹视图 | 点击文件夹即可查看内部文件明细 |
| 图片预览 | 支持图片文件的在线预览 |

---

## 快速开始

### 环境要求

- Python 3.8+（仅使用标准库，无需 `pip install`）

### 安装与运行

```bash
# 1. 克隆仓库
git clone https://github.com/PENG898/DocStore.git
cd DocStore

# 2. 配置扫描路径（编辑 src/config.py 修改 SCAN_DIRS）

# 3. 一键启动
双击 文存仓.bat
# 或在命令行运行：
python main.py
```

浏览器会自动打开 `http://localhost:8080/` 仪表盘页面。

> 也可以直接点击 GitHub 页面右上角 **Code -> Download ZIP**，解压后运行。

---

## 项目结构

```text
DocStore/
  main.py                # 主入口 - 扫描、导出、生成 HTML
  文存仓.bat             # Windows 一键启动脚本
  src/
    config.py            # 配置文件 - 在这里修改扫描文件夹路径
    db.py                # SQLite 数据库层（WAL 模式）
    scanner.py           # 文件扫描器
    search.py            # 多条件搜索
    suggest.py           # 重复文件 & 大文件建议
  templates/
    dashboard.html       # HTML 模板（CSS/JS 内嵌）
  data/                  # 自动生成 - SQLite 数据库
  output/                # 自动生成 - index.html + data.json
```

---

## 配置说明

编辑 `src/config.py`：

| 变量 | 说明 |
|---|---|
| `SCAN_DIRS` | 要扫描的文件夹路径列表 |
| `FOLDER_CATEGORY` | 文件夹名到分类的映射关系 |
| `MD5_MAX_SIZE` | 计算 MD5 的文件大小上限，默认 500MB |
| `SERVER_PORT` | Web 服务端口，默认 8080 |

---

## 技术栈

| 层级 | 技术 |
|---|---|
| 语言 | Python 3.8+（100% 标准库，零第三方依赖） |
| 数据库 | SQLite（WAL 模式，读写并发） |
| 前端 | 纯 HTML / CSS / JS，无框架 |
| 服务 | Python `http.server` + `ThreadingMixIn` |

---

## 更新日志

### v1.1

- 新增重复文件检测（文件名 + MD5 双重校验）
- 新增大文件雷达 TOP 10（金银铜牌排名）
- 新增一键刷新功能
- 新增暗色模式（跟随系统主题）
- 新增图片在线预览

### v1.0

- 初始版本：文件扫描、SQLite 索引、多条件搜索、统计仪表盘

---

## 贡献

欢迎提交 Issue 和 Pull Request。如果这个项目对你有帮助，请给一个 Star 支持一下。

## 开源协议

[MIT License](LICENSE) (c) 2026 PENG
