"""Validate tracked report/source pairs and copy only reports to a new Pages directory."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import shutil
from urllib.parse import quote

from report_common import source_digest

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "tmp" / "pages")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        parser.error("Output directory must be empty; use a new directory.")
    reports = sorted((ROOT / "reports").glob("*/*.html"))
    if not reports:
        parser.error("No reports found")
    entries = []
    for report in reports:
        relative = report.relative_to(ROOT / "reports")
        if report.is_symlink() or report.parent.is_symlink():
            raise ValueError("Report symlinks are not allowed")
        manifest = json.loads(report.with_suffix(".json").read_text())
        expected = f"competitions/{relative.parent}/{report.stem}.ipynb"
        if manifest["notebook"] != expected:
            raise ValueError(f"Invalid source path: {report}")
        notebook = json.loads((ROOT / expected).read_text())
        if source_digest(notebook) != manifest["source_sha256"]:
            raise ValueError(f"Notebook changed; re-export {expected}")
        if hashlib.sha256(report.read_bytes()).hexdigest() != manifest["html_sha256"]:
            raise ValueError(f"Report changed; re-export {expected}")
        entries.append((relative, manifest))
    output.mkdir(parents=True, exist_ok=True)
    cards = []
    for relative, manifest in entries:
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / "reports" / relative, target)
        cards.append(
            f'<li><a href="{quote(relative.as_posix())}">'
            f'{html.escape(manifest["title"])} — {html.escape(manifest["label"])}</a></li>'
        )
    (output / "index.html").write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Kaggle reports</title><style>'
        'body{font:18px/1.6 system-ui,sans-serif;max-width:880px;margin:64px auto;padding:0 24px;color:#17212b}'
        'a{color:#075cbd}li{margin:20px 0}</style></head><body>'
        '<h1>Kaggle reports</h1><p>Executed notebooks with code, interactive charts, and validation results.</p>'
        '<ul>' + ''.join(cards) + '</ul></body></html>'
    )
    print(f"Prepared {len(entries)} report(s) in {output}")


if __name__ == "__main__":
    main()
