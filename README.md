# VeilText STX1 Encryption + Recovery

这是 VeilText 的独立 STX1 加密 / 恢复工具。普通 Windows 用户可以直接使用单文件 `VeilText_STX1_Tool.exe`，无需安装 Python；同时完整保留 Python 源码和 STX1 规范，作为长期恢复保险。

它既可以生成与 VeilText STX1 规范兼容的密文，也可以在原始 VeilText.exe、WPF 程序或原电脑已经丢失的情况下独立恢复原文。

只要仍然拥有：

- 完整的 `STX1:...` 密文
- 正确密码

就可以通过 Windows 单文件 EXE 恢复原文。

即使未来 EXE 因 Windows 兼容性变化而无法运行，只要 Python 生态仍可用，也可以依据本仓库保留的 Python 源码和 `STX1-SPEC.md` 独立恢复。

## 功能

程序支持：

1. 直接粘贴明文并生成 STX1 密文
2. 直接粘贴完整 STX1 密文并恢复明文
3. 加密 UTF-8 文本文件
4. 解密 / 恢复 STX1 文本文件
5. 将结果保存为 UTF-8 文本文件


## 私密 HTML 图文日记（VS Code）

本仓库现在也可以作为一个本地 **Private HTML Diary** 工作流使用：

```text
VS Code 写 Markdown
        ↓
拖入图片
        ↓
Ctrl+Shift+V 图文预览
        ↓
Ctrl+Shift+B
        ↓
单文件 HTML（图片 Base64 内嵌）
        ↓
STX1 / AES-256-GCM 加密
        ↓
diary.stx1
```

第一次使用：

```powershell
.\journal\setup.ps1
```

之后打开：

```text
private-diary\diary.md
```

直接写文字，并把 JPG / PNG / WebP / GIF 图片拖进 VS Code Markdown 编辑区即可。

### 导出单文件 HTML

按：

```text
Ctrl + Shift + B
```

会把当前 Markdown 转为：

```text
xxx.single.html
```

所有本地图片都会转换成 Base64 并嵌入 HTML，因此 HTML 可以脱离 `images/` 文件夹独立打开。

### 一键导出 + 加密

在 VS Code 中执行：

```text
Terminal
→ Run Task
→ VeilText Diary: Export + Encrypt current Markdown
```

会：

1. 生成单文件 HTML
2. 要求输入并确认密码
3. 使用现有 STX1 AES-256-GCM 加密 HTML
4. 输出 `xxx.stx1`
5. 删除临时生成的明文 `xxx.single.html`

解密示例：

```powershell
.\.venv\Scripts\python.exe .\journal\decrypt_html.py .\private-diary\diary.stx1
```

正确输入密码后会恢复为 `diary.recovered.html`，Windows 下自动使用默认浏览器打开，文字和图片会一起显示。

详细说明见：

```text
journal/README.md
```

> 安全提醒：Markdown 源文件和图片在编辑阶段仍然是明文。`private-diary/` 默认加入 `.gitignore`，避免误提交到公开 GitHub 仓库，但 Git 忽略本身不等于磁盘加密。对真正敏感的内容，应在确认加密文件可恢复后自行管理或删除明文材料。

## STX1 加密格式

本工具严格对应现有 VeilText STX1：

- AES-256-GCM
- PBKDF2-HMAC-SHA256
- 600,000 iterations
- Salt: 16 bytes，随机生成
- Nonce: 12 bytes，随机生成
- Authentication Tag: 16 bytes
- AAD: `STX1|AES-256-GCM|PBKDF2-SHA256|600000`
- Password encoding: UTF-8，不做 Unicode normalization

密文格式：

```text
STX1:Base64(UTF-8 JSON)
```

JSON 字段：

- `Version = 1`
- `Algorithm = AES-256-GCM`
- `Kdf = PBKDF2-SHA256`
- `Iterations = 600000`
- `Salt = Base64(16 bytes)`
- `Nonce = Base64(12 bytes)`
- `Ciphertext = Base64(cipher bytes)`
- `Tag = Base64(16 bytes)`

