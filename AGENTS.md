# Project Guidelines

This repository tracks Kaggle notebook source and HTML execution reports with Git. Development and version control happen locally, while execution uses Kaggle server resources.

## Repository Structure

- Create one directory per competition at the repository root.
- Use the competition slug from its Kaggle URL as the directory name.
- Store all notebooks for a competition in its directory.
- Use descriptive notebook names such as `eda.ipynb`, `baseline.ipynb`, and `train_catboost.ipynb`.
- Store HTML reports within the corresponding competition directory. Choose report subdirectories and naming conventions when implementing publishing.

## Development and Version Control

- Treat notebooks in the local repository as the source of truth.
- Edit notebooks locally, commit changes with Git, and push to GitHub.
- Apply fixes and improvements discovered during Kaggle execution to the local source.
- Manage Git operations locally throughout this workflow.
- Track code and Markdown in `.ipynb` files. Before committing, clear code-cell `outputs` to an empty array and set `execution_count` to `null`.
- Preserve execution results in HTML reports.

## Execution and Competition Submission

1. Develop the notebook locally.
2. Connect the local notebook environment to a Kaggle Jupyter kernel.
3. Execute with Kaggle server resources and inspect the results.
4. Export the executed notebook to HTML with cell outputs included.
5. Clear cell outputs and execution counts from the source `.ipynb`.
6. Commit the notebook source and HTML report locally, then push to GitHub.
7. Publish the HTML report through GitHub Pages and submit competition entries on Kaggle.

Account for Kaggle data paths, required packages, and accelerator settings. Record execution requirements and reproducibility details in notebook code or Markdown.

## HTML Reports

- Include relevant tables, plots, text output, and training logs in HTML reports.
- Track HTML reports with Git and publish them through GitHub Pages.
- Export HTML before clearing notebook outputs to preserve the execution results.
- If a report references external images or files, verify that those resources remain accessible after publishing.
- When updating a report, verify that it corresponds to the accompanying notebook source.

## Pending Implementation Decisions

This document defines the agreed workflow. The following tools and settings remain to be selected and verified.

- The connection method between the local environment and a Kaggle Jupyter kernel
- The HTML export tool and command
- GitHub Pages publishing paths and deployment method
- Whether to automate clearing cell outputs and execution counts

When implementing these steps, verify the available connection methods and update this document with tested settings and commands.
