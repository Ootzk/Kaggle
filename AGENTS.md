# Project Guidelines

This repository tracks Kaggle notebook source and HTML execution reports with Git. Development uses VS Code Dev Containers on a local Mac. Git operations run on the Mac, while notebook execution uses a Kaggle remote Jupyter kernel.

## Repository Structure

- Create one directory per competition at the repository root.
- Use the competition slug from its Kaggle URL as the directory name.
- Store all notebooks for a competition in its directory.
- Use descriptive notebook names such as `eda.ipynb`, `baseline.ipynb`, and `train_catboost.ipynb`.
- Store HTML reports within the corresponding competition directory. Choose report subdirectories and naming conventions when implementing publishing.

## Development and Version Control

- Treat notebooks in the local repository as the source of truth.
- Mount the local repository into a VS Code Dev Container so edits are saved to the Mac's project files.
- Run development tools, Python tooling, and HTML export inside the Dev Container.
- Run Git operations, including commit, push, and pull, from the Mac terminal using the Mac's GitHub authentication.
- Apply fixes and improvements discovered during Kaggle execution to the local source.
- Track code and Markdown in `.ipynb` files. In the committed version, code-cell `outputs` must be an empty array and `execution_count` must be `null`.
- Preserve execution results in HTML reports.

## Development Environment

- Define the development environment in `.devcontainer/` and track its configuration with Git.
- Pin the selected base image version and record additional development dependencies in reproducible configuration.
- Configure the Python and Jupyter VS Code extensions for the container environment.
- The local container uses the Mac's compute resources. Select the Kaggle remote kernel for notebook execution on Kaggle resources.
- Verify the remote connection from the VS Code Dev Container with a small notebook before relying on it for competition work.
- Configure notebook output stripping as a Git filter on the Mac. Its executable must be available to the Mac's Git process.
- Keep outputs available in the working notebook for inspection and HTML export while stripping them from the Git version.
- Ignore virtual environments, caches, notebook checkpoints, credentials, downloaded data, model files, and temporary execution artifacts. Track HTML reports and any resources they require.

## Execution and Competition Submission

1. Open the local repository in a VS Code Dev Container and develop the notebook.
2. Connect VS Code's notebook editor to a Kaggle remote Jupyter kernel.
3. Execute with Kaggle server resources and inspect the results.
4. Save the executed notebook to the mounted repository and export it to HTML with cell outputs included using the container's export tools.
5. Stage changes with Git on the Mac and verify that the Git filter removes cell outputs and execution counts from the staged `.ipynb`.
6. Commit the notebook source and HTML report on the Mac, then push to GitHub.
7. Publish the HTML report through GitHub Pages and submit competition entries on Kaggle.

Account for Kaggle data paths, required packages, and accelerator settings. Record execution requirements and reproducibility details in notebook code or Markdown.

## HTML Reports

- Include relevant tables, plots, text output, and training logs in HTML reports.
- Track HTML reports with Git and publish them through GitHub Pages.
- Export HTML from the working notebook with outputs available.
- If a report references external images or files, verify that those resources remain accessible after publishing.
- When updating a report, verify that it corresponds to the accompanying notebook source.

## Pending Setup and Verification

This document defines the agreed workflow. The following setup tasks remain to be implemented and verified.

- The Dev Container base image, development tools, and VS Code configuration
- The connection method between VS Code inside the Dev Container and a Kaggle Jupyter kernel
- The Mac-side notebook output Git filter and its installation procedure
- Repository ignore rules
- The HTML export tool and command
- GitHub Pages publishing paths and deployment method

When implementing these steps, verify the available connection methods and update this document with tested settings and commands.
