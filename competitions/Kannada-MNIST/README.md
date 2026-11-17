# Kannada-MNIST

Classify handwritten Kannada digits (0–9) from 28 × 28 grayscale images.

- [Competition](https://www.kaggle.com/competitions/Kannada-MNIST)
- [Data](https://www.kaggle.com/competitions/Kannada-MNIST/data)
- [Evaluation](https://www.kaggle.com/competitions/Kannada-MNIST/overview/evaluation)
- [Rules](https://www.kaggle.com/competitions/Kannada-MNIST/rules)
- [Original dataset](https://github.com/vinayprabhu/Kannada_MNIST)

## Starting point

`eda.ipynb` checks the selected GPU environment, resolves data through KaggleHub, validates schemas, and displays Plotly label distributions and representative digits. It does not train a model or submit predictions.

1. Open the notebook in the existing Kaggle GPU Dev Container.
2. Select `/usr/bin/python3` and run the environment cell to confirm CUDA access.
3. Use the repository-root `.env` for local `KAGGLE_API_TOKEN` authentication. The notebook loads it with `load_dotenv(override=False)`; it does not print credentials.
4. Run the remaining cells. Existing CSVs in `data/` are reused; missing inputs are downloaded with `kagglehub.competition_download("Kannada-MNIST", ...)`. Always read the returned directory.

The competition slug and directory preserve the URL's case: `competitions/Kannada-MNIST/`. Local `data/` and `output/` are ignored and persist in the repository bind mount. Remote kernels use their own filesystem and authentication.

## Files and evaluation

| File | Initial use |
| --- | --- |
| `train.csv` | Labeled development data; reserve a fixed stratified validation split for the baseline |
| `test.csv` | Competition test pixels with `id` values |
| `sample_submission.csv` | Submission column order and IDs: `id,label` |
| `Dig-MNIST.csv` | Separate labeled challenge set, held out from initial training |

Do not confuse this competition's `id` column with Digit Recognizer's `ImageId`. Read the template and retain its IDs and ordering. Do not hard-code test row counts in a future prediction pipeline.

This historical competition ended in 2019 and uses **code submissions** evaluated by classification accuracy. A simple local CSV upload is not the submission workflow used for Digit Recognizer. Check current rules and scoring requirements before submitting; no submission is performed by this setup.

## Remote exploration

`kernel-metadata.json` configures a new private GPU EDA notebook at `pocariblitz/kannada-mnist-eda`, with the competition data attached. Internet is enabled for exploration; this is not a final scoring configuration. No remote notebook has been pushed yet.

For an interactive session, select the remote Kaggle Jupyter kernel and check the environment before running. KaggleHub may ignore `output_dir` on Kaggle; use its returned path. Generated files belong under a writable `/kaggle/working` directory remotely.

## Next steps

- Inspect the EDA, then add a CNN baseline with overall/per-digit metrics and error inspection.
- Evaluate the held-out validation split and Dig-MNIST separately.
- Export a completed local notebook using `/usr/bin/python3 scripts/export_report.py competitions/Kannada-MNIST/eda.ipynb`.
- Reports will be stored under `reports/Kannada-MNIST/`. No report is published until an executed export and its manifest exist and are merged into `main`.

See [data access](../../docs/data-access.md) and [report publishing](../../docs/report-publishing.md) for the shared workflow.
