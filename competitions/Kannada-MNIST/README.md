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
| `Dig-MNIST.csv` | Fixed 80/20 split: mixed may train on 80%; both models evaluate on the same 20% |

Do not confuse this competition's `id` column with Digit Recognizer's `ImageId`. Read the template and retain its IDs and ordering. Do not hard-code test row counts in a future prediction pipeline.

This historical competition ended in 2019 and uses **code submissions** evaluated by classification accuracy. A simple local CSV upload is not the submission workflow used for Digit Recognizer. Check current rules and scoring requirements before submitting; no submission is performed by this setup.

## CNN baseline and fixed split

`experiment-cnn-baseline.ipynb` trains the Digit Recognizer CNN architecture for ten fixed epochs with Adam (learning rate 0.001) and batch size 256. Only the training partition of `train.csv` is used for fitting; only the held-out 20% Dig-MNIST subset is evaluated after the final epoch. Baseline never uses Dig-MNIST for optimization or checkpoint selection.

TRAIN is stored in one PyTorch `TensorDataset`. Scikit-learn creates stratified row indices, `Subset` selects the training and validation rows without copying the image arrays, and `DataLoader` forms batches. Only the training loader shuffles; validation and inference retain row order. Dig-MNIST and test inference also use tensor datasets and loaders.

The split settings are defined once inside the notebook:

