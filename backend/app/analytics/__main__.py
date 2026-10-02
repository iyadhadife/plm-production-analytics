"""Offline generation of every analysis: `python -m app.analytics [output_dir]`."""

import sys
from pathlib import Path

from app.analytics import ANALYSES, render_analysis

out = Path(sys.argv[1] if len(sys.argv) > 1 else "analyses_html")
out.mkdir(parents=True, exist_ok=True)
for name in ANALYSES:
    (out / f"{name}.html").write_text(render_analysis(name), encoding="utf-8")
    print("OK", name)
