# Project Guidelines

This repository tracks Kaggle notebook source and HTML execution reports with Git. Development uses VS Code Dev Containers on Ubuntu with an NVIDIA GPU, based on the official Kaggle GPU `latest` image. Notebook execution on a remote Kaggle Jupyter kernel remains part of the workflow.

## Repository Structure

- Create one directory per competition under `competitions/`.
- Use the competition slug from its Kaggle URL as the directory name.
- Store all notebooks for a competition in its directory.
- Use descriptive notebook names such as `eda.ipynb`, `baseline.ipynb`, and `train_catboost.ipynb`.
- Store HTML reports under `reports/<competition-slug>/`, named after their notebook (for example `reports/digit-recognizer/baseline.html`).

## Development Environment

- Use the official `gcr.io/kaggle-gpu-images/python:latest` image as the Dev Container base. Follow `latest` deliberately; do not pin a version or digest. Pull before rebuilding and revalidate each updated image. Record its resolved digest in untracked local diagnostics.
- Use the Python and scientific packages supplied by that image. Manage additional development tools explicitly and preserve compatibility with the base environment.
- Define the VS Code container configuration in `.devcontainer/` and track it with Git.
- Mount the local repository into the container so edits persist on the development machine.
- Configure the Python and Jupyter extensions for the container environment.
- Install the checksum-verified Git LFS binary at the explicit Dockerfile version into `/opt/kaggle-git-tools/bin`, expose it to Git through `/usr/local/bin/git-lfs`, and register LFS locally during container startup. Do not rewrite published history when converting reports.
- Run notebook development tools and HTML export inside the container. Manage notebook Git tools as explicitly versioned installations in `.devcontainer/Dockerfile`, inside `/opt/kaggle-git-tools`. Keep this environment separate from the supplied scientific Python and leave the notebook interpreter at `/usr/bin/python3`. Do not require host Python development tools.
- Run Docker Engine directly on Ubuntu. Verify the NVIDIA driver and NVIDIA Container Toolkit runtime before relying on `--gpus all`. Use the current stable Docker Engine from its official Ubuntu repository.
- Validate container startup, Python imports, and local GPU access on the Ubuntu machine. Use a non-root container user matching the host UID/GID so bind-mounted files retain host ownership.
- Select the remote Kaggle Jupyter kernel when executing with Kaggle server resources. Confirm the selected kernel before running a notebook.
- Record the Python and relevant package versions for reproducibility. Verify local and remote environments independently.
- Keep shared documentation at the Ubuntu + NVIDIA GPU level. Do not include workstation-specific GPU models, resource allocations, OS builds, installed host-tool versions, or local troubleshooting history. Keep the official `latest` image reference and required software settings; store detailed machine diagnostics in untracked local logs.

## Development and Version Control

- Treat notebooks in the local repository as the source of truth.
- Run staging, commit, push, and pull from the Dev Container through VS Code Source Control or its terminal. Use VS Code forwarding of the Ubuntu host credential helper or SSH agent; never bake credentials or private authentication files into the image or repository.
- Apply fixes and improvements discovered during Kaggle execution to the local source.
- Track code and Markdown in `.ipynb` files. In the committed version, code-cell `outputs` must be an empty array and `execution_count` must be `null`.
- Configure output stripping as a Git filter in the environment that runs Git. Its executable must be available in that environment, including after a fresh clone.
- Keep outputs in the working notebook for inspection and HTML export while stripping them from the Git version.
- Preserve execution results in HTML reports.
- Ignore environments, caches, notebook checkpoints, credentials, downloaded data, models, and temporary execution artifacts. Track HTML reports and their required resources.

## Execution and Competition Submission

1. Open the local repository in the Kaggle GPU Dev Container and develop the notebook.
2. Select the intended kernel. Connect to the remote Kaggle Jupyter server for execution on Kaggle resources.
3. Execute the notebook and inspect the results.
4. Save the executed notebook to the mounted repository and export it to HTML with cell outputs included.
5. Stage changes using Git inside the Dev Container and verify that notebook outputs and execution counts are stripped from the staged version.
6. Commit the notebook source and HTML report, then push to GitHub.
7. Publish the HTML report through GitHub Pages and submit competition entries on Kaggle.

Account for data paths, attached datasets, required packages, and accelerator settings. Code executed on the remote Kaggle kernel reads files from the Kaggle server filesystem. Record execution requirements in notebook code or Markdown.

## HTML Reports

- Include relevant tables, plots, text output, and training logs in HTML reports.
- Track `reports/**/*.html` with Git LFS and publish them through GitHub Pages Actions. Keep report JSON manifests in regular Git. The workflow must download LFS content before building its artifact; unresolved LFS pointers are an error.
- Export HTML from the working notebook with outputs available.
- Verify that referenced images and files remain accessible after publishing.
- Verify that each updated report corresponds to the accompanying notebook source. Export writes a sibling JSON manifest with source and HTML hashes; Pages build rejects stale pairs.
- Publish only report HTML and the generated index. Never upload the repository root as a Pages artifact.
- `scripts/export_report.py` uses the image Python without executing cells. `scripts/build_pages.py` uses the standard library and runs in Actions without GPU/scientific dependencies.

## Handoff Status

