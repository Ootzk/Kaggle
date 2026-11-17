# HTML reports and GitHub Pages

## Layout

```text
competitions/
  digit-recognizer/
    experiment-cnn-baseline.ipynb
    data/                              # ignored local competition data
    output/                            # ignored generated files
reports/
  digit-recognizer/
    experiment-cnn-baseline.html          # tracked, includes local execution outputs
    experiment-cnn-baseline.json          # tracked source/report identity
```

HTML under `reports/` is tracked with Git LFS; the small JSON manifests remain regular Git files. The Dev Container installs checksum-verified Git LFS at the version declared in its Dockerfile and registers repository-local LFS filters and the pre-push hook on startup.

The notebook is the source of truth. Keep execution outputs in the working notebook; the container's Git filter strips committed notebooks. HTML preserves code, Markdown, tables, logs, and interactive Plotly figures.

## Export in the Dev Container

Save the executed notebook, then run from the repository root:

```bash
/usr/bin/python3 scripts/export_report.py competitions/digit-recognizer/experiment-cnn-baseline.ipynb
```

The command uses the Kaggle image's Python and existing packages. It does not run cells. It rejects unexecuted nonempty code cells and saved execution errors. It embeds images and the Plotly JavaScript runtime, replacing notebook-specific RequireJS wrappers so figures work in a standalone browser without a CDN. Chart hover and legends remain interactive.

Exported HTML includes a **Show code** checkbox at the top, enabled by default. Turn it off to hide code inputs and cells without outputs while preserving Markdown, tables, logs, and charts. It works offline and does not modify the notebook or rerun any code. The control itself is omitted when printing.

To hide an individual code cell's source in exported HTML while keeping its output, add `hide_input` to the cell's `metadata.tags`. The notebook retains its code and outputs; other code cells remain visible in HTML. For example, a model-summary cell can display only its generated table. This is an export setting, not a Git output-retention tag.

The adjacent JSON manifest records a digest of cell types, source, and the export-relevant `hide_input` tag, plus the HTML digest. It intentionally excludes outputs, execution counts, and transient notebook metadata. Untagged notebooks retain their existing digests. This lets a Pages build validate a report against the stripped notebook committed to Git. Hashes detect edits after export; they do not prove that saved outputs were produced by the current code. Rerun computational changes before exporting. Markdown-only and `hide_input` tag edits can be exported without retraining.

## Preview and verify

```bash
/usr/bin/python3 scripts/build_pages.py --output tmp/pages-preview
/usr/bin/python3 -m http.server 8000 --directory tmp/pages-preview
```

After a clone or when a report appears as a short LFS pointer, run `git lfs pull`. Use a fresh/empty output directory. Open the forwarded server in a browser. Check the index link, all plots, legend toggles, training logs, metrics, and error-gallery captions. Reports are standalone HTML; no external images or script downloads are needed. Review code and output for credentials and any information unsuitable for publication.

## Stage and commit

```bash
git add competitions/digit-recognizer/experiment-cnn-baseline.ipynb reports/digit-recognizer/
git show :competitions/digit-recognizer/experiment-cnn-baseline.ipynb
git diff --cached --check
```

Verify each indexed code cell has empty `outputs` and a null `execution_count`. Keep `.env`, CSV data, model artifacts, and temporary previews ignored. Commit source and matching report/manifest together, then push from the Dev Container.

## Deployment

The Pages workflow is `.github/workflows/pages.yml`. Only pushes to `main` that touch reports, notebook sources, report build scripts, attributes, or the workflow trigger automatic deployment. Manual dispatch is also supported, but a job condition permits it only for `refs/heads/main`. The `github-pages` environment independently permits deployments from `main` only. Work on feature branches is published after it is merged into `main`; a feature-branch push or pull request does not deploy. Documentation-only changes do not automatically deploy.

GitHub Pages must use **GitHub Actions** as its publishing source. The `github-pages` environment must permit the deployment branch. The workflow:

1. Downloads actual HTML with LFS-aware checkout (`lfs: true`) and an explicit `git lfs pull`.
2. Checks source/report digests with standard-library Python, rejects unresolved LFS pointers, then copies only `reports/<competition>/*.html` and generates an index with relative links. It never trains or exports notebooks.
3. Uploads that directory as the Pages artifact and deploys it with `pages: write` and `id-token: write` permissions.

Only report HTML and the index are published; source files, JSON manifests, data directories, and credentials are excluded from the site artifact.

Public URLs:

- [Report index](https://ootzk.github.io/Kaggle/)
- [Digit Recognizer — Baseline](https://ootzk.github.io/Kaggle/digit-recognizer/experiment-cnn-baseline.html)

Git preserves older HTML versions; the site shows the latest successful deployment.

## Verification status

The initial Pages publication and the subsequent LFS-backed deployment passed. Both public URLs returned HTTP 200, and the report matched the committed HTML byte-for-byte. Browser checks passed for all eight Plotly charts, grouped digit legend toggles, and ten error-gallery captions, with no external resource requests or JavaScript errors. Fresh-clone LFS retrieval and notebook Git output-preservation checks also passed.

The initial publication used the setup branch before the policy was restricted. Future deployments require `main`; changing that policy does not replace the previously published site until a new deployment succeeds. Local evidence and screenshots remain untracked under `.git/kaggle-devcontainer/`.

## Git LFS report storage

```bash
git lfs version
git lfs pull
git lfs ls-files
git lfs fsck
```

Stage an updated report with normal `git add`; LFS stores the HTML separately and commits a small pointer. The pre-push hook uploads its LFS object. Working files and the Pages artifact contain the full HTML. The Pages workflow hydrates LFS before assembling its artifact; it does not ask the branch-based Pages publisher to serve LFS pointers.

This conversion does not rewrite history. HTML in older commits remains an ordinary Git blob; only this and later report revisions use LFS. Rebuild the Dev Container to adopt its declared Git LFS installation when recreating the environment.

## Competition index

The index groups reports by their `reports/<competition-slug>/` directory. Each competition appears once, with its image and title beside links such as Baseline and EDA. Additional exported reports appear under the same competition automatically; empty or invented report links are not shown.

Optional `competitions/<competition-slug>/competition.json` supplies `title`, `url`, and `thumbnail_url`. Use public HTTPS links. Without this metadata, the first report title and the competition slug provide defaults. Missing or failed images show a text fallback.

KaggleHub currently handles input resources, not competition thumbnail discovery. Digit Recognizer uses the public representative image advertised by its official competition page's `og:image` metadata. The index references that Kaggle-hosted image; it is not an input dataset download, and no Kaggle authentication is needed in Pages builds. Images are not available offline unless already cached; individual exported reports remain standalone. Keep all notebook input downloads in KaggleHub.

Updating `competition.json` on `main` triggers the Pages workflow. Metadata-only index changes do not require notebook execution or HTML re-export.
