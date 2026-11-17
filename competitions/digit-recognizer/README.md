# Digit Recognizer

## Baseline

A small PyTorch CNN trained for five epochs on a stratified 80/20 split with seed 42. The notebook records the environment and evaluates validation accuracy, precision, recall, F1, and digit-level errors.

- [Competition](https://www.kaggle.com/competitions/digit-recognizer)
- [Data description](https://www.kaggle.com/competitions/digit-recognizer/data)
- [Published baseline report](https://ootzk.github.io/Kaggle/digit-recognizer/experiments-baseline.html)
- [Private Kaggle notebook](https://www.kaggle.com/code/pocariblitz/digit-recognizer-gpu-baseline)

## Local execution

1. Open `experiments-baseline.ipynb` in the Kaggle GPU Dev Container and select `/usr/bin/python3`.
2. Configure `KAGGLE_API_TOKEN` in the repository-root `.env` using `.env.example`. Accept the competition rules if required.
3. Run the environment cell and confirm CUDA computation succeeds.
4. Run the remaining cells. Existing `data/train.csv` and `data/test.csv` are reused. Missing data is downloaded with `kagglehub.competition_download`; the returned directory is used to read the CSVs.
5. Inspect the figures and generated files under `output/`.

The notebook locates this competition directory from the repository root or a directory inside the repository. It loads the root `.env` with `load_dotenv(override=False)`; KaggleHub reads the token from the environment. Restart the kernel after changing an already-loaded token. See [data access](../../docs/data-access.md) for the shared policy.

Local `data/` and `output/` are ignored directories in the bind-mounted repository and survive container replacement.

## Remote Kaggle execution

For interactive execution, start a Kaggle GPU Jupyter session, connect VS Code using its compatible server URL, and select the remote Python kernel for the local notebook. Run the environment cell before training. KaggleHub resolves the remote data path; it may ignore `output_dir`. Results stay on the server, normally under `/kaggle/working/digit-recognizer/output/`.

For batch execution, `kernel-metadata.json` targets `pocariblitz/digit-recognizer-gpu-baseline` with GPU, internet access, Digit Recognizer competition data, and `is_private: true`. Package the intended output-stripped notebook source and metadata before `kaggle kernels push`. Exclude `.env` and local files from that package. The API or CLI may push notebooks, inspect status, retrieve run outputs, and submit predictions; input downloads always use KaggleHub.

A notebook push creates and runs a version; it does not submit predictions to the competition. Never commit connection URLs or tokens. Record and inspect local and remote environments independently; GPU results can differ.

## Results

- Local five-epoch validation accuracy: **0.980357**; macro F1: **0.980100**.
- Kaggle competition submission accuracy: **0.97778**.

Validation uses the held-out labeled split; the leaderboard evaluates the competition test set. These are separate measurements.

## Interactive diagnostics

Plotly displays label counts, one training example per digit, training/validation loss, overall accuracy, precision/recall/F1 curves, a confusion matrix, and final digit-level metrics.

The metric legend toggles `Overall (macro)` and digits 0–9 across all three panels. The final gallery shows the ten most confident validation errors in descending order, with true/predicted labels and their probabilities below each image. Softmax scores are not calibrated confidence estimates.

Generated files include `submission.csv`, `training_history.csv`, and `validation_metrics_by_digit.csv`. No competition submission is sent automatically.

## Report export

Save outputs, then run from the repository root:

```bash
/usr/bin/python3 scripts/export_report.py competitions/digit-recognizer/experiments-baseline.ipynb
```

The report and manifest go to `reports/digit-recognizer/`. Export does not execute cells. Follow [report publishing](../../docs/report-publishing.md) for preview, Git LFS, and `main`-only Pages deployment.
