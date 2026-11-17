# Ubuntu GPU development setup

## Host requirements

Develop on Ubuntu with an NVIDIA driver, Docker Engine, NVIDIA Container Toolkit, VS Code with the Dev Containers extension, host Python 3 and Node.js for the validation helper, and Git for the initial clone and host authentication setup. Git development tools are installed only in the container.

Docker runs directly on Ubuntu. Use the current stable Docker Engine from Docker's official Ubuntu repository; keep host software versions out of shared documentation. The Kaggle container image follows the `latest` tag independently of the Docker Engine version.

Check the host from an Ubuntu terminal:

```bash
nvidia-smi
docker version
docker context show
docker info --format '{{range $name, $runtime := .Runtimes}}{{$name}} {{end}}'
code --list-extensions
```

The Docker client and Linux server must both respond. Use a local Docker context so the workspace bind mount refers to this Ubuntu checkout. The host user needs access to Docker without `sudo`; after adding a user to the `docker` group, log out and back in before validation.

## NVIDIA Container Toolkit

If `nvidia-ctk` is missing or Docker has no NVIDIA runtime, run this repository's helper from the Ubuntu host:

```bash
bash .devcontainer/setup-gpu.sh
```

The helper follows [NVIDIA's installation guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html): it registers the production apt repository and key, installs the current toolkit packages, and configures the Docker runtime. It uses `sudo` and leaves the NVIDIA driver and Docker Engine installation in place.

Load the runtime when existing Docker workloads can be interrupted:

```bash
sudo systemctl restart docker
docker info --format '{{range $name, $runtime := .Runtimes}}{{$name}} {{end}}'
```

The runtime list should now include `nvidia`. The helper does not restart Docker automatically because restarting the daemon can interrupt other containers.

## Management layer and container Git

Use VS Code Source Control and the integrated terminal in the Dev Container for staging, commits, pulls, and pushes. Notebook editing, execution, and Git operations share one VS Code window.

The Dockerfile installs `nbstripout` and `nbdime` at explicit versions into `/opt/kaggle-git-tools`, using the `uv` supplied by the official image. It also installs `wrapt` there for the base interpreter's Kaggle startup hook. This environment excludes system site packages and is not added to `PATH`, so notebook execution continues to use `/usr/bin/python3` and the supplied scientific packages. The management layer does not replace the notebook interpreter or manage scientific dependencies. Update Git tool versions in the Dockerfile and rebuild through Dev Containers.

The Dockerfile also installs a pinned, checksum-verified standalone Git LFS binary in `/opt/kaggle-git-tools/bin`, exposed through `/usr/local/bin/git-lfs`, without changing scientific Python. HTML reports use LFS; manifests remain regular Git files.

On every container start, `postStartCommand` runs `.devcontainer/configure-git.sh`. It installs repository-local LFS filters and the pre-push hook. It registers the clean filter, notebook diff/merge drivers, and optional web tools using the repository-relative `.devcontainer/git-tools.sh` dispatcher. The same setup applies after a fresh clone, container recreation, or restart. It leaves authentication settings in the shared `.git/config` untouched. Notebook Git operations require the container; missing tools make the required clean filter fail rather than stage outputs.

To reapply or validate the setup manually, run inside the container:

```bash
bash .devcontainer/configure-git.sh
python .devcontainer/verify_git_workflow.py
```

The check stages an executed fixture with a temporary index, verifies empty outputs and null execution counts in the indexed version, and confirms the working outputs and actual staging state are preserved. It exercises notebook diff and semantic merge, filenames with spaces, calls from a subdirectory, and registration in a fresh repository with no prior Git settings.

Do not use `keep_output` or `init_cell` metadata/tags. Before committing, inspect the actual index:

```bash
git show :competitions/competition-slug/notebook.ipynb
```

Every committed code cell must have `outputs: []` and `execution_count: null`. Working notebook outputs remain available for inspection and HTML export.

For optional browser-based review or conflict resolution inside the container:

```bash
sh .devcontainer/git-tools.sh nbdiff-web HEAD -- competitions/competition-slug/notebook.ipynb
git mergetool --tool nbdime -- '*.ipynb'
```

### Host authentication forwarding

Sign into GitHub on the Ubuntu host through its existing credential helper, or load the SSH key into the host SSH agent. Attach through the VS Code Dev Containers extension; a standalone Docker/CLI session does not set up the live VS Code credential proxy. The extension forwards HTTPS credential requests or the SSH agent. Keep `dev.containers.copyGitConfig` enabled and `dev.containers.gitCredentialHelperConfigLocation` set to its default `global` location.

The `postAttachCommand` runs `.devcontainer/configure-auth.py`. It routes copied URL-specific helpers, such as a host-only GitHub CLI helper, through VS Code's live credential proxy. It changes only the container user's global Git settings; host settings and shared repository authentication settings stay intact. No tokens, `.git-credentials`, SSH keys, or personal authentication files are added to the Docker build context or stored in the image/repository by this setup.

For this repository's HTTPS GitHub remote, verify authentication in the attached VS Code terminal:

```bash
python .devcontainer/verify_git_auth.py
```

The check obtains a credential in memory and makes an authenticated GitHub `/user` request, printing only a success flag. A public `git ls-remote` response alone is not evidence of authentication. SSH remotes instead require checking the forwarded agent and remote access.

## Latest Kaggle GPU image

Use the official image without a version or digest pin:

```bash
docker pull gcr.io/kaggle-gpu-images/python:latest
```

The image is large. Allow space for both downloaded layers and extraction. `latest` can change; record the resolved digest locally and rerun validation after every update:

```bash
mkdir -p .git/kaggle-devcontainer
docker image inspect gcr.io/kaggle-gpu-images/python:latest \
    --format '{{json .RepoDigests}}' > .git/kaggle-devcontainer/image-digests.json
```

The [Dockerfile](../.devcontainer/Dockerfile) adds a non-root development user and an isolated Git tool environment. The [Dev Container configuration](../.devcontainer/devcontainer.json) sets that user's UID/GID through build arguments to match the Ubuntu host, preserving ownership of files created in the bind-mounted checkout. It does not install or upgrade scientific packages.

## Start and verify the Dev Container

Before launching VS Code, export the host IDs from an Ubuntu terminal. The build arguments default to `1000:1000`; these variables also support hosts with different IDs. The validation helper sets them automatically for CLI startup. Automatic UID rewriting by the CLI is disabled because the build already creates the correct user.

```bash
export KAGGLE_HOST_UID=$(id -u)
export KAGGLE_HOST_GID=$(id -g)
code .
```

1. Open this repository in VS Code on Ubuntu.
2. Run **Dev Containers: Reopen in Container**. After pulling a newer image, use **Dev Containers: Rebuild Container** so the container adopts it.
3. Confirm the workspace is `/workspaces/Kaggle`, Python points to `/usr/bin/python3`, and Python/Pylance/Jupyter extensions are available in the container.
4. Select the container's Python kernel before running local notebook cells.
5. In the container terminal, run:

   ```bash
   python .devcontainer/verify_environment.py
   ```

The check imports scientific and notebook packages, prints versions and the interpreter, confirms that a file created in the workspace has the same owner as the workspace, and performs a real PyTorch CUDA calculation. A GPU name alone does not verify computation.

For CLI startup and validation from the Ubuntu host:

```bash
bash .devcontainer/validate.sh
```

To pull `latest` and recreate the container through the normal Dockerfile build flow, save all notebooks and run `bash .devcontainer/validate.sh --rebuild` on the Ubuntu host. Recreation loses current kernel state.

The helper uses `devcontainer` if installed, otherwise the CLI bundled with the installed VS Code Dev Containers extension (through host `node`). It pulls the configured base image, starts the configured container, checks that its base layers match the pulled image, and runs the environment check as its development user. If an existing container uses an older base, save notebooks and rebuild it in VS Code before validating again. The helper prevents concurrent runs of itself and runs the notebook Git integration check inside the container. It skips the attachment hook during CLI-only validation; authentication forwarding is checked after opening the container in VS Code. CLI validation does not replace interactive extension and notebook kernel checks.

Diagnostics stay in `.git/kaggle-devcontainer/`:

- `status.txt`: current stage, success, or failure.
- `pull.log` and `image-digests.json`: image download and resolved digest.
- `up.json` and `up.log`: CLI startup result and diagnostics.
- `environment.json` and `environment.log`: package, workspace, and CUDA checks.
- `host-config.json`: effective Docker resource configuration.
- `git-container.json` and `git-container.log`: staging, diff/merge, and fresh-repository Git checks.

Monitor validation from another terminal:

```bash
cat .git/kaggle-devcontainer/status.txt
tail -n 10 .git/kaggle-devcontainer/pull.log
tail -n 10 .git/kaggle-devcontainer/up.log
```

## Resource limits

The configuration supplies generic CPU, memory, and shared-memory limits. Override `KAGGLE_CONTAINER_CPUS` and `KAGGLE_CONTAINER_MEMORY` in the host environment before launching VS Code as the workload requires. Memory and memory-plus-swap use the same value, disabling container swap. Limits cover container-side VS Code services and notebook kernels; GPU VRAM is separate.

Rebuild after changing limits. On cgroup v2, verify effective limits inside the recreated container:

```bash
cat /sys/fs/cgroup/cpu.max
cat /sys/fs/cgroup/memory.max
cat /sys/fs/cgroup/memory.swap.max
```

The CPU quota divided by its period gives the CPU allowance; `max` means unlimited. Memory is in bytes; the swap limit should be zero. Keep machine-specific allocations and hardware diagnostics in local logs.

## Execution and publication

Run [Digit Recognizer](../competitions/digit-recognizer/README.md) locally first, then on a remote Kaggle GPU kernel. Use [KaggleHub for input downloads and remote data resolution](data-access.md). Reuse local files when available and always read from the path returned by KaggleHub. Remote execution reads the Kaggle server filesystem, independently of the Ubuntu container mount; confirm its environment and accelerator settings. Do not commit connection URLs or tokens.

HTML export follows both execution checks. Export inside the container from a working notebook with outputs, verify tables/plots/logs and referenced resources, and keep reports outside ignored artifact directories. Reports live in `reports/<competition>/`; use the [report publishing workflow](report-publishing.md) to export, preview, and deploy.

## Validation status

Ubuntu container startup, matching non-root workspace ownership, `/usr/bin/python3`, scientific imports, effective resource limits, and real PyTorch CUDA computation have passed validation. Repeat validation after each base image update; resolved digests and detailed machine diagnostics remain untracked in `.git/kaggle-devcontainer/`.

Notebook Git output stripping, working-output preservation, diff/merge, and fresh-repository registration passed. Forwarded GitHub authentication passed from the attached container. Local and remote Kaggle GPU baseline runs completed; results and report links are in the [competition guide](../competitions/digit-recognizer/README.md).

Git LFS upload/download, a fresh clone, and Pages deployment have passed. The Dockerfile now declares the Git LFS installation; a full image rebuild after that addition has not yet been validated. Save working notebooks before a rebuild. Kernel selection still needs to be confirmed interactively for each execution session.

## Official references

- [Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
- [NVIDIA Container Toolkit installation](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
- [Official Kaggle Python images](https://github.com/Kaggle/docker-python)
- [VS Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
- [Linux bind mounts and non-root users](https://code.visualstudio.com/remote/advancedcontainers/add-nonroot-user)
- [VS Code Git credential forwarding](https://code.visualstudio.com/remote/advancedcontainers/sharing-git-credentials)
- [nbstripout Git filter](https://github.com/kynan/nbstripout#using-as-a-git-filter)
- [nbdime Git integration](https://nbdime.readthedocs.io/en/latest/vcs.html)
- [uv project environments](https://docs.astral.sh/uv/concepts/projects/environments/)
