# HTML reports and GitHub Pages

## Layout

```text
competitions/
  digit-recognizer/
    baseline.ipynb
    data/                  # ignored local competition data
    output/                # ignored generated files
reports/
  digit-recognizer/
    baseline.html          # tracked, includes local execution outputs
    baseline.json          # tracked source/report identity
```

The notebook is the source of truth. Keep execution outputs in the working notebook; the container's Git filter strips committed notebooks. HTML preserves code, Markdown, tables, logs, and interactive Plotly figures.

## Export in the Dev Container

Save the executed notebook, then run from the repository root:

```bash
/usr/bin/python3 scripts/export_report.py competitions/digit-recognizer/baseline.ipynb
```

The command uses the Kaggle image's Python and existing packages. It does not run cells. It rejects unexecuted nonempty code cells and saved execution errors. It embeds images and the Plotly JavaScript runtime, replacing notebook-specific RequireJS wrappers so figures work in a standalone browser without a CDN. Chart hover and legends remain interactive.

The adjacent JSON manifest records a digest of cell types and source, plus the HTML digest. It intentionally excludes outputs, execution counts, and transient notebook metadata. This lets a Pages build validate a report against the stripped notebook committed to Git. Hashes detect edits after export; they do not prove that saved outputs were produced by the current code. Rerun computational changes before exporting. Markdown-only edits can be exported without retraining.

## Preview and verify

```bash
/usr/bin/python3 scripts/build_pages.py --output tmp/pages-preview
/usr/bin/python3 -m http.server 8000 --directory tmp/pages-preview
```

Use a fresh/empty output directory. Open the forwarded server in a browser. Check the index link, all plots, legend toggles, training logs, metrics, and error-gallery captions. Reports are standalone HTML; no external images or script downloads are needed. Review code and output for credentials and any information unsuitable for publication.

## Stage and commit

```bash
git add competitions/digit-recognizer/baseline.ipynb reports/digit-recognizer/
git show :competitions/digit-recognizer/baseline.ipynb
git diff --cached --check
```

Verify each indexed code cell has empty `outputs` and a null `execution_count`. Keep `.env`, CSV data, model artifacts, and temporary previews ignored. Commit source and matching report/manifest together, then push from the Dev Container.

## Deployment

The Pages workflow is `.github/workflows/pages.yml`. It currently accepts pushes to `setup/dev-container-workflow` and `main`, plus manual dispatch. The setup branch supports the initial deployment; once work is merged, remove that branch from the trigger and publish from `main` only. Do not use both branches for independent report releases.

GitHub Pages must use **GitHub Actions** as its publishing source. The `github-pages` environment must permit the deployment branch. The workflow:

1. Checks source/report digests with standard-library Python. It never trains or exports notebooks.
2. Copies only `reports/<competition>/*.html` and generates an index with relative links.
3. Uploads that directory as the Pages artifact and deploys it with `pages: write` and `id-token: write` permissions.

Only report HTML and the index are published; source files, JSON manifests, data directories, and credentials are excluded from the site artifact.

Public URLs:

- [Report index](https://ootzk.github.io/Kaggle/)
- [Digit Recognizer — Baseline](https://ootzk.github.io/Kaggle/digit-recognizer/baseline.html)

Git preserves older HTML versions; the site shows the latest successful deployment.

## Verified deployment

The initial deployment from commit `95ad742` completed successfully in [GitHub Actions](https://github.com/Ootzk/Kaggle/actions/runs/44075475308). Both public URLs returned HTTP 200, and the served report matched the committed HTML byte-for-byte. Browser verification passed for all eight Plotly charts, grouped digit legend toggles, and the ten error-gallery captions, with no external resource requests or JavaScript errors. Local diagnostics and screenshots remain untracked under `.git/kaggle-devcontainer/`.

The moved competition directory passed notebook Git staging/output-preservation and diff/merge verification. Local CSVs and outputs remain ignored and preserved under `competitions/digit-recognizer/`.
