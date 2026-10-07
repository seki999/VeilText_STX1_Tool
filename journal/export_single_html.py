from __future__ import annotations

import base64
import html
import mimetypes
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

import markdown

IMG_RE = re.compile(
    r'(<img\b[^>]*?\bsrc\s*=\s*)(["\'])(.*?)(\2)',
    flags=re.IGNORECASE | re.DOTALL,
)


def local_image_to_data_uri(src: str, base_dir: Path) -> str:
    stripped = src.strip()
    if stripped.startswith(("data:", "http://", "https://")):
        return src

    parsed = urlparse(stripped)
    if parsed.scheme and parsed.scheme.lower() != "file":
        return src

    if parsed.scheme.lower() == "file":
        raw_path = unquote(parsed.path)
        if re.match(r"^/[A-Za-z]:/", raw_path):
            raw_path = raw_path[1:]
        image_path = Path(raw_path)
    else:
        image_path = Path(unquote(parsed.path))
        if not image_path.is_absolute():
            image_path = (base_dir / image_path).resolve()

    if not image_path.exists() or not image_path.is_file():
        print(f"[WARN] Image not found, left unchanged: {src}", file=sys.stderr)
        return src

    mime, _ = mimetypes.guess_type(image_path.name)
    mime = mime or "application/octet-stream"
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def embed_images(rendered_html: str, base_dir: Path) -> str:
    def repl(match: re.Match[str]) -> str:
        prefix, quote, src, _ = match.groups()
        embedded = local_image_to_data_uri(html.unescape(src), base_dir)
        return f"{prefix}{quote}{embedded}{quote}"

    return IMG_RE.sub(repl, rendered_html)


def build_document(title: str, body: str) -> str:
    safe_title = html.escape(title)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{safe_title}</title>
<style>
:root {{
  color-scheme: light dark;
  --bg: #fbfbfa;
  --fg: #222;
  --border: #d8d8d8;
  --code: #f1f1f1;
  --quote: #f6f6f6;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --bg: #1e1e1e;
    --fg: #dddddd;
    --border: #444;
    --code: #2a2a2a;
    --quote: #262626;
  }}
}}
html {{ background: var(--bg); }}
body {{
  margin: 0 auto;
  max-width: 920px;
  padding: 42px 28px 80px;
  background: var(--bg);
  color: var(--fg);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Yu Gothic UI",
               "Meiryo", "Noto Sans CJK JP", Arial, sans-serif;
  font-size: 18px;
  line-height: 1.8;
}}
h1, h2, h3 {{ line-height: 1.35; margin-top: 1.5em; }}
p {{ margin: 0.9em 0; }}
img {{
  display: block;
  max-width: 100%;
  height: auto;
  margin: 1.4em auto;
  border-radius: 8px;
}}
blockquote {{
  margin: 1em 0;
  padding: .6em 1em;
  border-left: 4px solid var(--border);
  background: var(--quote);
}}
pre, code {{
  font-family: Consolas, "Cascadia Code", monospace;
  background: var(--code);
}}
code {{ padding: .12em .35em; border-radius: 4px; }}
pre {{ padding: 1em; overflow-x: auto; border-radius: 8px; }}
pre code {{ padding: 0; }}
table {{ border-collapse: collapse; width: 100%; margin: 1.3em 0; }}
th, td {{ border: 1px solid var(--border); padding: .5em .7em; text-align: left; }}
hr {{ border: 0; border-top: 1px solid var(--border); margin: 2em 0; }}
a {{ overflow-wrap: anywhere; }}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: export_single_html.py <file.md>", file=sys.stderr)
        return 2

    md_path = Path(sys.argv[1]).resolve()
    if md_path.suffix.lower() not in {".md", ".markdown"}:
        print(f"Not a Markdown file: {md_path}", file=sys.stderr)
        return 2
    if not md_path.exists():
        print(f"File does not exist: {md_path}", file=sys.stderr)
        return 2

    source = md_path.read_text(encoding="utf-8")
    body = markdown.markdown(
        source,
        extensions=["extra", "fenced_code", "tables", "sane_lists"],
        output_format="html5",
    )
    body = embed_images(body, md_path.parent)

    title = md_path.stem
    match = re.search(r"<h1[^>]*>(.*?)</h1>", body, flags=re.IGNORECASE | re.DOTALL)
    if match:
        title = re.sub(r"<[^>]+>", "", html.unescape(match.group(1))).strip() or title

    output = md_path.with_name(md_path.stem + ".single.html")
    output.write_text(build_document(title, body), encoding="utf-8")
    print(f"[OK] Exported: {output}")
    print(f"[OK] Size: {output.stat().st_size:,} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
