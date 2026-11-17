# Windows GPU development setup

## Host and Docker

Use Windows Git for commit, push, and pull in this checkout. Run the following in a host PowerShell terminal:

```powershell
nvidia-smi
wsl --version
wsl --list --verbose
docker context ls
docker version
```

The Docker client and Linux server must both respond. Select the WSL2 backend in Docker Desktop settings and use a Docker context that connects to its Linux engine.

Docker Desktop can also be updated from PowerShell:

```powershell
winget upgrade --id Docker.DockerDesktop --exact --source winget
```

Updating an all-users installation in `C:\Program Files` requires the Windows administrator prompt. Current Docker Desktop requires WSL 2.1.5 or later; an old inbox WSL kernel alone does not satisfy this requirement. Update WSL if necessary with `wsl --update`, then check `wsl --version` again.

Check `%USERPROFILE%\.wslconfig` for resource limits. Allocate memory, CPUs, and swap according to the machine's capacity and the notebook workload, leaving resources for Windows. Back up the file before changing it. These limits apply to all WSL2 distributions together. Apply changes with `wsl --shutdown` and restart Docker Desktop; this also interrupts other WSL workloads and Docker containers.

Verify GPU passthrough before downloading the Kaggle image:

```powershell
docker run --rm --gpus all nvidia/cuda:12.6.3-base-ubuntu22.04 nvidia-smi
```

## Notebook Git filter

Git runs on Windows. Host development tools are declared in the `dev` dependency group in `pyproject.toml`; `uv.lock` records the resolved versions and hashes of their dependencies. `uv sync --locked` installs them into the ignored Windows `.venv`. Notebook execution and HTML export use the Python environment supplied by the Kaggle GPU image.

If `uv` is not installed, install it from a host PowerShell terminal:

```powershell
winget install --id astral-sh.uv --exact --source winget
```

Open a new terminal after installation. From the repository root, install the locked dependencies and register the Git filter:

```powershell
uv sync --locked
uv run --locked nbstripout --install --attributes .gitattributes
uv run --locked nbstripout --is-installed
```

The filter configuration in `.git/config` references the Windows `.venv` Python executable directly, so Git does not require environment activation. Registration is local and is not inherited by a fresh clone. Keep `.venv` available and re-register the filter after cloning or moving the checkout. The shared `.gitattributes` records which files use the filter.

Run these setup commands on Windows. Keep the Windows `.venv` for host Git operations; select the Kaggle image's Python interpreter inside the Dev Container. Do not synchronize the mounted Windows `.venv` from Linux.

To change host dependencies, use `uv add --dev` or `uv remove --dev` and review both `pyproject.toml` and `uv.lock`. For a deliberate dependency upgrade, use `uv lock --upgrade-package nbstripout`, adjusting its declared version constraint first when needed, then `uv sync --locked`. Commit both dependency files together.

`git add` strips notebook execution results in the Git version while preserving the working notebook and its outputs for inspection and HTML export. `nbstripout` also normalizes cell IDs and removes selected metadata according to its defaults. Do not use `keep_output` or `init_cell` metadata/tags that retain outputs; this repository requires every committed code cell to have `outputs: []` and `execution_count: null`.

After staging, inspect the indexed notebook, rather than the working file:

```powershell
git show :competition-slug/notebook.ipynb
```

Confirm that code and Markdown remain, code-cell outputs are empty, and execution counts are null. `uv run --locked nbstripout --verify notebook.ipynb` checks the working file, which intentionally retains outputs, so it is not an index check.

Host-side validation uses temporary repositories to check real staging, working-output preservation, fresh-clone registration, and failure handling. Detailed fixture results remain local rather than adding custom filter scripts to the repository.

## Notebook diff and merge

`nbdime` is a locked host development dependency. Keep `nbstripout` as the clean filter and use `nbdime` for structured notebook diffs and merges. Register it locally after each clone:

```powershell
uv run --locked nbdime config-git --enable
git config --local diff.jupyternotebook.command '".venv/Scripts/git-nbdiffdriver.exe" diff'
git config --local merge.jupyternotebook.driver '".venv/Scripts/git-nbmergedriver.exe" merge %O %A %B %L %P'
```

The explicit paths let regular Windows `git diff` and `git merge` find the project tools without activating `.venv`. `.gitattributes` selects `diff=jupyternotebook` and `merge=jupyternotebook`; these replace the simpler `nbstripout` diff view while preserving its output-stripping filter.

For a browser-based diff or interactive merge resolution, run from the repository root:

