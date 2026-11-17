ARG KAGGLE_IMAGE=gcr.io/kaggle-gpu-images/python:latest
FROM ${KAGGLE_IMAGE}

USER root
# Keep Git tools separate from the image's scientific Python environment.
# wrapt is needed by the base interpreter's Kaggle sitecustomize hook.
RUN git --version \
    && uv venv /opt/kaggle-git-tools --python /usr/bin/python3 --no-managed-python --no-python-downloads \
    && UV_SYSTEM_PYTHON=false uv pip install --python /opt/kaggle-git-tools/bin/python --no-cache \
        nbstripout==0.9.1 nbdime==4.0.4 wrapt==1.17.3


# Standalone Git LFS stays with the isolated Git tools, not scientific Python.
ARG GIT_LFS_VERSION=3.8.1
ARG GIT_LFS_SHA256=e72cf723a4a660438862282e8aecf3885fc8123e88bfcad534cf6b941a354b75
RUN curl -fsSL --retry 3 \
        "https://github.com/git-lfs/git-lfs/releases/download/v${GIT_LFS_VERSION}/git-lfs-linux-amd64-v${GIT_LFS_VERSION}.tar.gz" \
        -o /tmp/kaggle-git-lfs.tar.gz \
    && echo "${GIT_LFS_SHA256}  /tmp/kaggle-git-lfs.tar.gz" | sha256sum -c - \
    && tar -xzf /tmp/kaggle-git-lfs.tar.gz -C /tmp \
    && install -m 0755 "/tmp/git-lfs-${GIT_LFS_VERSION}/git-lfs" /opt/kaggle-git-tools/bin/git-lfs \
    && ln -sf /opt/kaggle-git-tools/bin/git-lfs /usr/local/bin/git-lfs \
    && rm -rf /tmp/kaggle-git-lfs.tar.gz "/tmp/git-lfs-${GIT_LFS_VERSION}"

ARG USER_UID=1000
ARG USER_GID=1000
# Free the base image's unused ubuntu account only if its UID conflicts.
RUN if id -u ubuntu >/dev/null 2>&1 && [ "$(id -u ubuntu)" = "$USER_UID" ]; then userdel ubuntu; fi \
    && if ! getent group "$USER_GID" >/dev/null; then groupadd --gid "$USER_GID" vscode; fi \
    && useradd --uid "$USER_UID" --gid "$USER_GID" --create-home --shell /bin/bash vscode

ENV PYTHONUSERBASE=/home/vscode/.local \
    ENV=/home/vscode/.bashrc
USER vscode
