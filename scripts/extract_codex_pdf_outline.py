#!/usr/bin/env python3
"""Extract PDF outline for Codex book (optional enrichment)."""

import sys
from pathlib import Path

from pypdf import PdfReader

PDF = Path(r"c:\Users\54461\Desktop\Codex快速入门-PDF-yuancongde-批注.pdf")
OUT = Path(__file__).resolve().parents[1] / "docs" / "codex_pdf_outline.txt"


def main():
    r = PdfReader(str(PDF))
    lines = [f"pages: {len(r.pages)}", ""]

    if r.outline:
        def walk(items, depth=0):
            for it in items:
                if isinstance(it, list):
                    walk(it, depth + 1)
                else:
                    lines.append("  " * depth + str(it.title))

        walk(r.outline)
    else:
        lines.append("no PDF outline/bookmarks")
        # fallback: scan first lines of each page for chapter headings
        import re

        pat = re.compile(r"第\s*\d+\s*章|Chapter\s*\d+", re.I)
        for i, page in enumerate(r.pages[:50]):
            text = page.extract_text() or ""
            for line in text.splitlines():
                line = line.strip()
                if pat.search(line) and len(line) < 80:
                    lines.append(f"p{i+1}: {line}")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
