"""Route copied URL-specific helpers through VS Code's live host proxy."""

from pathlib import Path
import subprocess


def main():
    if not Path("/.dockerenv").exists():
        raise SystemExit("Run this inside the VS Code Dev Container.")
    result = subprocess.run(["git", "config", "--get-all", "credential.helper"],
                            capture_output=True, text=True, check=False)
    proxies = [helper for helper in result.stdout.splitlines()
               if "vscode-remote-containers" in helper and "git-credential-helper" in helper]
    if not proxies:
        raise SystemExit("VS Code credential forwarding is unavailable. Attach with Dev Containers and enable its Git credential helper.")
    # A copied host helper such as /usr/bin/gh may not exist in the container.
    # Keep the shared repository config and host global config untouched.
    keys = subprocess.run(["git", "config", "--global", "--name-only", "--get-regexp", r"^credential\..*\.helper$"],
                          capture_output=True, text=True, check=False)
    for key in set(keys.stdout.splitlines()):
        subprocess.run(["git", "config", "--global", "--replace-all", key, ""], check=True)
        subprocess.run(["git", "config", "--global", "--add", key, proxies[-1]], check=True)
    print("VS Code host credential forwarding configured; no credentials stored by this script.")


if __name__ == "__main__":
    main()
