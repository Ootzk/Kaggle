# Project Guidelines

This repository tracks Kaggle notebook source and HTML execution reports with Git. Development will use VS Code Dev Containers on Windows with an NVIDIA GPU, based on the official Kaggle GPU image. Notebook execution on a remote Kaggle Jupyter kernel remains part of the workflow.

## Repository Structure

- Create one directory per competition at the repository root.
- Use the competition slug from its Kaggle URL as the directory name.
- Store all notebooks for a competition in its directory.
- Use descriptive notebook names such as `eda.ipynb`, `baseline.ipynb`, and `train_catboost.ipynb`.
- Store HTML reports within the corresponding competition directory. Choose report subdirectories and naming conventions when implementing publishing.

## Development Environment

- Use the official `gcr.io/kaggle-gpu-images/python` image as the Dev Container base and pin a tested version or digest.
- Use the Python and scientific packages supplied by that image. Manage additional development tools explicitly and preserve compatibility with the base environment.
- Define the VS Code container configuration in `.devcontainer/` and track it with Git.
- Mount the local repository into the container so edits persist on the development machine.
- Configure the Python and Jupyter extensions for the container environment.
- Run notebook development tools and HTML export inside the container. Manage host Git tools explicitly in `pyproject.toml` and `uv.lock`, and run them from the Windows `.venv` created by `uv sync --locked`.
- On Windows, verify Docker GPU access through the WSL2 backend and the NVIDIA driver before relying on local GPU execution.
- Validate container startup, Python imports, and local GPU access on the Windows machine.
- Select the remote Kaggle Jupyter kernel when executing with Kaggle server resources. Confirm the selected kernel before running a notebook.
- Record the Python and relevant package versions for reproducibility. Verify local and remote environments independently.
- Keep shared documentation at the Windows + NVIDIA GPU level. Do not include workstation-specific GPU models, resource allocations, OS builds, installed host-tool versions, or local troubleshooting history. Keep reproducible container image pins and required software settings; store detailed machine diagnostics in untracked local logs.

## Development and Version Control

- Treat notebooks in the local repository as the source of truth.
- Run commit, push, and pull operations from the development machine using its GitHub authentication. Choose the Windows or WSL Git environment during setup.
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
5. Stage changes using host-side Git and verify that notebook outputs and execution counts are stripped from the staged version.
6. Commit the notebook source and HTML report, then push to GitHub.
7. Publish the HTML report through GitHub Pages and submit competition entries on Kaggle.

Account for data paths, attached datasets, required packages, and accelerator settings. Code executed on the remote Kaggle kernel reads files from the Kaggle server filesystem. Record execution requirements in notebook code or Markdown.

## HTML Reports

- Include relevant tables, plots, text output, and training logs in HTML reports.
- Track HTML reports with Git and publish them through GitHub Pages.
- Export HTML from the working notebook with outputs available.
- Verify that referenced images and files remain accessible after publishing.
- Verify that each updated report corresponds to the accompanying notebook source.

## Handoff Status

- Work is on branch `setup/dev-container-workflow`.
- The initial workflow documentation and the Dev Container decision have been committed.
- Remote Kaggle connection verification was explicitly deferred by the user.
- Use Windows Git for this checkout.
- `.gitignore` excludes local environments, caches, credentials, and designated data/artifact directories at the root and directly inside each competition. Keep HTML reports and resources outside those directories. `.gitattributes` uses LF for text and CRLF for Windows command scripts.
- Windows Git uses `nbstripout`, declared in the `dev` dependency group in `pyproject.toml` and locked with its transitive dependencies in `uv.lock`. Run `uv sync --locked`, then `uv run --locked nbstripout --install --attributes .gitattributes` after each clone or repository move. Check registration with `uv run --locked nbstripout --is-installed`. Inspect indexed notebooks with `git show :competition-slug/notebook.ipynb` before committing. Keep the Windows `.venv` for host Git tools and use the Kaggle image's Python for notebook execution and HTML export.
- Do not use notebook or cell metadata/tags that tell `nbstripout` to retain outputs (`keep_output` or `init_cell`); committed code cells must always have empty outputs and null execution counts.
- `nbdime` is also managed in the host `dev` dependency group and `uv.lock`. `.gitattributes` uses its `jupyternotebook` diff/merge drivers while retaining the `nbstripout` clean filter. Follow `docs/windows-setup.md` to register drivers with explicit Windows `.venv/Scripts` paths so host Git works without environment activation.
- `.devcontainer/devcontainer.json` now pins the official GPU `v172` image by digest, mounts the local repository, requests GPU access, and configures Python/Jupyter extensions without changing the image's scientific packages.
- `.devcontainer/verify_environment.py` records package versions and checks a real PyTorch CUDA operation. Run it inside the container before claiming the image is tested.
- `.devcontainer/validate.ps1` starts the configured container with the installed VS Code Dev Containers CLI and runs the Python check. Host-only logs and current status are in `.git/kaggle-devcontainer/`. Check them before starting another validation process.
- NVIDIA GPU visibility was verified on Windows, in WSL2, and in a CUDA container using `--gpus all`.
- The pinned Kaggle GPU image downloaded successfully. Dev Container CLI startup, the workspace bind mount, scientific/notebook imports, and an actual PyTorch CUDA computation passed. The configured interpreter is `/usr/bin/python3`. See `docs/windows-setup.md` and untracked local validation logs for evidence. VS Code UI startup, extensions, and notebook kernel selection remain to be checked interactively.
- HTML export and Pages setup remain to be implemented. Remote Kaggle verification remains deferred.

## Next Steps on Windows

1. Verify the NVIDIA driver, WSL2, Docker GPU access, and the VS Code Dev Containers extension.
2. Configure the official Kaggle GPU image as the Dev Container base. Verify startup, Python imports, and GPU access.
3. After a fresh clone, install the host-side notebook output filter and verify staged notebooks using the commands above.
4. Configure and test HTML export with tables and plots.
5. Verify the Kaggle remote connection when the user is ready. Start a Kaggle session, open `Run > Kaggle Jupyter Server`, and use the `VS Code Compatible URL` in VS Code's remote Jupyter server picker.
6. Choose HTML report paths and configure GitHub Pages deployment.
7. Update these instructions with the commands and settings actually tested.

## References

- [Official Kaggle Python images](https://github.com/Kaggle/docker-python)
- [Kaggle notebook and Jupyter server documentation](https://www.kaggle.com/docs/notebooks)
- [VS Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
- [Docker Desktop GPU support on Windows](https://docs.docker.com/desktop/features/gpu/)
