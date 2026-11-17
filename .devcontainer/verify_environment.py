"""Run inside the Kaggle container; print a reproducible environment and GPU check."""

import importlib
import json
import os
import platform
import subprocess
import sys
import tempfile
from importlib.metadata import version
from pathlib import Path


def main():
    packages = {
        "numpy": "numpy",
        "pandas": "pandas",
        "scipy": "scipy",
        "sklearn": "scikit-learn",
        "matplotlib": "matplotlib",
        "IPython": "ipython",
        "ipykernel": "ipykernel",
        "nbconvert": "nbconvert",
        "kagglehub": "kagglehub",
        "torch": "torch",
    }
    report = {
        "python": sys.version,
        "executable": sys.executable,
        "platform": platform.platform(),
        "packages": {},
    }
    workspace = Path(__file__).resolve().parents[1]
    if os.getuid() == 0 or os.getuid() != workspace.stat().st_uid:
        raise RuntimeError("Run as the non-root Dev Container user matching the Ubuntu workspace owner.")
    with tempfile.TemporaryFile(dir=workspace) as probe_file:
        probe_file.write(b"workspace write check")
        probe_file.flush()
        report["workspace"] = {
            "path": str(workspace),
            "uid": os.getuid(),
            "gid": os.getgid(),
            "created_file_uid": os.fstat(probe_file.fileno()).st_uid,
        }
    for module, distribution in packages.items():
        importlib.import_module(module)
        report["packages"][distribution] = version(distribution)

    import torch

    if not torch.cuda.is_available():
        raise RuntimeError("PyTorch cannot access CUDA. Check --gpus=all and the selected kernel.")
    device = torch.cuda.current_device()
    values = torch.arange(16, dtype=torch.float32, device="cuda")
    actual = (values @ values).item()
    if actual != 1240.0:
        raise RuntimeError(f"Unexpected CUDA computation result: {actual}")
    torch.cuda.synchronize()
    report["gpu"] = {
        "name": torch.cuda.get_device_name(device),
        "capability": list(torch.cuda.get_device_capability(device)),
        "torch_cuda": torch.version.cuda,
        "compiled_architectures": torch.cuda.get_arch_list(),
        "dot_product": actual,
    }
    report["nvidia_smi"] = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"],
        text=True,
    ).strip()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
