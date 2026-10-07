from __future__ import annotations

import getpass
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from veiltext_stx1_recovery import decrypt_veiltext


def main() -> int:
    if len(sys.argv) not in (2, 3):
        print("Usage: decrypt_html.py <input.stx1> [output.html]", file=sys.stderr)
        return 2

    input_path = Path(sys.argv[1]).resolve()
    output_path = (
        Path(sys.argv[2]).resolve()
        if len(sys.argv) == 3
        else input_path.with_suffix(".recovered.html")
    )

    encrypted_text = input_path.read_text(encoding="utf-8")
    password = getpass.getpass("Diary password: ")
    html_text = decrypt_veiltext(encrypted_text, password)
    output_path.write_text(html_text, encoding="utf-8")

    print(f"[OK] Recovered HTML: {output_path}")

    if os.name == "nt":
        os.startfile(output_path)  # type: ignore[attr-defined]

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