因此：

- 原 VeilText 生成的 STX1 密文可以继续由本工具恢复。
- 本工具生成的 STX1 密文遵守同一格式，可供任何正确实现 STX1 规范的程序解密。

## Windows 单文件 EXE（普通用户推荐）

发布版目标文件：

```text
VeilText_STX1_Tool.exe
```

这是 **Portable 单文件程序**：

- 不需要预先安装 Python
- 不需要运行 `pip install`
- 不需要虚拟环境
- 不需要安装器
- 双击即可打开图形界面
- EXE 内包含 Python 运行时及所需的 `cryptography` 依赖
- 加密格式仍然严格保持 STX1 v1，不因打包方式发生变化

### 从 GitHub Actions 下载 EXE

仓库已包含：

```text
.github/workflows/build-windows-exe.yml
```

每次相关源码推送到 `main` 后，GitHub 会在 Windows Runner 上：

1. 安装构建用 Python
2. 安装运行依赖和 PyInstaller
3. 运行 STX1 自动兼容性测试
4. 构建单文件 GUI EXE
5. 计算 SHA-256
6. 上传构建产物 `VeilText_STX1_Tool-Windows-x64`

构建产物包含：

```text
VeilText_STX1_Tool.exe
SHA256.txt
```

进入仓库的 **Actions → Build Windows EXE → 最新成功运行 → Artifacts** 即可下载。

> GitHub Actions 的 Artifact 有保留期限。因此，重要版本建议下载后自行备份，或后续再发布到 GitHub Releases。

## 本地构建 EXE（仅开发者需要 Python）

推荐使用 Python 虚拟环境进行构建，这样可以避免污染系统 Python，也能让不同项目之间的依赖保持隔离。

推荐方式：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -r requirements-build.txt
.\build_exe.ps1
```

其中：

- `.venv` 仅用于开发和重新构建 EXE
- 最终生成的 `VeilText_STX1_Tool.exe` 不依赖这个虚拟环境
- 普通用户运行 EXE 时不需要安装 Python

如果已经有合适的 Python 环境，也可以直接执行：

```powershell
.\build_exe.ps1
```

脚本会自动：

- 安装 `requirements.txt`
- 安装 `requirements-build.txt` 中的 PyInstaller
- 执行全部单元测试
- 构建 `--onefile --windowed` GUI 程序
- 输出 SHA-256

生成文件：

```text
dist\VeilText_STX1_Tool.exe
```

这里的 Python **只用于开发/重新打包**。最终生成的 EXE 在目标 Windows 电脑上运行时不需要 Python。

## Python 源码恢复模式（长期保险）

本仓库继续保留完整 Python 实现，不依赖 EXE：

- `veiltext_stx1_recovery.py`：核心加密 / 解密逻辑
- `veiltext_stx1_gui.py`：Tkinter GUI
- `requirements.txt`：运行依赖
- `STX1-SPEC.md`：独立格式规范
- `test_stx1.py`：兼容性测试

建议 Python 3.10 或更高版本。

```powershell
python -m pip install -r requirements.txt
```

## Python 源码版安装

建议 Python 3.10 或更高版本。

```powershell
python -m pip install -r requirements.txt
```

## 图形界面（推荐）

使用 Python 源码模式时，Windows 上可以运行：

```powershell
python veiltext_stx1_gui.py
```

或者双击：

```text
run_gui.bat
```

GUI 提供：

- 左侧 Plaintext 明文编辑区
- 右侧 STX1 Ciphertext 密文编辑区
- 密码与确认密码输入框
- Encrypt 加密按钮
- Decrypt / Recover 解密恢复按钮
- 打开明文文件 / 打开密文文件
- 保存明文 / 保存密文
- 复制明文 / 复制密文
- 显示 / 隐藏密码
- 状态提示
- English / 简体中文 界面切换（默认简体中文）

GUI 只是界面层，底层仍调用 `veiltext_stx1_recovery.py` 中同一套 STX1 加密 / 解密函数，因此与命令行版使用完全相同的 STX1 v1 格式。

## 命令行模式

如果需要最简单、最长期稳定的备用方式，仍可以运行：

```powershell
python veiltext_stx1_recovery.py
```

启动后：

```text
VeilText STX1 Encryption + Recovery Tool
----------------------------------------
1. Encrypt pasted text
2. Decrypt / recover pasted STX1 ciphertext
3. Encrypt UTF-8 text file
4. Decrypt / recover STX1 text file
5. Exit
```

### 加密粘贴文本

选择 `1`。

可以输入多行明文。输入完成后，在单独一行输入：

```text
::END::
```

然后输入两次密码确认。

程序会生成完整的：

```text
STX1:...
```

密文。

### 恢复粘贴密文

选择 `2`，粘贴完整的单行 `STX1:...` 密文，然后输入密码。

### 加密文件

选择 `3`，指定 UTF-8 明文文件、输出文件和密码。

默认输出文件：

```text
encrypted_stx1.txt
```

### 恢复文件

选择 `4`，指定包含完整 STX1 密文的文本文件和输出文件，然后输入密码。

默认输出文件：

```text
recovered.txt
```

## 自动兼容性测试

项目包含 `test_stx1.py`，可直接运行：

```powershell
python -m unittest -v
```

测试覆盖：

- 中文 / 日文 / 英文 / Emoji 往返加密解密
- STX1 v1 JSON 字段和参数检查
- 随机 Salt / Nonce 导致相同明文每次产生不同密文
- 错误密码必须解密失败
- 空明文和空密码的新加密请求会被拒绝

## Python API

也可以直接导入使用：

```python
from veiltext_stx1_recovery import encrypt_veiltext, decrypt_veiltext

