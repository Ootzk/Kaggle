# Kaggle

Kaggle notebooks and HTML execution reports, organized by competition and versioned with Git.

## Workflow

1. Develop notebooks in VS Code using a local Dev Container with the Mac's project directory mounted.
2. Connect VS Code to a Kaggle remote Jupyter kernel and execute with Kaggle server resources.
3. Export execution results to HTML with cell outputs included using tools in the Dev Container.
4. Commit notebook source and HTML reports from the Mac, push to GitHub, and publish reports through GitHub Pages.
5. Submit competition entries on Kaggle.

Git tracks notebook code and Markdown with cell outputs and execution counts stripped. Execution results are preserved in HTML reports. Git operations and GitHub authentication are managed on the Mac.

## Organization

Each competition has a directory at the repository root, named after its Kaggle competition slug. The directory contains its notebooks and HTML reports.

See [AGENTS.md](AGENTS.md) for detailed development guidelines and pending implementation decisions.
