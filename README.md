# VeilText STX1 Recovery

这是 VeilText 的独立 Python 恢复工具。

用途：即使原始 VeilText.exe、WPF 程序或原电脑已经丢失，只要仍然拥有：

- 完整的 `STX1:...` 密文
- 正确密码
- Python 环境

就可以恢复原文。

## 加密格式

本工具对应 VeilText STX1：

- AES-256-GCM
- PBKDF2-HMAC-SHA256
- 600,000 iterations
- Salt: 16 bytes
- Nonce: 12 bytes
- Authentication Tag: 16 bytes
- AAD: `STX1|AES-256-GCM|PBKDF2-SHA256|600000`

## 安装

建议 Python 3.10 或更高版本。

```powershell
python -m pip install -r requirements.txt
```

## 使用

```powershell
python veiltext_stx1_recovery.py
```

程序支持：

1. 直接粘贴完整 STX1 密文
2. 从 UTF-8 文本文件读取密文
3. 输入密码
4. 显示恢复后的明文
5. 可选择将明文保存为 UTF-8 文本文件

## 长期保存建议

建议把整个 ZIP 与重要密文分开备份到多个位置，例如：

- 本地电脑
- 外置硬盘 / U 盘
- 云盘

密码不要和密文放在同一个地方。

请长期保留：

- `veiltext_stx1_recovery.py`
- `requirements.txt`
- 本 README
- 一份已知明文对应的测试密文

这样未来即使 VeilText 主程序已经无法运行，也可以独立恢复 STX1 数据。

## 注意

- 忘记密码无法恢复。
- 密文被破坏或修改后，AES-GCM 验证会失败。
- Base64 只是编码，不是加密。
- 此工具不依赖 Windows DPAPI、TPM、当前 Windows 用户账户或原电脑。
