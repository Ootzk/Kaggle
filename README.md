# Kaggle

Kaggle notebook source and published execution reports, organized by competition.

- [Published reports](https://ootzk.github.io/Kaggle/)
- [Digit Recognizer — Baseline](https://ootzk.github.io/Kaggle/digit-recognizer/baseline.html)

## Development environment

Use one VS Code Dev Container for notebook development, execution, HTML export, and Git operations. The Ubuntu host supplies Docker Engine, the NVIDIA driver and Container Toolkit, and forwarded Git authentication.

The container has two parts:

| Part | Responsibility |
| --- | --- |
| Official `gcr.io/kaggle-gpu-images/python:latest` | GPU runtime, `/usr/bin/python3`, and the supplied scientific/notebook packages |
| Repository management layer in [Dockerfile](.devcontainer/Dockerfile) | Non-root workspace user, isolated notebook Git tools, and Git LFS |

Keep scientific packages from the base image. Manage Git tools at explicit versions under `/opt/kaggle-git-tools`; they do not replace the notebook interpreter. The base deliberately follows `latest`: pull before rebuilding, repeat validation, and keep resolved digests and machine diagnostics in untracked local logs.

See [Ubuntu setup](docs/ubuntu-setup.md) for container startup, GPU validation, Git filters, and authentication.

## Repository layout

```text
competitions/<competition-slug>/
  baseline.ipynb          # regular Git; committed without outputs
  kernel-metadata.json   # Kaggle execution settings, when needed
  data/                  # ignored local data
  output/                # ignored generated artifacts
reports/<competition-slug>/
  baseline.html          # Git LFS; includes execution outputs
  baseline.json          # regular Git; source/report identity
```

Competition directory names follow their Kaggle URL slugs. Working notebooks retain outputs; the Git clean filter strips outputs and execution counts from the index. HTML preserves code, Markdown, tables, plots, and logs. After cloning, use `git lfs pull` if reports appear as pointer files.

## Workflow

1. Open the repository in the Kaggle GPU Dev Container and confirm the intended kernel.
2. Obtain competition and dataset inputs through **KaggleHub**. Reuse existing local data; always use the path returned by KaggleHub when resolving or downloading it. See [data access](docs/data-access.md).
3. Develop and execute locally. For Kaggle GPU execution, select its remote Jupyter kernel or push a private notebook; check the environment independently.
4. Save local execution outputs and [export the report](docs/report-publishing.md) inside the container. Export does not retrain the model.
5. Commit source, HTML, and its manifest together, then push the feature branch and merge into `main` when ready.
6. GitHub Pages deploys matching reports from **`main` only**. Feature branches and pull requests do not publish.

Kaggle notebook execution and competition prediction submission are separate actions. The [Digit Recognizer guide](competitions/digit-recognizer/README.md) covers the current baseline. [AGENTS.md](AGENTS.md) records repository rules.
