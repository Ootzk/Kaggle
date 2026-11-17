"""Validate tracked report/source pairs and copy only reports to a new Pages directory."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import shutil
from urllib.parse import quote, urlparse

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
        if report.read_bytes().startswith(b"version https://git-lfs.github.com/spec/v1"):
            raise ValueError(f"Report is an LFS pointer; run git lfs pull: {report}")
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
    groups = {}
    for relative, manifest in entries:
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / "reports" / relative, target)
        groups.setdefault(relative.parent.name, []).append((relative, manifest))

    cards = []
    for slug, reports in groups.items():
        metadata_path = ROOT / "competitions" / slug / "competition.json"
        metadata = json.loads(metadata_path.read_text()) if metadata_path.exists() else {}
        title = metadata.get("title", reports[0][1]["title"])
        url = metadata.get("url", f"https://www.kaggle.com/competitions/{quote(slug)}")
        thumbnail = metadata.get("thumbnail_url", "")
        for value in (url, thumbnail):
            if value and (urlparse(value).scheme != "https" or not urlparse(value).netloc):
                raise ValueError(f"Competition links must use HTTPS: {slug}")
        title_text = html.escape(title)
        initials = html.escape("".join(word[0] for word in title.split()[:2]).upper())
        image = (
            f'<img src="{html.escape(thumbnail, quote=True)}" alt="{title_text} competition image" '
            'loading="lazy" referrerpolicy="no-referrer" onerror="this.remove()">'
            if thumbnail else ""
        )
        links = "".join(
            f'<li><a href="{quote(relative.as_posix())}">{html.escape(manifest["label"])}</a></li>'
            for relative, manifest in reports
        )
        cards.append(
            '<article class="competition">'
            f'<div class="thumbnail"><span aria-hidden="true">{initials}</span>{image}</div>'
            f'<div><h2><a href="{html.escape(url, quote=True)}">{title_text}</a></h2>'
            f'<ul class="reports">{links}</ul></div></article>'
        )
    (output / "index.html").write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Kaggle reports</title><style>'
        'body{font:17px/1.6 system-ui,sans-serif;max-width:880px;margin:64px auto;padding:0 24px;color:#17212b;background:#fafbfd}'
        'h1{font-size:32px;letter-spacing:-.03em;margin-bottom:4px}'
        '.intro{color:#586574;margin:0 0 36px}a{color:#075cbd;text-underline-offset:3px}'
        '.competition{display:grid;grid-template-columns:144px 1fr;gap:24px;padding:28px 0;border-top:1px solid #dce3eb;align-items:start}'
        '.thumbnail{position:relative;aspect-ratio:2/1;background:#e6edf5;border-radius:8px;overflow:hidden;display:grid;place-items:center;color:#576b80;font-weight:600}'
        '.thumbnail img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}'
        'h2{font-size:21px;line-height:1.3;margin:0 0 10px}h2 a{color:inherit;text-decoration:none}h2 a:hover{text-decoration:underline}'
        '.reports{margin:0;padding-left:22px}.reports li{padding:3px 0}'
        '@media(max-width:520px){body{margin:32px auto;padding:0 18px}.competition{grid-template-columns:96px 1fr;gap:16px}h2{font-size:19px}}'
        '</style></head><body><main><h1>Kaggle reports</h1>'
        '<p class="intro">Competition notebooks, experiments, and execution results.</p>'
        + ''.join(cards) + '</main></body></html>'
    )
    print(f"Prepared {len(entries)} report(s) in {output}")


if __name__ == "__main__":
    main()
