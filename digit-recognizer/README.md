# Digit Recognizer GPU baseline

Open `baseline.ipynb` in the Kaggle GPU Dev Container. Use the container Python kernel for the local run.

1. Accept any required terms on the [competition page](https://www.kaggle.com/competitions/digit-recognizer/data).
2. Run the environment cell first and check the host, interpreter, and GPU.
3. Copy the repository-root `.env.example` to `.env` and set `KAGGLE_API_TOKEN` there. The file is ignored by Git; never put a token in the notebook or a tracked file. Run the data preparation cell. Existing `data/train.csv` and `data/test.csv` are used without authentication. Otherwise the cell loads the root `.env` using `load_dotenv(override=False)` from the image-supplied `python-dotenv` and reads the token through `os.environ` and downloads through `kagglehub.competition_download`. An existing `KAGGLE_API_TOKEN` environment variable takes precedence. KaggleHub reads the token from the environment without printing it. After changing `.env`, restart the kernel and rerun the notebook so previously loaded environment values do not persist. Authentication failure stops execution; check the token and competition terms before retrying.
4. Inspect validation accuracy, the confusion matrix, and `output/submission.csv`. No competition submission is performed automatically.
5. For the remote run, attach the competition data to a Kaggle GPU notebook/session. Obtain its VS Code compatible Jupyter server URL, connect VS Code to that server, and select its Python kernel for this local notebook. Check the environment cell again before training.
6. Run the same notebook on the remote GPU. Existing project CSVs are reused. Otherwise, `kagglehub.competition_download` downloads locally or resolves/attaches data on Kaggle. Always read the returned directory: Kaggle can ignore `output_dir`. Generated files go to the project `output` directory; with Kaggle’s default working directory this is `/kaggle/working/digit-recognizer/output`. Copy remote results locally if needed.

The baseline uses a stratified 80/20 split, seed 42, and a small CNN for five epochs. Versions are printed by the environment cell. GPU results can vary between runs and machines. Keep working notebook outputs for inspection; Git inside the Dev Container strips outputs when staging. HTML export follows completion of both execution checks.

Never commit Jupyter connection URLs or tokens. Connection and kernel selection require the active Kaggle session; a local CUDA check does not verify the remote environment.

Local `data/` and `output/` are real directories in the mounted Ubuntu repository, survive container replacement, and are ignored by Git.

## Interactive diagnostics

Plotly displays label counts, one image per digit, training/validation loss curves, validation accuracy and macro precision/recall/F1 curves, a confusion matrix, and per-digit metrics. The final gallery shows up to ten misclassified validation images ranked by predicted probability, with true/predicted labels and their softmax probabilities. These probabilities are not calibrated, and the examples do not imply that every error is visually ambiguous. Plotly assets are embedded by the notebook renderer for offline viewing.

Precision, recall, and F1 curves share grouped legend entries for `Overall (macro)` and digits 0–9. Overall is visible initially; click a digit to toggle it across all three panels, or double-click to isolate it. The final metric comparison uses the same target labels. Per-epoch overall and digit metrics are saved in `output/validation_metrics_by_digit.csv`.

## Private Kaggle execution

`kernel-metadata.json` targets `pocariblitz/digit-recognizer-gpu-baseline` with GPU execution, internet access, the Digit Recognizer competition data, and explicit `is_private: true`. `kernels push` uploads and runs a notebook version; it does not send its predictions to the competition leaderboard.

The first API upload used the clean notebook from Git commit `7bd2c5c`, packaged with this metadata under `.git/kaggle-devcontainer/kernel-push/`. Working outputs and `.env` were excluded. Kaggle accepted version 1 at [the private notebook](https://www.kaggle.com/code/pocariblitz/digit-recognizer-gpu-baseline). Authentication was loaded from the local `.env` using `load_dotenv()` before initializing the image-supplied `KaggleApi`.

For CLI calls from this container, load `.env` into the child process without shell-sourcing it:

```python
import subprocess
from dotenv import load_dotenv

load_dotenv(".env", override=False)
subprocess.run(
    ["kaggle", "kernels", "status", "pocariblitz/digit-recognizer-gpu-baseline"],
    check=True,
)
```

An upload can use `kaggle kernels push -p .git/kaggle-devcontainer/kernel-push` after refreshing that package from the intended clean Git commit. Confirm `is_private: true` in its metadata before uploading. Download generated artifacts into an ignored output directory; never overwrite the local notebook source with remote code automatically.
