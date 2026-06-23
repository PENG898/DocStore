# DocStore / \u6587\u5b58\u4ed3

\u4e00\u6b3e\u8f7b\u91cf\u7ea7\u7684\u684c\u9762\u6587\u4ef6\u7ba1\u7406\u4eea\u8868\u76d8\u3002\u626b\u63cf\u4f60\u6307\u5b9a\u7684\u6587\u4ef6\u5939\uff0c\u5c06\u6240\u6709\u6587\u4ef6\u7d22\u5f15\u5230 SQLite \u6570\u636e\u5e93\uff0c\u751f\u6210\u4e00\u4e2a\u5355\u9875 HTML \u4eea\u8868\u76d8\uff0c\u652f\u6301\u641c\u7d22\u3001\u7b5b\u9009\u3001\u91cd\u590d\u6587\u4ef6\u68c0\u6d4b\u3001\u5927\u6587\u4ef6\u96f7\u8fbe\u7b49\u529f\u80fd\u3002

**Zero dependencies \u00b7 Pure Python stdlib \u00b7 Single HTML output \u00b7 Works offline**

---

## \u2728 \u529f\u80fd\u7279\u70b9

| \u529f\u80fd | \u8bf4\u660e |
|---------|------|
| \ud83d\udd0d \u5168\u6587\u641c\u7d22 | \u652f\u6301\u6587\u4ef6\u540d\u3001\u8def\u5f84\u5173\u952e\u8bcd\uff0c\u6309\u5206\u7c7b/\u7c7b\u578b/\u5927\u5c0f\u7b5b\u9009 |
| \ud83d\udcca \u7edf\u8ba1\u4eea\u8868\u76d8 | \u6587\u4ef6\u5206\u7c7b\u5206\u5e03\u3001\u7c7b\u578b TOP 10\u3001\u6587\u4ef6\u5939\u6982\u89c8 |
| \ud83e\uddca \u91cd\u590d\u6587\u4ef6\u68c0\u6d4b | \u6309\u6587\u4ef6\u540d + MD5 \u53cc\u91cd\u68c0\u6d4b\uff0c\u81ea\u52a8\u8ba1\u7b97\u6d6a\u8d39\u7a7a\u95f4 |
| \ud83d\udce1 \u5927\u6587\u4ef6\u96f7\u8fbe TOP 10 | \u91d1\u94f6\u94dc\u5956\u724c\u6392\u540d\uff0c\u4e00\u76ee\u4e86\u7136\u7684\u5927\u6587\u4ef6\u6e05\u5355 |
| \ud83d\udd04 \u4e00\u952e\u5237\u65b0 | \u70b9\u51fb\u6309\u94ae\u5373\u53ef\u91cd\u65b0\u626b\u63cf\uff0c\u65e0\u9700\u91cd\u542f |
| \ud83c\udfa8 \u6697\u8272\u6a21\u5f0f | \u8ddf\u968f\u7cfb\u7edf\u4e3b\u9898\u81ea\u52a8\u5207\u6362 |
| \ud83d\udcc2 \u6587\u4ef6\u5939\u89c6\u56fe | \u70b9\u51fb\u6587\u4ef6\u5939\u5373\u53ef\u67e5\u770b\u5185\u90e8\u6587\u4ef6 |

---

## \ud83d\ude80 \u5feb\u901f\u5f00\u59cb

### 1. \u5b89\u88c5 Python

\u9700\u8981 Python 3.8+\uff0c\u65e0\u4efb\u4f55\u7b2c\u4e09\u65b9\u4f9d\u8d56\uff08\u5168\u90e8\u4f7f\u7528\u6807\u51c6\u5e93\uff09\u3002

