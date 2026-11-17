# Kaggle

Kaggle notebooks and HTML execution reports, organized by competition and versioned with Git.

## Workflow

1. Develop on Ubuntu with an NVIDIA GPU, using VS Code Dev Containers and the official `gcr.io/kaggle-gpu-images/python:latest` image.
2. Run locally with the container's Python kernel, then connect VS Code to a remote Kaggle Jupyter GPU kernel when Kaggle resources are needed. Check the selected kernel before execution.
3. Export executed notebooks to HTML inside the container, with tables, plots, and logs included.
4. Use Git in the Dev Container through VS Code Source Control or its terminal to commit notebook source and HTML reports, push to GitHub, and publish reports through GitHub Pages.
5. Submit competition entries on Kaggle.

Git tracks notebook code and Markdown with outputs and execution counts stripped. Working notebooks retain their results; HTML reports preserve execution results for publication. Notebook development and Git operations share one container VS Code window. VS Code forwards authentication from the Ubuntu host.

## Setup

Follow [Ubuntu GPU setup and validation](docs/ubuntu-setup.md). Docker Engine runs directly on Ubuntu and needs the NVIDIA Container Toolkit for `--gpus all`.

The [Dev Container configuration](.devcontainer/devcontainer.json) builds a thin development image from the official Kaggle GPU `latest` image. It adds a non-root user for Linux workspace ownership and installs Git tools in an isolated Python environment without upgrading the image's scientific packages. The repository is mounted at `/workspaces/Kaggle`; Python and Jupyter extensions run inside the container.

The [Dockerfile](.devcontainer/Dockerfile) declares the versions of `nbstripout` and `nbdime` and installs them in `/opt/kaggle-git-tools`. No host Python environment or project dependency manifest is needed for these tools. The notebook interpreter remains `/usr/bin/python3`.

On every container start, `.devcontainer/configure-git.sh` registers the notebook filter and diff/merge drivers in the repository's local Git configuration. Fresh clones and recreated containers use the same setup automatically. The container's Source Control integration is enabled. Run Git inside the container; its driver settings use container tools.

After VS Code attaches, its credential helper forwards requests to the host. The attachment hook routes URL-specific helpers through this proxy as well. Credentials and private authentication files are not copied into the image or repository. See [Git and authentication setup](docs/ubuntu-setup.md#notebook-git-inside-the-container).

The image deliberately follows `latest`. Pull it before rebuilding to adopt an update, then repeat environment validation. Record the resolved image digest and package versions in untracked local diagnostics rather than pinning the configuration.

## Organization and status

Store notebook source in `competitions/<competition-slug>/` and HTML reports in `reports/<competition-slug>/`. Competition slugs follow their Kaggle URLs. Put local data in `data/`, `datasets/`, or `input/`, and generated artifacts in the ignored `output/`, `working/`, `models/`, `checkpoints/`, `submissions/`, `logs/`, `runs/`, `tmp/`, or `temp/` directories at the root or directly within a competition. Keep HTML reports and required resources outside those ignored directories.

Credentials, environments, and caches are ignored. `.env.example` and `.env.template` remain trackable.

The [Digit Recognizer baseline](competitions/digit-recognizer/README.md) has completed local and Kaggle GPU execution. Its [HTML report](reports/digit-recognizer/baseline.html) preserves local outputs. See [report publishing](docs/report-publishing.md) for export, preview, and Pages deployment. See [AGENTS.md](AGENTS.md) for project guidelines and handoff status.
