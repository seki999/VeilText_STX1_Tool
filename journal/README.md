# VeilText Private HTML Diary

这个目录把 VeilText 扩展成一个适合 VS Code 的本地私密图文日记工作流。

## 工作流

```text
VS Code 写 Markdown
        ↓
拖入 JPG / PNG / WebP / GIF
        ↓
Ctrl+Shift+V 图文预览
        ↓
Ctrl+Shift+B
        ↓
单文件 HTML（图片已 Base64 内嵌）
        ↓
VeilText STX1 / AES-256-GCM 加密
```

## 第一次使用

在仓库根目录运行：

```powershell
.\journal\setup.ps1
```

脚本会：

- 创建或复用根目录的 `.venv`
- 安装现有 VeilText 依赖
- 安装 Markdown 导出依赖
- 创建 `private-diary\images`
- 首次创建 `private-diary\diary.md`

`private-diary/` 默认被 Git 忽略，避免私人日记、图片和生成文件误提交到公开仓库。

## 写日记

打开：

```text
private-diary\diary.md
```

直接写 Markdown。

图片可以从 Windows 文件管理器拖到 Markdown 编辑区。VS Code 会把图片复制到 `private-diary/images/`，并插入 Markdown 图片链接。

预览：

```text
Ctrl + Shift + V
```

## 导出单文件 HTML

当前打开的是 `.md` 文件时：

```text
Ctrl + Shift + B
```

会生成：

```text
diary.single.html
```

HTML 内的本地图片会转换为：

```html
<img src="data:image/jpeg;base64,...">
```

因此 HTML 是一个完整单文件，不依赖外部 images 文件夹。

## 一键导出并加密

VS Code：

```text
Terminal
→ Run Task
→ VeilText Diary: Export + Encrypt current Markdown
```

流程：

1. Markdown 转单文件 HTML
2. 输入两次日记密码
3. 使用现有 STX1 AES-256-GCM 加密 HTML
4. 保存为 `diary.stx1`
5. 自动删除刚生成的明文 `diary.single.html`

这样最终保留的是 STX1 密文。

## 解密并打开图文日记

例如：

```powershell
.\.venv\Scripts\python.exe .\journal\decrypt_html.py .\private-diary\diary.stx1
```

输入密码后会生成：

```text
diary.recovered.html
```

Windows 下随后自动用默认浏览器打开，文字和图片会一起显示。

## 安全说明

- STX1 仍然保持原规范不变；这里加密的明文只是“包含 Base64 图片的 UTF-8 HTML”。
- Markdown 源文件和 `images/` 在编辑阶段仍然是明文。
- `private-diary/` 只是 Git 忽略，并不等于磁盘加密。
- 对真正敏感的日记，完成编辑并确认 `.stx1` 可恢复后，应自行决定是否删除明文 Markdown、图片和 recovered HTML。
- 忘记密码无法恢复。
