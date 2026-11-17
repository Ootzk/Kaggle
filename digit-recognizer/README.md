# Digit Recognizer GPU baseline

Open `baseline.ipynb` in the Kaggle GPU Dev Container. Use the container Python kernel for the local run.

1. Accept any required terms on the [competition page](https://www.kaggle.com/competitions/digit-recognizer/data).
2. Run the environment cell first and check the host, interpreter, and GPU.
3. Copy the repository-root `.env.example` to `.env` and set `KAGGLE_API_TOKEN` there. The file is ignored by Git; never put a token in the notebook or a tracked file. Run the data preparation cell. Existing `data/train.csv` and `data/test.csv` are used without authentication. Otherwise the cell loads the root `.env` using `load_dotenv(override=False)` from the image-supplied `python-dotenv` and reads the token through `os.environ` and downloads through `kagglehub.competition_download`. An existing `KAGGLE_API_TOKEN` environment variable takes precedence. Tokens are passed to KaggleHub in memory without printing them. After changing `.env`, restart the kernel and rerun the notebook so previously loaded environment values do not persist. Authentication failure stops execution; check the token and competition terms before retrying.
4. Inspect validation accuracy, the confusion matrix, and `output/submission.csv`. No competition submission is performed automatically.
5. For the remote run, attach the competition data to a Kaggle GPU notebook/session. Obtain its VS Code compatible Jupyter server URL, connect VS Code to that server, and select its Python kernel for this local notebook. Check the environment cell again before training.
6. Run the same notebook on the remote GPU. The notebook downloads missing data into the project data directory using `output_dir`. Generated CSV files always go into the project `output/` directory. During remote execution this directory is on the server; copy results locally if needed.

The baseline uses a stratified 80/20 split, seed 42, and a small CNN for three epochs. Versions are printed by the environment cell. GPU results can vary between runs and machines. Keep working notebook outputs for inspection; Git inside the Dev Container strips outputs when staging. HTML export follows completion of both execution checks.

Never commit Jupyter connection URLs or tokens. Connection and kernel selection require the active Kaggle session; a local CUDA check does not verify the remote environment.

Local `data/` and `output/` are real directories in the mounted Ubuntu repository, survive container replacement, and are ignored by Git.
