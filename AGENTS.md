# Project Guidelines

This repository tracks Kaggle notebook source and HTML execution reports. Development uses VS Code Dev Containers on Ubuntu with an NVIDIA GPU. Local and remote Kaggle execution are verified independently.

## Repository structure

- Store notebook source in `competitions/<competition-slug>/`. Use the slug from the Kaggle competition URL.
- Follow `docs/notebook-naming.md`: `eda.ipynb`, `experiment-<model>-<variant>.ipynb`, `submission-<model>.ipynb`, and `report.ipynb`. Use lowercase kebab-case and singular `experiment`.
- Store report HTML and its JSON manifest in `reports/<competition-slug>/`, with the exact notebook stem. Store per-notebook Kaggle settings as `<notebook-stem>.kaggle.json`; copy to `kernel-metadata.json` only in the upload package. Keep existing Kaggle notebook IDs stable when renaming local files.
- Keep competition data and generated files in ignored competition-local directories such as `data/` and `output/`. Repository-wide temporary files belong in ignored `tmp/`.
- Optional `competitions/<slug>/competition.json` supplies the Pages index title, public competition URL, and thumbnail URL; reports are grouped under each competition.
- Keep shared operating instructions in `docs/`; keep machine diagnostics under untracked `.git/kaggle-devcontainer/`.

## Kaggle GPU base and management layer

- Use official `gcr.io/kaggle-gpu-images/python:latest` as the Dev Container base. Follow `latest` deliberately; do not pin its version or digest.
- Add a thin management layer in `.devcontainer/Dockerfile`: a non-root workspace user and explicitly versioned Git tools. Do not install or upgrade the base scientific packages.
- Keep notebook execution and HTML export on `/usr/bin/python3`, using packages supplied by the Kaggle image.
- Install `nbstripout`, `nbdime`, and their startup compatibility dependency `wrapt` in the isolated `/opt/kaggle-git-tools` environment. Keep it out of the notebook interpreter's import path.
- Install the checksum-verified Git LFS binary at its explicit Dockerfile version under `/opt/kaggle-git-tools/bin`, exposed as `/usr/local/bin/git-lfs`.
- Define the VS Code container configuration in `.devcontainer/`, mount the repository at `/workspaces/Kaggle`, and enable Python and Jupyter extensions.
- Match the development user's UID/GID to the Ubuntu workspace owner with `USER_UID`/`USER_GID` build arguments. The helper supplies `KAGGLE_HOST_UID`/`KAGGLE_HOST_GID`; automatic UID rewriting is disabled.
- The Ubuntu host supplies Docker Engine from its official Ubuntu repository, the NVIDIA driver and Container Toolkit, VS Code, and forwarded Git authentication. Verify the NVIDIA runtime before relying on `--gpus all`.
- Pull before rebuilding and validate each updated base image. Record its resolved digest and package versions in local diagnostics.
- Keep shared documentation at the Ubuntu + NVIDIA GPU level. Do not add workstation-specific GPU models, allocations, OS builds, host-tool versions, or local troubleshooting history.

## Data access

- Use **KaggleHub for every input competition/dataset download**. Use `competition_download` for competition inputs and `dataset_download` for datasets. Reuse files already available locally.
- Always use the directory returned by KaggleHub when resolving/downloading resources. Remote Kaggle execution may ignore `output_dir`; do not construct a fixed input mount path.
- Store local downloads under `competitions/<competition-slug>/data/` or another ignored data directory.
- Load the root `.env` with `load_dotenv(..., override=False)` for local `KAGGLE_API_TOKEN` authentication. KaggleHub reads the environment. Never print credentials.
- Remote kernels read the Kaggle server filesystem and use their own session authentication; they cannot access the local repository mount or `.env`.
- Kaggle API/CLI notebook push/status/output retrieval and prediction submission are permitted separately. Do not use them to replace KaggleHub input downloads.
- Record dataset handles, required versions, competition access requirements, and accelerator settings in notebook code or Markdown. See `docs/data-access.md`.

## Notebook development and Git

