# VeilText STX1 Encryption + Recovery

这是 VeilText 的独立 Python 加密 / 恢复工具。

它既可以生成与 VeilText STX1 规范兼容的密文，也可以在原始 VeilText.exe、WPF 程序或原电脑已经丢失的情况下独立恢复原文。

只要仍然拥有：

- 完整的 `STX1:...` 密文
- 正确密码
- Python 环境

就可以恢复原文。

## 功能

程序支持：

1. 直接粘贴明文并生成 STX1 密文
2. 直接粘贴完整 STX1 密文并恢复明文
3. 加密 UTF-8 文本文件
4. 解密 / 恢复 STX1 文本文件
5. 将结果保存为 UTF-8 文本文件

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

## 安装

建议 Python 3.10 或更高版本。

```powershell
python -m pip install -r requirements.txt
```

## 使用

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

建议把整个项目 ZIP 与重要密文分开备份到多个位置，例如：

- 本地电脑
- 外置硬盘 / U 盘
- 云盘

密码不要和密文放在同一个地方。

请长期保留：

- `veiltext_stx1_recovery.py`
- `requirements.txt`
- `STX1-SPEC.md`
- 本 README
- 一份已知明文对应的测试密文

这样未来即使 VeilText 主程序已经无法运行，也可以使用 Python 独立加密和恢复 STX1 数据。

## 注意

- 忘记密码无法恢复。
- 密文被破坏或修改后，AES-GCM 验证会失败。
- 每次加密都会随机生成新的 Salt 和 Nonce，所以相同明文和相同密码多次加密得到不同密文，这是正常且必要的安全特性。
- Base64 只是编码，不是加密。
- 此工具不依赖 Windows DPAPI、TPM、当前 Windows 用户账户或原电脑。
