# STX1 Format Specification

Prefix:

```text
STX1:
```

Payload:

```text
Base64(UTF-8 JSON)
```

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

```text
UTF-8, without Unicode normalization.
```

Key derivation:

```text
PBKDF2-HMAC-SHA256
Iterations: 600000
Output length: 32 bytes
```

Encryption:

```text
AES-256-GCM
```

AAD:

```text
STX1|AES-256-GCM|PBKDF2-SHA256|600000
```

Encryption procedure:

1. Generate a cryptographically random 16-byte Salt.
2. Generate a cryptographically random 12-byte Nonce.
3. Derive a 32-byte key from the UTF-8 password using PBKDF2-HMAC-SHA256 with 600000 iterations.
4. Encode plaintext as UTF-8.
5. Encrypt with AES-256-GCM using the fixed AAD above.
6. Split the AES-GCM output into:
   - Ciphertext
   - final 16 bytes as authentication Tag
7. Base64-encode Salt, Nonce, Ciphertext and Tag.
8. Serialize the required JSON fields as UTF-8 JSON.
9. Base64-encode the JSON bytes.
10. Prefix the result with `STX1:`.

Python AESGCM API expects ciphertext and authentication tag concatenated as:

```text
ciphertext || tag
```

Compatibility rule:

STX1 v1 parameters and field meanings are fixed. Future cryptographic changes should use a new version identifier rather than silently changing STX1.
