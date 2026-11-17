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
- Run development tools and HTML export inside the container.
- On Windows, verify Docker GPU access through the WSL2 backend and the NVIDIA driver before relying on local GPU execution.
- Validate container startup, Python imports, and local GPU access on the Windows machine.
- Select the remote Kaggle Jupyter kernel when executing with Kaggle server resources. Confirm the selected kernel before running a notebook.
- Record the Python and relevant package versions for reproducibility. Verify local and remote environments independently.

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
- The earlier Microsoft Python image configuration, uv project files, ignore rules, and helper scripts were discarded when switching to the official Kaggle GPU image.
- The temporary Mac-side notebook Git filter and the nbstripout tool installed for it were removed.
- Official GPU image metadata was checked for `latest`, `v173`, and `v172`. All three reported `linux/amd64`.
- The previous Mac used ARM64. A small AMD64 Alpine container ran successfully under emulation, but the Kaggle image itself was never downloaded or launched.
- Remote Kaggle connection verification was explicitly deferred by the user.
- The repository currently contains workflow documentation. Container, output filtering, HTML export, and Pages setup remain to be implemented.

## Next Steps on Windows

1. Verify the NVIDIA driver, WSL2, Docker GPU access, and the VS Code Dev Containers extension.
2. Configure the official Kaggle GPU image as the Dev Container base. Verify startup, Python imports, and GPU access.
3. Add repository ignore rules and host-side notebook output filtering. Test that working outputs remain available and committed outputs are removed.
4. Configure and test HTML export with tables and plots.
5. Verify the Kaggle remote connection when the user is ready. Start a Kaggle session, open `Run > Kaggle Jupyter Server`, and use the `VS Code Compatible URL` in VS Code's remote Jupyter server picker.
6. Choose HTML report paths and configure GitHub Pages deployment.
7. Update these instructions with the commands and settings actually tested.

## References

- [Official Kaggle Python images](https://github.com/Kaggle/docker-python)
- [Kaggle notebook and Jupyter server documentation](https://www.kaggle.com/docs/notebooks)
- [VS Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
- [Docker Desktop GPU support on Windows](https://docs.docker.com/desktop/features/gpu/)