\u4e0b\u8f7d\u5730\u5740\uff1a[python.org](https://www.python.org/downloads/)

### 2. \u4e0b\u8f7d\u672c\u9879\u76ee

```bash
git clone https://github.com/YOUR_USERNAME/DocStore.git
cd DocStore
```

\u6216\u8005\u76f4\u63a5\u70b9\u51fb GitHub \u9875\u9762\u53f3\u4e0a\u89d2 **Code \u2192 Download ZIP**\uff0c\u89e3\u538b\u5373\u53ef\u3002

### 3. \u914d\u7f6e\u4f60\u7684\u6587\u4ef6\u5939

\u7f16\u8f91 `src/config.py`\uff0c\u4fee\u6539 `SCAN_DIRS` \u5217\u8868\uff0c\u6307\u5411\u4f60\u60f3\u626b\u63cf\u7684\u6587\u4ef6\u5939\uff1a

```python
SCAN_DIRS = [
    DESKTOP / "\u6211\u7684\u8bfe\u7a0b",
    DESKTOP / "\u9879\u76ee",
    DESKTOP / "\u5b66\u4e60\u8d44\u6599",
]

FOLDER_CATEGORY = {
    "\u6211\u7684\u8bfe\u7a0b": "\u8bfe\u7a0b",
    "\u9879\u76ee": "\u9879\u76ee",
    "\u5b66\u4e60\u8d44\u6599": "\u8bfe\u7a0b",
}
```

### 4. \u542f\u52a8

\u53cc\u51fb `\u6587\u5b58\u4ed3.bat`\uff0c\u6216\u5728\u547d\u4ee4\u884c\u8fd0\u884c\uff1a

```bash
python main.py
```

\u6d4f\u89c8\u5668\u4f1a\u81ea\u52a8\u6253\u5f00\u4eea\u8868\u76d8\u9875\u9762\u3002

---

## \ud83d\udcc1 \u9879\u76ee\u7ed3\u6784

```
DocStore/
  main.py              # \u4e3b\u5165\u53e3 \u2014 \u626b\u63cf\u3001\u5bfc\u51fa\u3001\u751f\u6210 HTML
  \u6587\u5b58\u4ed3.bat               # Windows \u4e00\u952e\u542f\u52a8
  src/
    config.py          # \u2b50 \u914d\u7f6e\u6587\u4ef6 \u2014 \u4fee\u6539\u8fd9\u91cc\u7684\u6587\u4ef6\u5939\u8def\u5f84
    db.py              # SQLite \u6570\u636e\u5e93\u5c42
    scanner.py         # \u6587\u4ef6\u626b\u63cf\u5668
    search.py          # \u591a\u6761\u4ef6\u641c\u7d22
    suggest.py         # \u91cd\u590d\u6587\u4ef6 & \u5927\u6587\u4ef6\u5efa\u8bae
  templates/
    dashboard.html     # HTML \u6a21\u677f\uff08CSS/JS \u5185\u5d4c\uff09
  data/                # \u81ea\u52a8\u751f\u6210 \u2014 SQLite \u6570\u636e\u5e93
  output/              # \u81ea\u52a8\u751f\u6210 \u2014 index.html + data.json
```

---

## \ud83d\udd27 \u81ea\u5b9a\u4e49\u914d\u7f6e

\u7f16\u8f91 `src/config.py`\uff1a

| \u53d8\u91cf | \u8bf4\u660e |
|------|------|
| `SCAN_DIRS` | \u8981\u626b\u63cf\u7684\u6587\u4ef6\u5939\u5217\u8868 |
| `FOLDER_CATEGORY` | \u6587\u4ef6\u5939\u540d \u2192 \u5206\u7c7b\u6620\u5c04 |
| `MD5_MAX_SIZE` | \u8ba1\u7b97 MD5 \u7684\u6587\u4ef6\u5927\u5c0f\u4e0a\u9650\uff08\u9ed8\u8ba4 500MB\uff09 |
| `SERVER_PORT` | Web \u670d\u52a1\u7aef\u53e3\uff08\u9ed8\u8ba4 8080\uff09 |

---

## \ud83d\udce6 \u6280\u672f\u6808

- **\u8bed\u8a00**\uff1aPython 3.8+ (100% \u6807\u51c6\u5e93\uff0c\u96f6\u4f9d\u8d56)
- **\u6570\u636e\u5e93**\uff1aSQLite (WAL \u6a21\u5f0f)
- **\u524d\u7aef**\uff1a\u7eaf HTML/CSS/JS\uff0c\u65e0\u6846\u67b6
- **\u670d\u52a1\u5668**\uff1aPython `http.server` + `ThreadingMixIn`

---

## \ud83d\udcdd \u66f4\u65b0\u65e5\u5fd7

- **v1.0** \u2014 \u521d\u59cb\u7248\u672c\uff1a\u6587\u4ef6\u626b\u63cf\u3001\u7d22\u5f15\u3001\u641c\u7d22\u3001\u4eea\u8868\u76d8
- **v1.1** \u2014 \u65b0\u589e\u91cd\u590d\u6587\u4ef6\u68c0\u6d4b\u3001\u5927\u6587\u4ef6\u96f7\u8fbe TOP 10\u3001\u4e00\u952e\u5237\u65b0\u3001\u6697\u8272\u6a21\u5f0f

---

## \ud83d\udc9d Contributing

PR \u548c Issue \u90fd\u6b22\u8fce\uff01\u5982\u679c\u4f60\u89c9\u5f97\u8fd9\u4e2a\u9879\u76ee\u6709\u7528\uff0c\u7ed9\u4e2a Star \u2b50

## \ud83d\udcc4 License

[MIT](LICENSE) \u00a9 2026 PENG


---

## GitHub 开源发布流程

如果你想把这个项目 fork 到自己的 GitHub 并开源，按以下步骤操作：

### 1. 初始化本地 Git 仓库

`ash
cd DocStore
git init
git add .
git commit -m "feat: 文存仓 DocStore v1.1 初始版本"
`

### 2. 在 GitHub 创建远程仓库

1. 打开 [github.com/new](https://github.com/new)
2. Repository name 填 DocStore（或你喜欢的名字）
3. 选择 **Public**
4. **不要**勾选 Initialize with README / .gitignore / License（本地已经有了）
5. 点击 Create repository

### 3. 关联远程仓库并推送

`ash
git remote add origin https://github.com/YOUR_USERNAME/DocStore.git
git branch -M main
git push -u origin main
`

### 4. 设置仓库信息

在 GitHub 仓库页面：
- **About** 区域点击齿轮图标，填入项目描述和 Topics（如 python, ile-manager, dashboard, sqlite）
- 勾选 **Use your repository description as the social preview**

### 5. 创建第一个 Release

1. 进入仓库页面 → Releases → Create a new release
2. Tag 填 1.1
3. Title 填 文存仓 DocStore v1.1
4. 描述写主要功能变更
5. 点击 Publish release

### 日常更新流程

`ash
# 修改代码后
git add .
git commit -m "fix: 修复了xxx问题"
git push

# 发新版本时
git tag v1.2
git push --tags
`

### 注意事项

- .gitignore 已配置好，data/index.db 和 output/ 目录不会被提交
- LICENSE 文件（MIT）已就绪，开源合规
- 不要把个人文件路径硬编码到 config.py 后提交；建议用示例路径