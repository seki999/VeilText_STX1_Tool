# STX1 Format Specification

Prefix:

STX1:

Payload:

Base64(UTF-8 JSON)

Required JSON fields:

- Version = 1
- Algorithm = AES-256-GCM
- Kdf = PBKDF2-SHA256
- Iterations = 600000
- Salt = Base64(16 bytes)
- Nonce = Base64(12 bytes)
- Ciphertext = Base64(cipher bytes)
- Tag = Base64(16 bytes)

Password encoding:

UTF-8, without Unicode normalization.

Key derivation:

PBKDF2-HMAC-SHA256
Iterations: 600000
Output length: 32 bytes

Encryption:

AES-256-GCM

AAD:

ASCII:
STX1|AES-256-GCM|PBKDF2-SHA256|600000

Python AESGCM API expects ciphertext and authentication tag concatenated as:

ciphertext || tag