```powershell
uv run --locked nbdiff-web HEAD -- competition-slug/notebook.ipynb
uv run --locked git mergetool --tool nbdime -- '*.ipynb'
```

These commands expose the project executables through `uv run`. Review unresolved code conflicts manually and verify the resulting notebook before staging it. Browser-based tools require an interactive user session.

## Kaggle image and VS Code

The configuration pins the official GPU image `v172`:

```text
gcr.io/kaggle-gpu-images/python:v172@sha256:9a6bcfda6d03b2cd9aa347ee8c1bae62043328ed0f4afe9bda014e4f8bbf9435
```

Registry metadata identifies it as `linux/amd64` with CUDA 12.8.1. Its compressed layers total about 23.91 GiB; Docker needs additional disk space to extract and retain the image. Verify successful CUDA computation with its bundled framework on the target NVIDIA GPU before calling the image tested.

1. Open this repository in VS Code on Windows.
2. Run **Dev Containers: Reopen in Container**. The first pull is large.
3. Confirm that the workspace is `/workspaces/Kaggle` and Python points to `/usr/local/bin/python`.
4. In the container terminal, run:

   ```bash
   python .devcontainer/verify_environment.py
   ```

The script imports the scientific and notebook packages, prints their versions and the Python executable, and verifies a real CUDA dot product with PyTorch. It fails if GPU access or computation fails. Retain the JSON output when recording a tested image. No additional Python packages are installed by this configuration.

For a terminal check independent of the VS Code UI, run from the repository root on Windows:

```powershell
$image = (Get-Content .devcontainer/devcontainer.json -Raw | ConvertFrom-Json).image
docker pull $image
docker run --rm --gpus all --shm-size=2g --mount "type=bind,source=$($PWD.Path),target=/workspaces/Kaggle" --workdir /workspaces/Kaggle $image python .devcontainer/verify_environment.py
```

The repository is a bind mount, so edits persist on Windows. Python and Jupyter extensions are installed in the container by VS Code. Confirm the notebook kernel before running cells; the local container interpreter and a remote Kaggle kernel have separate filesystems and environments. Remote Kaggle connection verification remains deferred.

To start and verify the configured Dev Container using the CLI bundled with the installed VS Code extension, run this host helper from the main Windows checkout:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .devcontainer/validate.ps1
```

It waits for the image pull and container startup, then runs the Python verification script. A successful CLI startup validates the container configuration; opening the container in the VS Code UI and checking its extensions/kernel is a separate check. Logs stay under `.git/kaggle-devcontainer/`, outside version control:

- `status.txt`: current stage, success, or failure.
- `up.log` and `up.json`: Dev Containers CLI logs and result.
- `environment.json` and `environment.log`: Python package/GPU results and diagnostics.

Monitor a running validation from another PowerShell terminal with:

```powershell
Get-Content .git/kaggle-devcontainer/status.txt
Get-Content .git/kaggle-devcontainer/up.log -Tail 10
```

## Validation status

- NVIDIA GPU visibility was verified on Windows, in WSL2, and in a CUDA container.
- Dev Container JSON and the validation scripts' Python/PowerShell syntax passed host checks. The Dev Containers CLI successfully resolved the configuration and workspace bind mount.
- The image pull and host validation helper were started. Check local logs for their current status; Kaggle imports, CUDA computation, and Dev Container CLI startup remain unconfirmed in shared documentation. VS Code UI startup and kernel selection have not been tested.

Keep machine-specific hardware details, resource allocations, installed host-tool versions, and troubleshooting logs in untracked local diagnostics. Shared documentation describes the Windows + NVIDIA GPU workflow and reproducible container configuration.

## Remaining workflow work

- Export executed notebooks to HTML inside the container and verify tables, plots, logs, and required resources.
- Choose competition report paths and configure GitHub Pages deployment.
- Verify the remote Kaggle connection when requested and record its environment independently.

## Official references

- [Kaggle Python images](https://github.com/Kaggle/docker-python)
- [Docker Desktop Windows installation](https://docs.docker.com/desktop/setup/install/windows-install/)
- [Docker Desktop GPU support](https://docs.docker.com/desktop/features/gpu/)
- [VS Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
- [nbstripout Git filter](https://github.com/kynan/nbstripout#using-as-a-git-filter)
- [nbdime Git integration](https://nbdime.readthedocs.io/en/latest/vcs.html)
- [uv project dependencies](https://docs.astral.sh/uv/concepts/projects/dependencies/)
- [uv locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/)
