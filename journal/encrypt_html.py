from __future__ import annotations

import getpass
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from veiltext_stx1_recovery import encrypt_veiltext


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: encrypt_html.py <input.html> <output.stx1>", file=sys.stderr)
        return 2

    input_path = Path(sys.argv[1]).resolve()
    output_path = Path(sys.argv[2]).resolve()

    html_text = input_path.read_text(encoding="utf-8")
    if not html_text:
        raise ValueError("HTML file is empty.")

    password = getpass.getpass("Diary password: ")
    confirm = getpass.getpass("Confirm password: ")

    if not password:
        raise ValueError("Password must not be empty.")
    if password != confirm:
        raise ValueError("Passwords do not match.")

    ciphertext = encrypt_veiltext(html_text, password)
    output_path.write_text(ciphertext, encoding="utf-8")

    print(f"[OK] Encrypted: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