- Work is on branch `setup/dev-container-workflow`.
- Development runs on Ubuntu. Use a single container VS Code window for notebooks and Git; the host supplies Docker and forwarded Git authentication.
- The user explicitly chose the official Kaggle GPU `latest` image. The Dev Container builds a thin image from it, adding a non-root `vscode` user and isolated Git tools without changing scientific packages. The `USER_UID`/`USER_GID` build arguments match the Ubuntu workspace owner; the validation helper supplies the host IDs through `KAGGLE_HOST_UID`/`KAGGLE_HOST_GID`. Automatic UID rewriting is disabled to avoid a redundant image build.
- `.gitignore` excludes environments, caches, credentials, data, and generated artifacts. Keep HTML reports and their required resources outside ignored directories.
- The Dockerfile pins `nbstripout`, `nbdime`, and the startup compatibility dependency `wrapt` in an isolated `/opt/kaggle-git-tools` environment. Host `.venv` and repository Python dependency manifests are not used. `postStartCommand` automatically registers required notebook Git filters and diff/merge drivers on fresh clones, recreations, and restarts. All Git work runs inside the container.
- Do not use notebook or cell metadata/tags that retain outputs (`keep_output` or `init_cell`). Inspect indexed notebooks with `git show :competitions/competition-slug/notebook.ipynb` before committing: every code cell must have empty outputs and a null execution count.
- Notebook execution and HTML export use the Kaggle image's Python, independently of the Git tools environment. The configured interpreter is `/usr/bin/python3`; validate it after image updates.
- `.devcontainer/setup-gpu.sh` installs NVIDIA Container Toolkit and configures its Docker runtime on Ubuntu with sudo. Docker restart is a separate host action because other containers may be running.
- `.devcontainer/validate.sh` pulls the configured image, starts the Dev Container using the installed CLI or VS Code extension CLI, and runs `.devcontainer/verify_environment.py` as the development user. Host-only logs and status stay in `.git/kaggle-devcontainer/`; check them before launching another validation.
- `.devcontainer/verify_git_workflow.py` verifies actual staging with a temporary index, working-output preservation, diff/merge tools, and fresh-repository registration without changing the real staging state.
- `postAttachCommand` routes container Git credentials through the live VS Code host proxy. `.devcontainer/verify_git_auth.py` verifies HTTPS GitHub authentication without printing or storing credentials. CLI-only startup skips the attachment hook; attach VS Code before testing authentication.
- The environment check records package versions, verifies non-root workspace writes, and performs a real PyTorch CUDA operation. Previous Windows verification is not evidence for Ubuntu or a newly pulled image.
- Ubuntu validation passed: the official GPU `latest` image was downloaded; Dev Container build/startup, `/usr/bin/python3`, scientific/notebook imports, non-root workspace writes with host ownership, actual PyTorch CUDA computation, and configured CPU/memory/swap limits were verified. The resolved image digest and detailed diagnostics are in `.git/kaggle-devcontainer/`. Container notebook Git staging/output preservation, diff/merge, fresh-repository initialization, and preservation of the original staging entries passed. Scientific package versions were unchanged. VS Code configured the host credential proxy on attachment; an authenticated GitHub `/user` request from the attached container passed using `python .devcontainer/verify_git_auth.py`. The local Jupyter `python3` kernel executed the baseline environment cell with `/usr/bin/python3` and passed CUDA computation; VS Code notebook kernel selection still requires an interactive check. The working baseline notebook completed local execution through submission generation with no cell errors; final local validation accuracy after five epochs was 0.9803571428571428. Local competition CSVs are present in the ignored data directory.
- `competitions/digit-recognizer/baseline.ipynb` is the GPU baseline. Local and Kaggle GPU execution passed. The Kaggle submission scored 0.97778. Export saved local outputs to `reports/digit-recognizer/baseline.html` using `scripts/export_report.py`; assemble Pages with `scripts/build_pages.py`. Confirm each kernel and record its environment independently.
- Reports are live at `https://ootzk.github.io/Kaggle/`. Initial Pages Actions run `44075475308` succeeded from commit `95ad742`; public HTTP responses and all eight Plotly figures, grouped legend toggles, and error captions passed browser verification. The setup branch and `main` are allowed to deploy; after merging, publish from `main` only. See `docs/report-publishing.md`.

## Next Steps on Ubuntu

1. After image updates, pull `latest` and repeat Dev Container validation with `bash .devcontainer/validate.sh`. Before launching VS Code, export `KAGGLE_HOST_UID=$(id -u)` and `KAGGLE_HOST_GID=$(id -g)` so the build uses the host IDs; the validation helper sets these automatically.
2. Check VS Code container extensions and choose the local Python kernel interactively.
3. Run Digit Recognizer locally, then on the remote Kaggle GPU kernel. Connect using an active Kaggle session's VS Code compatible Jupyter server URL; never commit URLs or tokens.
4. Follow `docs/report-publishing.md` to export saved outputs inside the container, validate source/report hashes, and deploy only `reports/` HTML through GitHub Pages.
5. Update these instructions with tested commands and evidence. Keep workstation-specific diagnostics in untracked local logs.

## References

- [Official Kaggle Python images](https://github.com/Kaggle/docker-python)
- [Kaggle notebook and Jupyter server documentation](https://www.kaggle.com/docs/notebooks)
- [VS Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
- [Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