- Seed **42**, stratified by `label`.
- **TRAIN 80/20**: 48,000 learning rows and 12,000 validation rows.
- **Dig-MNIST 80/20**: 8,192 learning rows and 2,048 validation rows; split independently with the same seed and stratification.
- Baseline does not fit on Dig learning rows; mixed adds only those rows. Both validation partitions stay excluded from fitting.
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
dig_train_indices, dig_valid_indices = train_test_split(
    np.arange(len(dig_mnist)),
    test_size=split_config["validation_fraction"],
    random_state=split_config["seed"],
    stratify=dig_mnist[split_config["stratify_column"]].to_numpy(),
)
```

No external split configuration file is needed locally or remotely. Both notebooks save TRAIN and Dig-MNIST CSV hashes, the scikit-learn version, and both complete split row lists in their respective `output/baseline/split_manifest.json` and `output/mixed/split_manifest.json` files. Reuse these recorded positions if reproducing the partition under a different library version; verify the input file hash first. Fixing the split does not guarantee bit-identical GPU training results.

Outputs under `output/baseline/` include final weights, learning curves in the working notebook, training/per-digit metric CSVs, separate validation and Dig-MNIST summaries, confident-error tables, and `submission.csv`. Test IDs come from the supplied `id,label` template; no test accuracy is computed without ground truth. No upload or submission is performed automatically.

## Mixed-data experiment

`experiment-cnn-mixed.ipynb` uses the same CNN, optimizer, learning rate, batch size, model seed, ten epochs, and both split definitions as baseline. PyTorch `ConcatDataset` combines the 48,000-row TRAIN learning subset with the 8,192-row Dig learning subset. Training contains 56,192 examples; the 12,000 TRAIN validation and 2,048 Dig validation images remain held out.

Compare both models using the exact same validation rows from each source. Dig-MNIST validation is now a held-out metric for mixed too. Once repeatedly used for model development, these are validation scores, not an untouched final test. The 2,048-row Dig holdout is suitable for an initial comparison; small score differences warrant further confirmation.

Artifacts go to separate `output/baseline/` and `output/mixed/` directories. Mixed still has more batches per epoch, so equal epochs do not mean equal optimizer updates. Neither notebook trains on competition test images or submits predictions automatically.

### Consolidated results

See [report.ipynb](report.ipynb) for cross-experiment result tables, graphs, and interpretation. Individual experiment notebooks document their own configuration, diagnostics, and observed properties.

## Remote exploration

`experiment-cnn-baseline.kaggle.json` configures the private GPU baseline notebook at `pocariblitz/kannada-mnist-baseline`, with the competition data attached. Internet is disabled because the competition forbids it. The competition data is attached through the notebook metadata; KaggleHub resolves that data in the Kaggle environment. Local missing-input downloads still use KaggleHub with local authentication. Notebook push runs the baseline but does not submit predictions to the competition.

`experiment-cnn-mixed.kaggle.json` provides the matching private GPU, internet-disabled configuration for `pocariblitz/kannada-mnist-mixed`. Package it as `kernel-metadata.json` beside the committed `experiment-cnn-mixed.ipynb` when pushing mixed; keep the baseline metadata and source in a separate package. Both notebooks attach `Kannada-MNIST` and produce a root-level `submission.csv` on Kaggle.

For an interactive session, select the remote Kaggle Jupyter kernel and check the environment before running. KaggleHub may ignore `output_dir` on Kaggle; use its returned path. Generated files belong under a writable `/kaggle/working` directory remotely.

## Next steps

- Inspect the EDA and ten-epoch baseline with overall/per-digit metrics and error inspection.
- Evaluate the held-out validation split and Dig-MNIST separately.
- Export a completed local notebook using `/usr/bin/python3 scripts/export_report.py competitions/Kannada-MNIST/eda.ipynb`.
- Reports will be stored under `reports/Kannada-MNIST/`. No report is published until an executed export and its manifest exist and are merged into `main`.

See [data access](../../docs/data-access.md) and [report publishing](../../docs/report-publishing.md) for the shared workflow.

For code-competition submission, the notebook writes `/kaggle/working/submission.csv` at the Kaggle output root. Select `submission.csv` from the completed notebook version when submitting. Locally, predictions remain in `output/baseline/submission.csv`; auxiliary metrics and weights stay in the baseline artifact directory.

## Final fit and consolidated report

`submission-cnn.ipynb` initializes the same CNN from scratch and trains for ten epochs on all 60,000 TRAIN plus all 10,240 Dig-MNIST rows. There is no validation split, early stopping, or checkpoint selection. Training curves are optimization diagnostics, not held-out performance. Outputs go to `output/submission/` locally, including `model.pt`, `training_history.csv`, `training_manifest.json`, and `submission.csv`. Kaggle writes the CSV at `/kaggle/working/submission.csv`.

`submission-cnn.kaggle.json` defines a separate private GPU notebook with internet disabled. Package it as `kernel-metadata.json` with `submission-cnn.ipynb` only when intentionally starting a remote run. Creating this notebook does not push, run, or submit it on Kaggle.

`report.ipynb` describes the CNN and K-means methods and embeds one completed local run per experiment and the verified baseline v3, Mixed v1, and full-data v1 competition scores. Its tables and Plotly charts render without local training artifacts or authentication. Experimental validation uses local results only; Kaggle run validation results are excluded. The shared CNN is defined in code and summarized with the image-supplied `torchinfo`, including layer shapes and parameter counts; no additional visualization package is required. Queued/canceled runs are excluded. Mixed v1 scored public 0.96800 / private 0.96780; full-data v1 scored public 0.96120 / private 0.96420. The full-data fit did not improve on Mixed in this run; its training accuracy is not a validation metric. Update the report snapshot and provenance together when adding completed results.

Experimental artifact directory names remain `output/baseline/` and `output/mixed/`; renaming the source notebooks does not rename or discard existing execution results. Existing Kaggle notebook slugs remain unchanged as well.


## K-means pixel baseline

`experiment-kmeans-pixels.ipynb` provides a CPU scikit-learn KMeans reference using 784 float32 pixels divided by 255. It fits centers on 48,000 TRAIN learning rows and maps clusters to the majority digit using those learning labels only. Both original held-out partitions remain excluded from fitting and mapping; no Dig-MNIST learning rows or competition test images are used for training.

The fixed settings are K=10, k-means++ initialization, 50 independent k-means++ initializations with one fit per recorded seed, at most 300 Lloyd iterations per fit, tolerance 0.0001, master random seed 42, and one numerical thread. Generate 50 distinct seeds deterministically; select the smallest TRAIN-learning inertia, retaining the first run for exact ties. Store every run seed, inertia, and iteration count in `restart_history.csv`; held-out metrics are evaluated only after selecting the model. Lower inertia does not guarantee higher classification accuracy. No PCA, image alignment, augmentation, or hyperparameter search is used. The objective is squared Euclidean pixel distance. Training cluster purity and centroid distances are not calibrated probabilities.

| Partition | Accuracy | Macro F1 |
| --- | ---: | ---: |
| TRAIN validation (12,000) | 74.1000% | 0.708511 |
| Dig-MNIST validation (2,048) | 36.9141% | 0.332482 |

Cluster diagnostics are ordered by mapped digit and then original cluster ID; display labels retain both. The notebook displays centroid and empirical mean/variance images, cluster membership sizes, digit counts and proportions (including a 0–9 distribution panel for each cluster), a statistics table, squared-distance box plots and normalized histograms, held-out confusion matrices, overall/per-digit metric legends, and seeded error examples with Kannada numerals. Two clusters map to digit 2 and none to 7 in this run; cluster IDs are not digit labels and the mapping need not be one-to-one.

Ignored artifacts are saved under `output/experiment-kmeans-pixels/`: the fitted model and mapping, split/run manifests, evaluation tables, error examples, and experimental test predictions. `experiment-kmeans-pixels.kaggle.json` defines a separate private CPU notebook with internet disabled and the competition attached. It has not been pushed or submitted. HTML export/publication is deferred while the notebook is being developed; keep the execution outputs in the working notebook for inspection.


The K-means notebook automatically reuses a matching local `model.joblib` cache. Its key includes the actual learning features/labels and row order, input CSV hash, preprocessing description, all initialization seeds, K-means parameters, NumPy/scikit-learn versions, and numerical-thread setting. Missing or mismatching caches trigger a fresh 50-run search. Set `FORCE_REFIT = True` in the fitting cell to force retraining. A cache hit still recomputes the label mapping, diagnostic plots, held-out evaluation, and test predictions; its recorded original training duration is distinct from the current load/fit duration.


## Pixel overclustering

`experiment-kmeans-pixels-overclustered.ipynb` fits K=30 centers on 48,000 TRAIN learning images, using normalized pixels, 50 fixed-seed initializations, and learning-inertia selection. It describes the selected model's mapped-digit coverage, class distributions, pixel statistics, and held-out results. Artifacts and the reusable cache are isolated under `output/experiment-kmeans-pixels-overclustered/`. The matching `.kaggle.json` is private, CPU-only, and internet-disabled.

## Mixed-data pixel overclustering

`experiment-kmeans-pixels-overclustered-mixed.ipynb` fits K=30 centers and the majority-label mapping on 56,192 images: 48,000 TRAIN learning rows followed by 8,192 Dig learning rows. The 12,000 TRAIN validation and 2,048 Dig validation rows are excluded. It uses normalized pixels, 50 fixed-seed initializations, learning-inertia selection, and no PCA, reweighting, or cluster-size constraint.

Artifacts and the matching-model cache live under `output/experiment-kmeans-pixels-overclustered-mixed/`. The key includes both CSV hashes, learning-row orders, and the combined features/labels. Its matching `.kaggle.json` defines a private CPU notebook with internet disabled. The notebook describes its own mixed-data clusters and held-out results.

K-means notebooks have not been pushed to Kaggle. Cross-experiment comparisons, including the K=10→30 change and Dig learning-data effect, are maintained in [report.ipynb](report.ipynb). The report embeds completed local snapshots and separately records confirmed CNN competition scores; it runs without ignored local artifacts. HTML export/publication remains deferred during development.