- Treat local notebooks as the source of truth. Apply improvements discovered during remote execution to local source.
- Keep each experiment notebook focused on its own method and results. Consolidate comparisons between experiments in the competition's `report.ipynb`.
- Run notebook development, export, staging, commits, pulls, and pushes inside the Dev Container. Use VS Code forwarding of the host credential helper or SSH agent; never bake credentials into the image or repository.
- `postStartCommand` registers required notebook filters, diff/merge drivers, and local LFS configuration. `postAttachCommand` configures the live VS Code host credential proxy. CLI-only startup does not replace VS Code attachment for authentication checks.
- Keep outputs in working notebooks for inspection and export. Every indexed/committed code cell must have `outputs: []` and `execution_count: null`.
- Do not use `keep_output` or `init_cell` metadata/tags. Verify the actual index with `git show :competitions/<competition-slug>/<notebook>.ipynb` before committing.
- Keep `.ipynb` and small JSON manifests in regular Git. Use Git LFS for `reports/**/*.html`; do not rewrite published history during conversion.
- Use LF text files. Ignore environments, caches, credentials, input data, models, checkpoints, and temporary artifacts while keeping report HTML trackable.

## Reports and GitHub Pages

- Use `/usr/bin/python3 scripts/export_report.py competitions/<slug>/<notebook>.ipynb` to export saved execution outputs. The command does not execute cells.
- Include code, Markdown, tables, plots, text output, and training logs. Preserve interactive Plotly behavior and embed required resources for standalone HTML.
- Rerun computational changes before export. Markdown-only edits do not require retraining.
- Export writes a sibling JSON manifest with source and HTML hashes. `scripts/build_pages.py` rejects stale pairs and unresolved LFS pointers. Hashes verify file correspondence, not execution provenance.
- Commit source and matching report/manifest together. Verify notebook output stripping and preservation of working outputs.
- Deploy **from `main` only**. The push trigger, manual-run job condition, and `github-pages` environment branch policy enforce this. Feature branches and pull requests do not publish.
- Pages Actions downloads LFS content, validates report/source identity with standard-library Python, and publishes only report HTML and a generated index. Do not upload the repository root.
- Verify published links, referenced resources, Plotly figures, legends, and error-gallery captions after publishing. See `docs/report-publishing.md`.
- Notebook push and competition prediction submission are separate actions. Neither report export nor training submits a competition entry automatically.

## Validation and current status

- The environment/report workflow is merged into `main`. New competition work starts on a dedicated branch; merge into `main` when ready to publish. Reports are available at `https://ootzk.github.io/Kaggle/`.
- Ubuntu Dev Container startup, non-root workspace ownership, scientific imports, `/usr/bin/python3`, effective resource limits, and real PyTorch CUDA computation have passed validation. Repeat after image updates.
- Notebook Git checks passed for output stripping, working-output preservation, diff/merge, fresh-repository registration, and original-index preservation. GitHub authentication through the attached VS Code proxy passed.
- Digit Recognizer completed five-epoch local and Kaggle GPU execution. Local validation accuracy was 0.980357 and macro F1 was 0.980100; the Kaggle competition submission scored 0.97778.
- HTML export, browser interactivity, public resource checks, LFS upload/download from a fresh clone, and Pages artifact deployment passed. Detailed evidence stays under `.git/kaggle-devcontainer/`.
- The Dockerfile's Git LFS installation has been declared; a full Dev Container rebuild after that addition has not yet been validated. Preserve working notebooks and use the host validation helper when rebuilding.

## Routine checks

- After a base image or Dockerfile update: run `bash .devcontainer/validate.sh` from the Ubuntu host; use `--rebuild` when recreation is needed. Check existing local validation status before launching another run.
- Before launching VS Code, export `KAGGLE_HOST_UID=$(id -u)` and `KAGGLE_HOST_GID=$(id -g)`. The host validation helper sets them automatically.
- Inside the attached container: run `python .devcontainer/verify_git_auth.py` for authenticated GitHub access and `python .devcontainer/verify_git_workflow.py` for notebook Git behavior.
- Confirm local/remote kernel selection interactively before execution and record each execution environment independently.
- Use `git lfs pull` to hydrate reports and `git lfs fsck` to verify LFS objects. Keep input data downloads in KaggleHub.

## References

- [Official Kaggle Python images](https://github.com/Kaggle/docker-python)
- [KaggleHub](https://github.com/Kaggle/kagglehub)
- [Kaggle notebooks](https://www.kaggle.com/docs/notebooks)
- [VS Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
- [Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
