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

## Setup Status

The workflow is documented. Development is moving to Windows with an NVIDIA GPU. Dev Container configuration, notebook output filtering, HTML export, and GitHub Pages deployment are pending. Remote Kaggle connection verification will be performed later.

See [AGENTS.md](AGENTS.md) for development guidelines, handoff details, and the setup sequence.
