import base64
import getpass
import json
import os
import sys
from pathlib import Path

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


ITERATIONS = 600_000
AAD = b"STX1|AES-256-GCM|PBKDF2-SHA256|600000"
SALT_LENGTH = 16
NONCE_LENGTH = 12
TAG_LENGTH = 16


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive the AES-256 key exactly as VeilText STX1 does."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    return kdf.derive(password.encode("utf-8"))


def encrypt_veiltext(plaintext: str, password: str) -> str:
    """Encrypt UTF-8 text into a VeilText STX1 ciphertext."""
    if plaintext == "":
        raise ValueError("Plaintext must not be empty.")
    if password == "":
        raise ValueError("Password must not be empty.")

    salt = os.urandom(SALT_LENGTH)
    nonce = os.urandom(NONCE_LENGTH)
    key = derive_key(password, salt)

    encrypted = AESGCM(key).encrypt(
        nonce,
        plaintext.encode("utf-8"),
        AAD,
    )
    ciphertext = encrypted[:-TAG_LENGTH]
    tag = encrypted[-TAG_LENGTH:]

    payload = {
        "Version": 1,
        "Algorithm": "AES-256-GCM",
        "Kdf": "PBKDF2-SHA256",
        "Iterations": ITERATIONS,
        "Salt": base64.b64encode(salt).decode("ascii"),
        "Nonce": base64.b64encode(nonce).decode("ascii"),
        "Ciphertext": base64.b64encode(ciphertext).decode("ascii"),
        "Tag": base64.b64encode(tag).decode("ascii"),
    }

    json_bytes = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return "STX1:" + base64.b64encode(json_bytes).decode("ascii")


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

    if len(salt) != SALT_LENGTH:
        raise ValueError("Invalid salt length.")
    if len(nonce) != NONCE_LENGTH:
        raise ValueError("Invalid nonce length.")
    if len(tag) != TAG_LENGTH:
        raise ValueError("Invalid authentication tag length.")
    if len(ciphertext) == 0:
        raise ValueError("Invalid ciphertext length.")

    key = derive_key(password, salt)
    aesgcm = AESGCM(key)

    try:
        plaintext_bytes = aesgcm.decrypt(
            nonce,
            ciphertext + tag,
            AAD,
        )
    except Exception as exc:
        raise ValueError(
            "Decryption failed. Password may be incorrect "
            "or ciphertext may be damaged."
        ) from exc

    return plaintext_bytes.decode("utf-8")


def encrypt_file(input_path: str, output_path: str, password: str) -> None:
    plaintext = Path(input_path).read_text(encoding="utf-8")
    encrypted_text = encrypt_veiltext(plaintext, password)
    Path(output_path).write_text(encrypted_text, encoding="utf-8")


def decrypt_file(input_path: str, output_path: str, password: str) -> None:
    encrypted_text = Path(input_path).read_text(encoding="utf-8")
    plaintext = decrypt_veiltext(encrypted_text, password)
    Path(output_path).write_text(plaintext, encoding="utf-8")


def prompt_new_password() -> str:
    password = getpass.getpass("Password: ")
    confirmation = getpass.getpass("Confirm password: ")

    if password != confirmation:
        raise ValueError("Passwords do not match.")
    if password == "":
        raise ValueError("Password must not be empty.")

    return password


def read_multiline_plaintext() -> str:
    print()
    print("Paste plaintext below.")
    print("Enter a line containing only ::END:: when finished:")
    lines = []

    while True:
        line = input()
        if line == "::END::":
            break
        lines.append(line)

    return "\n".join(lines)


def encrypt_text_interactive() -> None:
    plaintext = read_multiline_plaintext()
    password = prompt_new_password()
    encrypted_text = encrypt_veiltext(plaintext, password)

    print()
    print("===== STX1 ciphertext =====")
    print(encrypted_text)
    print("===========================")
    print()

    save = input("Save ciphertext to a UTF-8 text file? [y/N]: ").strip().lower()
    if save == "y":
        output_path = (
            input("Output file path [encrypted_stx1.txt]: ").strip().strip('"')
            or "encrypted_stx1.txt"
        )
        Path(output_path).write_text(encrypted_text, encoding="utf-8")
        print(f"Saved to: {output_path}")


def decrypt_text_interactive() -> None:
    print()
    print("Paste the complete STX1 ciphertext, then press Enter:")
    encrypted_text = input().strip()
    password = getpass.getpass("Password: ")
    plaintext = decrypt_veiltext(encrypted_text, password)

    print()
    print("===== Decrypted text =====")
    print(plaintext)
    print("==========================")
    print()

    save = input("Save plaintext to a UTF-8 text file? [y/N]: ").strip().lower()
    if save == "y":
        output_path = (
            input("Output file path [recovered.txt]: ").strip().strip('"')
            or "recovered.txt"
        )
        Path(output_path).write_text(plaintext, encoding="utf-8")
        print(f"Saved to: {output_path}")


def encrypt_file_interactive() -> None:
    input_path = input("Plaintext UTF-8 file path: ").strip().strip('"')
    output_path = (
        input("Output file path [encrypted_stx1.txt]: ").strip().strip('"')
        or "encrypted_stx1.txt"
    )
    password = prompt_new_password()
    encrypt_file(input_path, output_path, password)
    print(f"Encrypted file saved to: {output_path}")


def decrypt_file_interactive() -> None:
    input_path = input("Encrypted STX1 text file path: ").strip().strip('"')
    output_path = (
        input("Output file path [recovered.txt]: ").strip().strip('"')
        or "recovered.txt"
    )
    password = getpass.getpass("Password: ")
    decrypt_file(input_path, output_path, password)
    print(f"Recovered plaintext saved to: {output_path}")


def interactive_mode() -> None:
    print("VeilText STX1 Encryption + Recovery Tool")
    print("----------------------------------------")
    print("1. Encrypt pasted text")
    print("2. Decrypt / recover pasted STX1 ciphertext")
    print("3. Encrypt UTF-8 text file")
    print("4. Decrypt / recover STX1 text file")
    print("5. Exit")
    print()

    choice = input("Choose 1-5 [2]: ").strip() or "2"

    try:
        if choice == "1":
            encrypt_text_interactive()
        elif choice == "2":
            decrypt_text_interactive()
        elif choice == "3":
            encrypt_file_interactive()
        elif choice == "4":
            decrypt_file_interactive()
        elif choice == "5":
            return
        else:
            raise ValueError("Invalid choice. Please select 1, 2, 3, 4, or 5.")
    except Exception as exc:
        print()
        print("ERROR:", exc)
        sys.exit(1)


if __name__ == "__main__":
    interactive_mode()
