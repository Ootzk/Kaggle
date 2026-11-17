# Digit Recognizer GPU baseline

Open `baseline.ipynb` in the Kaggle GPU Dev Container. Use the container Python kernel for the local run.

1. Accept any required terms on the [competition page](https://www.kaggle.com/competitions/digit-recognizer/data).
2. Run the environment cell first and check the host, interpreter, and GPU.
3. Run the data preparation cell. It checks `digit-recognizer/data/train.csv` and `test.csv` first. When either file is missing, it calls `kagglehub.competition_download` with `output_dir` pointing to that project directory. On `UnauthenticatedError`, it waits for an API token through a hidden input prompt and retries in the same kernel until the download succeeds. Tokens are used only in the current kernel. Interrupt the kernel to cancel; Run All proceeds to the next cell only after this cell completes. Local data lives in the mounted Ubuntu repository and survives container replacement; it is ignored by Git.
4. Inspect validation accuracy, the confusion matrix, and `output/submission.csv`. No competition submission is performed automatically.
5. For the remote run, attach the competition data to a Kaggle GPU notebook/session. Obtain its VS Code compatible Jupyter server URL, connect VS Code to that server, and select its Python kernel for this local notebook. Check the environment cell again before training.
6. Run the same notebook on the remote GPU. The notebook downloads missing data into the project data directory using `output_dir`. Generated CSV files always go into the project `output/` directory. During remote execution this directory is on the server; copy results locally if needed.

The baseline uses a stratified 80/20 split, seed 42, and a small CNN for three epochs. Versions are printed by the environment cell. GPU results can vary between runs and machines. Keep working notebook outputs for inspection; Git inside the Dev Container strips outputs when staging. HTML export follows completion of both execution checks.

Never commit Jupyter connection URLs or tokens. Connection and kernel selection require the active Kaggle session; a local CUDA check does not verify the remote environment.

Local `data/` and `output/` are real directories in the mounted Ubuntu repository, survive container replacement, and are ignored by Git.
