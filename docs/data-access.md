# Kaggle data access

## Policy

Use **KaggleHub for every competition or dataset download** in notebooks and supporting development code. Existing local files can be reused. Do not introduce CLI data downloads, direct download URLs, shell download commands, or manually copied datasets as the normal input workflow.

The Kaggle CLI/API remains available for notebook push/status/output retrieval and competition submission; those operations are separate from downloading input datasets.

Use the Kaggle image's supplied `kagglehub` package. Record its version when diagnosing environment differences; do not change scientific packages to work around path assumptions.

## Authentication

For local execution, copy the repository-root `.env.example` to `.env`, set `KAGGLE_API_TOKEN`, and load it with `load_dotenv(..., override=False)`. KaggleHub reads the environment variable. Existing environment values take precedence; restart the kernel after changing a token that was already loaded.

Never print credentials or place them in notebook source, saved outputs, reports, or tracked files. Accept any required competition rules in Kaggle. Remote Kaggle sessions use their own authentication and cannot access the local `.env`.

## Competition inputs

The notebook resolves its project directory to `competitions/<competition-slug>/` locally. After loading local authentication, use:

```python
from pathlib import Path
import kagglehub
import pandas as pd

# project_dir is the competition directory in the current execution environment.
data_dir = Path(
    kagglehub.competition_download(
        "digit-recognizer",
        output_dir=str(project_dir / "data"),
    )
)
train = pd.read_csv(data_dir / "train.csv")
```

An existence check may skip the call when the required CSVs already exist. Let KaggleHub manage downloads and caching; do not force a redownload just because the notebook is reopened.

## Dataset inputs

Use `kagglehub.dataset_download("owner/dataset-slug", ...)` for standalone Kaggle datasets. Record the handle and any required version in the notebook. Keep downloaded files inside the competition's ignored data directories.

## Local and remote paths

- **Local:** keep input files under `competitions/<competition-slug>/data/`. The bind mount preserves them across container replacement.
- **Kaggle:** KaggleHub can resolve or attach data in the remote environment and may ignore `output_dir`. Always read from its returned path, rather than constructing a `/kaggle/input/...` path.
- **Generated files:** use the competition's `output/` directory locally and a writable directory under `/kaggle/working` remotely. Keep outputs separate from read-only input mounts.
- **Reports:** export saved notebook outputs to `reports/<competition-slug>/`. Reports are tracked; input data and generated CSVs are ignored.

Notebook source stays local when using a remote Jupyter kernel, but its Python code runs against the remote filesystem. Local data and `.env` are not uploaded automatically.

See the [official KaggleHub documentation](https://github.com/Kaggle/kagglehub) for resource handles, authentication, and download behavior.
