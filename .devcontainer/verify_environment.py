"""Run inside the Kaggle container; print a reproducible environment and GPU check."""

import importlib
import json
import platform
import subprocess
import sys
from importlib.metadata import version


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
        "torch": "torch",
    }
    report = {
        "python": sys.version,
        "executable": sys.executable,
        "platform": platform.platform(),
        "packages": {},
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
