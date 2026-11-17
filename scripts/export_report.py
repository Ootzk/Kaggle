"""Export saved notebook outputs inside the Dev Container; never execute cells."""
import argparse
import hashlib
import json
from pathlib import Path
import re

import nbformat
from bs4 import BeautifulSoup
from nbconvert import HTMLExporter
from nbconvert.preprocessors import TagRemovePreprocessor
from plotly.offline import get_plotlyjs

from report_common import source_digest

ROOT = Path(__file__).resolve().parents[1]


def add_code_toggle(soup):
    style = soup.new_tag("style", id="report-code-toggle-style")
    style.string = """
        #report-controls {
            position: sticky;
            top: 8px;
            z-index: 1000;
            margin-bottom: 24px;
            padding: 10px 14px;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            background: var(--jp-layout-color0, white);
            font: 14px system-ui, sans-serif;
        }
        #report-controls label {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
        }
        .report-hide-code .jp-CodeCell .jp-InputArea,
        .report-hide-code .jp-CodeCell.jp-mod-noOutputs {
            display: none !important;
        }
        @media print {
            #report-controls { display: none; }
        }
    """
    soup.head.append(style)
    controls = soup.new_tag("div", id="report-controls")
    label = soup.new_tag("label", attrs={"for": "report-show-code"})
    checkbox = soup.new_tag(
        "input", id="report-show-code", attrs={"type": "checkbox", "checked": ""}
    )
    label.append(checkbox)
    label.append("Show code")
    controls.append(label)
    soup.body.insert(0, controls)
    script = soup.new_tag("script", id="report-code-toggle-script")
    script.string = """
        document.getElementById('report-show-code').addEventListener('change', (event) => {
            document.body.classList.toggle('report-hide-code', !event.target.checked);
            window.dispatchEvent(new Event('resize'));
        });
    """
    soup.body.append(script)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notebook", type=Path)
    args = parser.parse_args()
    path = args.notebook.resolve()
    relative = path.relative_to(ROOT / "competitions")
    if len(relative.parts) != 2 or path.suffix != ".ipynb":
        parser.error("Use competitions/<competition>/<notebook>.ipynb")
    notebook = nbformat.read(path, as_version=4)
    source_hash = source_digest(notebook)
    code = [c for c in notebook.cells if c.cell_type == "code" and c.source.strip()]
    if not code or any(c.execution_count is None for c in code):
        parser.error("Save an executed notebook before exporting; not all code cells have run.")
    if any(o.output_type == "error" for c in code for o in c.outputs):
        parser.error("Notebook contains execution errors.")
    # Replace notebook-specific RequireJS wrappers with the embedded Plotly runtime.
    for cell in code:
        for output in cell.outputs:
            data = output.get("data", {})
            if "text/html" not in data:
                continue
            html = data["text/html"]
            if "plotly.js v" in html:
                data["text/html"] = ""
                continue
            soup = BeautifulSoup(html, "html.parser")
            for script in soup.find_all("script"):
                value = script.string or ""
                if 'require(["plotly"], function(Plotly)' in value:
                    value = value.replace('require(["plotly"], function(Plotly)', '(function(Plotly)', 1)
                    value, count = re.subn(r"\}\);\s*$", "})(window.Plotly);", value)
                    if count != 1:
                        raise ValueError("Unrecognized Plotly notebook wrapper")
                    script.string = value
            data["text/html"] = str(soup)
    exporter = HTMLExporter(template_name="lab", embed_images=True)
    exporter.register_preprocessor(
        TagRemovePreprocessor(remove_input_tags={"hide_input"}), enabled=True
    )
    body, resources = exporter.from_notebook_node(notebook)
    if resources.get("outputs"):
        raise ValueError("Unexpected external export resources")
    soup = BeautifulSoup(body, "html.parser")
    for script in soup.find_all("script", src=True):
        # This report has no math or notebook widget outputs requiring these loaders.
        script.decompose()
    plotly_script = soup.new_tag("script")
    plotly_script.string = get_plotlyjs()
    soup.head.append(plotly_script)
    add_code_toggle(soup)
    body = "\n".join(line.rstrip() for line in str(soup).splitlines()) + "\n"
    if 'require(["plotly"]' in body:
        raise ValueError("Unconverted Plotly output")
    destination = ROOT / "reports" / relative.parent / (path.stem + ".html")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(body)
    manifest = {
        "notebook": path.relative_to(ROOT).as_posix(),
        "title": notebook.metadata.get("title", path.stem),
        "label": path.stem.replace("_", " ").title(),
        "source_sha256": source_hash,
        "html_sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
    }
    destination.with_suffix(".json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(destination.relative_to(ROOT))


if __name__ == "__main__":
    main()
