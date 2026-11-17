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

## CNN baseline and fixed split

`baseline.ipynb` trains the Digit Recognizer CNN architecture for ten fixed epochs with Adam (learning rate 0.001) and batch size 256. Only the training partition of `train.csv` is used for fitting; Dig-MNIST is evaluated after the final epoch and never used for optimization or checkpoint selection.

TRAIN is stored in one PyTorch `TensorDataset`. Scikit-learn creates stratified row indices, `Subset` selects the training and validation rows without copying the image arrays, and `DataLoader` forms batches. Only the training loader shuffles; validation and inference retain row order. Dig-MNIST and test inference also use tensor datasets and loaders.

The split settings are defined once inside the notebook:

- Seed **42**, stratified by `label`.
- **80% training / 20% validation**: 48,000 and 12,000 rows for the current CSV.
- Split original CSV row positions before any sorting, filtering, augmentation, or concatenation.
- Keep split seed separate from model and DataLoader random state when changing experiments.

Comparison notebooks should use the same settings and original CSV row order:

```python
import numpy as np
from sklearn.model_selection import train_test_split

split_config = {"seed": 42, "validation_fraction": 0.2, "stratify_column": "label"}
train_indices, valid_indices = train_test_split(
    np.arange(len(train)),
    test_size=split_config["validation_fraction"],
    random_state=split_config["seed"],
    stratify=train[split_config["stratify_column"]].to_numpy(),
)
```

No external split configuration file is needed locally or remotely. The baseline saves the training CSV SHA-256, scikit-learn version, and complete split row positions in `output/baseline/split_manifest.json`. Reuse these recorded positions if reproducing the partition under a different library version; verify the input file hash first. Fixing the split does not guarantee bit-identical GPU training results.

Outputs under `output/baseline/` include final weights, learning curves in the working notebook, training/per-digit metric CSVs, separate validation and Dig-MNIST summaries, confident-error tables, and `submission.csv`. Test IDs come from the supplied `id,label` template; no test accuracy is computed without ground truth. No upload or submission is performed automatically.

Local ten-epoch run with tensor subsets: validation accuracy **0.993000** (macro F1 **0.993007**); Dig-MNIST accuracy **0.716895** (macro F1 **0.713235**). These scores use the final epoch and the fixed split above.

## Remote exploration

`kernel-metadata.json` configures the private GPU baseline notebook at `pocariblitz/kannada-mnist-baseline`, with the competition data attached. Internet is enabled for development execution; this is not a final scoring configuration. Notebook push runs the baseline but does not submit predictions to the competition.

For an interactive session, select the remote Kaggle Jupyter kernel and check the environment before running. KaggleHub may ignore `output_dir` on Kaggle; use its returned path. Generated files belong under a writable `/kaggle/working` directory remotely.

## Next steps

- Inspect the EDA and ten-epoch baseline with overall/per-digit metrics and error inspection.
- Evaluate the held-out validation split and Dig-MNIST separately.
- Export a completed local notebook using `/usr/bin/python3 scripts/export_report.py competitions/Kannada-MNIST/eda.ipynb`.
- Reports will be stored under `reports/Kannada-MNIST/`. No report is published until an executed export and its manifest exist and are merged into `main`.

See [data access](../../docs/data-access.md) and [report publishing](../../docs/report-publishing.md) for the shared workflow.

For code-competition submission, the notebook writes `/kaggle/working/submission.csv` at the Kaggle output root. Select `submission.csv` from the completed notebook version when submitting. Locally, predictions remain in `output/baseline/submission.csv`; auxiliary metrics and weights stay in the baseline artifact directory.
