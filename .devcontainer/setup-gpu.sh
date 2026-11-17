#!/usr/bin/env bash
# Run on the Ubuntu host. Docker restart is a separate, deliberate step.
set -euo pipefail

sudo -v
sudo apt-get update
sudo apt-get install -y --no-install-recommends ca-certificates curl gnupg

setup_tmp=$(mktemp -d)
trap 'rm -rf "$setup_tmp"' EXIT
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey |
    gpg --dearmor > "$setup_tmp/keyring.gpg"
curl -fsSL https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list |
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' > "$setup_tmp/toolkit.list"
sudo install -m 644 "$setup_tmp/keyring.gpg" /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
sudo install -m 644 "$setup_tmp/toolkit.list" /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker

printf '%s\n' 'Toolkit installed and configured. To load the runtime, run: sudo systemctl restart docker' \
    'Restarting Docker can interrupt existing containers. Then run: bash .devcontainer/validate.sh'
