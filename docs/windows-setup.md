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

- Add ignore rules and install an output-stripping Git filter in Windows Git, including a fresh-clone setup command and an index-content check.
- Export executed notebooks to HTML inside the container and verify tables, plots, logs, and required resources.
- Choose competition report paths and configure GitHub Pages deployment.
- Verify the remote Kaggle connection when requested and record its environment independently.

## Official references

- [Kaggle Python images](https://github.com/Kaggle/docker-python)
- [Docker Desktop Windows installation](https://docs.docker.com/desktop/setup/install/windows-install/)
- [Docker Desktop GPU support](https://docs.docker.com/desktop/features/gpu/)
- [VS Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
