"""Check forwarded GitHub authentication without printing or storing a token."""

import json
import os
import subprocess
import urllib.request


def main():
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")
    result = subprocess.run(["git", "credential", "fill"],
                            input="protocol=https\nhost=github.com\n\n",
                            capture_output=True, text=True, env=env, timeout=30)
    fields = dict(line.split("=", 1) for line in result.stdout.splitlines() if "=" in line)
    if result.returncode or not fields.get("password"):
        raise SystemExit("Forwarded GitHub credential unavailable; check VS Code attachment and host sign-in.")
    request = urllib.request.Request("https://api.github.com/user", headers={
        "Authorization": "Bearer " + fields["password"],
        "Accept": "application/vnd.github+json",
        "User-Agent": "Kaggle-DevContainer-auth-check",
    })
    with urllib.request.urlopen(request, timeout=30) as response:
        account = json.load(response)
    assert account.get("id") and account.get("login")
    print(json.dumps({"forwarded_github_authentication": True}))


if __name__ == "__main__":
    main()