ciphertext = encrypt_veiltext("秘密文本", "my-password")
plaintext = decrypt_veiltext(ciphertext, "my-password")
```

文件 API：

```python
from veiltext_stx1_recovery import encrypt_file, decrypt_file

encrypt_file("plain.txt", "encrypted.txt", "my-password")
decrypt_file("encrypted.txt", "recovered.txt", "my-password")
```

## 兼容性原则

为了长期可恢复性，本项目不会随意修改 STX1 v1 的以下参数：

- AES-256-GCM
- PBKDF2-HMAC-SHA256
- 600,000 iterations
- Salt / Nonce / Tag 长度
- AAD
- JSON 字段含义
- `STX1:` 前缀

如果未来需要升级算法，建议创建新的格式版本（例如 STX2），而不是改变 STX1 的定义。

## 长期保存建议

建议同时保存 **EXE + Python 源码 + STX1 规范**，并与重要密文分开备份到多个位置，例如：

- 本地电脑
- 外置硬盘 / U 盘
- 云盘

密码不要和密文放在同一个地方。

请长期保留：

- `VeilText_STX1_Tool.exe`（方便直接使用）
- `veiltext_stx1_recovery.py`（最重要的源码保险）
- `veiltext_stx1_gui.py`
- `requirements.txt`
- `requirements-build.txt`
- `STX1-SPEC.md`
- `build_exe.ps1`
- 本 README
- 一份已知明文对应的测试密文

这样未来即使 VeilText 主程序已经无法运行，也可以使用 Python 独立加密和恢复 STX1 数据。

## 注意

- 忘记密码无法恢复。
- 密文被破坏或修改后，AES-GCM 验证会失败。
- 每次加密都会随机生成新的 Salt 和 Nonce，所以相同明文和相同密码多次加密得到不同密文，这是正常且必要的安全特性。
- Base64 只是编码，不是加密。
- 此工具不依赖 Windows DPAPI、TPM、当前 Windows 用户账户或原电脑。
