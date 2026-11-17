#!/usr/bin/env bash
# Run on the Ubuntu host; diagnostics remain outside version control.
set -euo pipefail

repository=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repository"
up_args=()
if [ "${1:-}" = --rebuild ] && [ "$#" = 1 ]; then
    printf '%s\n' 'Recreating the Dev Container; save notebooks first. Current kernel state will be lost.'
    up_args+=(--remove-existing-container)
elif [ "$#" != 0 ]; then
    printf '%s\n' 'Usage: bash .devcontainer/validate.sh [--rebuild]' >&2
    exit 2
fi
export KAGGLE_HOST_UID=$(id -u)
export KAGGLE_HOST_GID=$(id -g)
log_directory=$(git rev-parse --absolute-git-dir)/kaggle-devcontainer
mkdir -p "$log_directory"
exec 9>"$log_directory/validate.lock"
flock -n 9 || { printf '%s\n' 'Another validation is already running.' >&2; exit 1; }
trap 'printf "%s\n" "Failed; see logs in $log_directory" > "$log_directory/status.txt"' ERR

# Prefer an explicit CLI, otherwise use the installed VS Code extension's CLI.
if command -v devcontainer >/dev/null 2>&1; then
    cli=(devcontainer)
else
    extension=$(code --locate-extension ms-vscode-remote.remote-containers)
    cli_path="$extension/dist/spec-node/devContainersSpecCLI.js"
    test -f "$cli_path" || { printf '%s\n' 'Install the VS Code Dev Containers extension.' >&2; exit 1; }
    cli=(node "$cli_path")
fi

image=$(python3 -c 'import json; print(json.load(open(".devcontainer/devcontainer.json"))["build"]["args"]["KAGGLE_IMAGE"])')
printf '%s\n' 'Pulling the configured latest image; see pull.log.' > "$log_directory/status.txt"
docker pull "$image" > "$log_directory/pull.log" 2>&1
docker image inspect "$image" --format '{{json .RepoDigests}}' > "$log_directory/image-digests.json"

printf '%s\n' 'Starting Dev Container; see up.log.' > "$log_directory/status.txt"
"${cli[@]}" up --workspace-folder "$repository" --skip-post-attach "${up_args[@]}" > "$log_directory/up.json" 2> "$log_directory/up.log"
container_id=$(python3 -c 'import json,sys; r=json.load(open(sys.argv[1])); assert r["outcome"] == "success"; print(r["containerId"])' "$log_directory/up.json")
# `up` can reuse an existing container. Verify it actually uses the pulled base.
python3 - "$image" "$container_id" <<'PY'
import json
import subprocess
import sys

def inspect(kind, reference):
    return json.loads(subprocess.check_output(["docker", kind, "inspect", reference]))[0]

base = inspect("image", sys.argv[1])["RootFS"]["Layers"]
running_image = inspect("container", sys.argv[2])["Image"]
actual = inspect("image", running_image)["RootFS"]["Layers"]
if actual[:len(base)] != base:
    raise SystemExit("Container uses an older base image. Save notebooks, rebuild in VS Code, and validate again.")
PY

printf '%s\n' 'Checking workspace writes, package imports, and CUDA.' > "$log_directory/status.txt"
"${cli[@]}" exec --workspace-folder "$repository" python .devcontainer/verify_environment.py \
    > "$log_directory/environment.json" 2> "$log_directory/environment.log"
docker inspect "$container_id" --format '{{json .HostConfig}}' > "$log_directory/host-config.json"
"${cli[@]}" exec --workspace-folder "$repository" /usr/bin/python3 .devcontainer/verify_git_workflow.py \
    > "$log_directory/git-container.json" 2> "$log_directory/git-container.log"
printf '%s\n' 'Passed: container startup, workspace writes, scientific imports, CUDA, and notebook Git drivers.' |
    tee "$log_directory/status.txt"
