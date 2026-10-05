import base64
import json
import sys
import getpass
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


ITERATIONS = 600_000
AAD = b"STX1|AES-256-GCM|PBKDF2-SHA256|600000"


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive the AES-256 key exactly as VeilText STX1 does."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    return kdf.derive(password.encode("utf-8"))


def decrypt_veiltext(encrypted_text: str, password: str) -> str:
    encrypted_text = encrypted_text.strip()

    if not encrypted_text.startswith("STX1:"):
        raise ValueError("Not a valid STX1 VeilText ciphertext.")

    encoded_payload = encrypted_text[5:]
    json_bytes = base64.b64decode(encoded_payload, validate=True)
    payload = json.loads(json_bytes.decode("utf-8"))

    if payload.get("Version") != 1:
        raise ValueError("Unsupported STX version.")
    if payload.get("Algorithm") != "AES-256-GCM":
        raise ValueError("Unsupported encryption algorithm.")
    if payload.get("Kdf") != "PBKDF2-SHA256":
        raise ValueError("Unsupported KDF.")
    if payload.get("Iterations") != ITERATIONS:
        raise ValueError("Unsupported PBKDF2 iteration count.")

    salt = base64.b64decode(payload["Salt"], validate=True)
    nonce = base64.b64decode(payload["Nonce"], validate=True)
    ciphertext = base64.b64decode(payload["Ciphertext"], validate=True)
    tag = base64.b64decode(payload["Tag"], validate=True)

    if len(salt) != 16:
        raise ValueError("Invalid salt length.")
    if len(nonce) != 12:
        raise ValueError("Invalid nonce length.")
    if len(tag) != 16:
        raise ValueError("Invalid authentication tag length.")
    if len(ciphertext) == 0:
        raise ValueError("Invalid ciphertext length.")

    key = derive_key(password, salt)
    aesgcm = AESGCM(key)

    try:
        plaintext_bytes = aesgcm.decrypt(
            nonce,
            ciphertext + tag,
            AAD
        )
    except Exception as exc:
        raise ValueError(
            "Decryption failed. Password may be incorrect "
            "or ciphertext may be damaged."
        ) from exc

    return plaintext_bytes.decode("utf-8")


def decrypt_file(input_path: str, output_path: str, password: str) -> None:
    encrypted_text = Path(input_path).read_text(encoding="utf-8")
    plaintext = decrypt_veiltext(encrypted_text, password)
    Path(output_path).write_text(plaintext, encoding="utf-8")


def interactive_mode() -> None:
    print("VeilText STX1 Recovery Tool")
    print("---------------------------")
    print("1. Paste ciphertext")
    print("2. Read ciphertext from file")
    print()

    choice = input("Choose 1 or 2 [1]: ").strip() or "1"
    password = getpass.getpass("Password: ")

    try:
        if choice == "2":
            input_path = input("Encrypted text file path: ").strip().strip('"')
            encrypted_text = Path(input_path).read_text(encoding="utf-8")
        else:
            print()
            print("Paste the complete STX1 ciphertext, then press Enter:")
            encrypted_text = input().strip()

        plaintext = decrypt_veiltext(encrypted_text, password)

        print()
        print("===== Decrypted text =====")
        print(plaintext)
        print("==========================")
        print()

        save = input("Save plaintext to a UTF-8 text file? [y/N]: ").strip().lower()
        if save == "y":
            output_path = input("Output file path [recovered.txt]: ").strip().strip('"') or "recovered.txt"
            Path(output_path).write_text(plaintext, encoding="utf-8")
            print(f"Saved to: {output_path}")

    except Exception as e:
        print()
        print("ERROR:", e)
        sys.exit(1)


if __name__ == "__main__":
    interactive_mode()
