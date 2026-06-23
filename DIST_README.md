# 文存仓 DocStore 分发说明

## 解压规范

1. 将 `DocStore.zip` 解压到任意**英文路径**目录，例如 `D:\DocStore`。
2. 解压后目录结构如下：
   ```
   DocStore/
     main.py
     setup.py
     setup.bat
     DIST_README.md
     README.md
     文存仓.bat
     src/
     templates/
     data/          ← setup.bat 运行后自动生成
     output/        ← 首次扫描后自动生成
   ```
3. **不要**把解压路径放在含中文或空格的位置（例如 `C:\Users\张三\Desktop\我的工具`），否则可能导致 Python 编码异常。

## setup.bat 操作步骤

1. 双击 `setup.bat`，脚本会自动检测 Python 环境。
2. 如果提示「未检测到 Python」，请前往 [python.org](https://www.python.org/downloads/) 安装 Python 3.10+，安装时**务必勾选 "Add Python to PATH"**。
3. 安装向导会扫描桌面文件夹并生成 `src/config.py` 配置文件。
4. 配置完成后，脚本会自动生成空白 SQLite 数据库（`data/index.db`），**不会**携带本机扫描记录。
5. 双击 `文存仓.bat` 启动程序，浏览器访问 `http://localhost:8080/` 即可使用。

> **提示**：所有异步扫描线程均为守护线程，关闭 bat 窗口后所有后台任务自动销毁，不会残留进程。

## 常见报错与解决方案

### 1. `'python' 不是内部或外部命令`

- **原因**：Python 未加入系统 PATH。
- **解决**：重新安装 Python，勾选 "Add Python to PATH"；或手动将 Python 安装目录添加到系统环境变量。

### 2. 端口 8080 被占用

- **原因**：其他程序占用了 8080 端口。
- **解决**：关闭占用端口的程序，或修改 `src/config.py` 中的 `SERVER_PORT` 为其他端口（如 8081）。

### 3. `PermissionError: [Errno 13] Access is denied`

- **原因**：目标文件夹无读取/写入权限。
- **解决**：以管理员身份运行 `setup.bat`，或将扫描目录设置为当前用户有完全控制权的文件夹。

### 4. 浏览器显示 `ERR_EMPTY_RESPONSE`

- **原因**：服务器端 Python 进程异常退出。
- **解决**：检查命令行窗口是否有报错信息；确认 Python 版本 ≥ 3.10；尝试重启 `文存仓.bat`。

### 5. `UnicodeDecodeError` 或中文乱码

- **原因**：路径或文件名含特殊字符。
- **解决**：确保 `setup.bat` 和 `文存仓.bat` 以 UTF-8 编码运行（脚本已自动设置 `chcp 65001`）；如仍有问题，将文件移至纯英文路径。

### 6. 数据库锁死 / 扫描卡住

- **原因**：多个进程同时写入 SQLite。
- **解决**：关闭所有 `文存仓.bat` 窗口后重新启动；程序已使用 WAL 模式，正常情况下不会锁死。
