# Kaggle

Kaggle notebooks and HTML execution reports, organized by competition and versioned with Git.

## Workflow

1. Develop notebooks in VS Code using a Dev Container based on the official Kaggle GPU image, with the local project directory mounted.
2. Use a Windows machine with an NVIDIA GPU for local development. Connect VS Code to a remote Kaggle Jupyter kernel to execute with Kaggle server resources.
3. Export execution results to HTML with cell outputs included using tools in the Dev Container.
4. Commit notebook source and HTML reports from the development machine, push to GitHub, and publish reports through GitHub Pages.
5. Submit competition entries on Kaggle.

Git tracks notebook code and Markdown with cell outputs and execution counts stripped. Execution results are preserved in HTML reports. Git operations and GitHub authentication are managed on the development machine.

## Organization

Each competition has a directory at the repository root, named after its Kaggle competition slug. The directory contains its notebooks and HTML reports.

Store local data in `data/`, `datasets/`, or `input/`, and generated files in `output/`, `working/`, `models/`, `checkpoints/`, `submissions/`, `logs/`, `runs/`, `tmp/`, or `temp/`. These directories are ignored at the repository root and directly inside each competition. Keep HTML reports and their resources outside these directories so Git can track them. Data and model file extensions are not ignored globally; use the designated directories.

Environment files and credentials are ignored; `.env.example` and `.env.template` remain trackable. Text files use LF across Windows and Linux, with CRLF for Windows `.bat` and `.cmd` scripts.

## Setup Status

The Windows Dev Container configuration is in [`.devcontainer/devcontainer.json`](.devcontainer/devcontainer.json). It uses the official Kaggle GPU `v172` image pinned by digest, requests the NVIDIA GPU, and mounts this repository at `/workspaces/Kaggle`. It uses the image's Python environment without installing or upgrading scientific packages.

Follow [Windows setup and validation](docs/windows-setup.md) before opening the container. Container execution validation is tracked there separately from configuration checks.

Notebook output filtering, HTML export, and GitHub Pages deployment are pending. Use Windows Git for this checkout. Remote Kaggle connection verification remains deferred.

See [AGENTS.md](AGENTS.md) for development guidelines, handoff details, and the setup sequence.
