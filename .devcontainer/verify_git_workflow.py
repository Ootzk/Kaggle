"""Exercise configured Git drivers without changing the user's real index."""

import copy
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile


def main():
    root = Path(__file__).resolve().parents[1]
    original_index = subprocess.check_output(["git", "ls-files", "--stage", "-z"], cwd=root)
    fixture_parent = root / "tmp"
    fixture_parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="git-drivers-", dir=fixture_parent) as directory:
        folder = Path(directory)
        env = dict(os.environ, GIT_INDEX_FILE=str(folder / "index"), GIT_TERMINAL_PROMPT="0")

        def git(*args, cwd=root):
            return subprocess.check_output(["git", *args], cwd=cwd, env=env, text=True)

        notebook = {
            "nbformat": 4,
            "nbformat_minor": 5,
            "metadata": {},
            "cells": [
                {"cell_type": "code", "id": f"cell-{i}", "metadata": {},
                 "source": [f"{name} = 1\n"], "execution_count": i + 1,
                 "outputs": [{"output_type": "stream", "name": "stdout", "text": ["working output\n"]}]}
                for i, name in enumerate(("x", "y"))
            ],
        }
        fixture = folder / "notebook with spaces.ipynb"
        fixture.write_text(json.dumps(notebook))
        original = fixture.read_bytes()
        relative = fixture.relative_to(root).as_posix()
        git("read-tree", "HEAD")
        # Run from a subdirectory, like Git operations launched outside the root.
        git("add", "--force", "--", str(fixture), cwd=root / "competitions" / "digit-recognizer")
        staged = json.loads(git("show", ":" + relative))
        assert [c["source"] for c in staged["cells"]] == [c["source"] for c in notebook["cells"]]
        assert all(c["outputs"] == [] and c["execution_count"] is None for c in staged["cells"])
        assert fixture.read_bytes() == original, "Staging changed the working notebook"
        cached_diff = git("diff", "--cached", "--", relative)
        assert "nbdiff" in cached_diff
        modified = copy.deepcopy(notebook)
        modified["cells"][0]["source"] = ["x = 2\n"]
        fixture.write_text(json.dumps(modified))
        diff = git("diff", "--", str(fixture), cwd=root / "competitions" / "digit-recognizer")
        assert "nbdiff" in diff and "x = 2" in diff

        # Execute the configured merge command on independent cell edits.
        base = copy.deepcopy(staged)
        local, remote = copy.deepcopy(base), copy.deepcopy(base)
        local["cells"][0]["source"] = ["x = 2\n"]
        remote["cells"][1]["source"] = ["y = 3\n"]
        merge_files = [folder / name for name in ("base.ipynb", "local.ipynb", "remote.ipynb")]
        for path, content in zip(merge_files, (base, local, remote)):
            path.write_text(json.dumps(content))
        substitutions = dict(zip(("%O", "%A", "%B"), map(str, merge_files)))
        substitutions.update({"%L": "7", "%P": relative})
        driver = shlex.split(git("config", "--get", "merge.jupyternotebook.driver").strip())
        subprocess.run([substitutions.get(arg, arg) for arg in driver], cwd=root, env=env, check=True)
        merged = json.loads(merge_files[1].read_text())
        assert merged["cells"][0]["source"] == ["x = 2\n"]
        assert merged["cells"][1]["source"] == ["y = 3\n"]

        # A fresh checkout has no repository-local Git driver configuration.
        fresh = folder / "fresh checkout"
        (fresh / ".devcontainer").mkdir(parents=True)
        for name in ("git-tools.sh", "configure-git.sh"):
            shutil.copy2(root / ".devcontainer" / name, fresh / ".devcontainer" / name)
        shutil.copy2(root / ".gitattributes", fresh / ".gitattributes")
        fresh_env = dict(os.environ)
        fresh_env.pop("GIT_INDEX_FILE", None)
        subprocess.run(["git", "init", "-q", str(fresh)], check=True, env=fresh_env)
        configure = ["bash", str(fresh / ".devcontainer/configure-git.sh")]
        subprocess.run(configure, check=True, capture_output=True, cwd=fresh, env=fresh_env)
        first_config = subprocess.check_output(["git", "config", "--local", "--list"], cwd=fresh, env=fresh_env)
        subprocess.run(configure, check=True, capture_output=True, cwd=fresh, env=fresh_env)
        assert subprocess.check_output(["git", "config", "--local", "--list"], cwd=fresh, env=fresh_env) == first_config
        fresh_notebook = fresh / "fresh.ipynb"
        fresh_notebook.write_bytes(original)
        subprocess.run(["git", "add", "fresh.ipynb"], cwd=fresh, env=fresh_env, check=True)
        fresh_staged = json.loads(subprocess.check_output(["git", "show", ":fresh.ipynb"], cwd=fresh, env=fresh_env))
        assert all(c["outputs"] == [] and c["execution_count"] is None for c in fresh_staged["cells"])
        assert fresh_notebook.read_bytes() == original

    final_index = subprocess.check_output(["git", "ls-files", "--stage", "-z"], cwd=root)
    assert final_index == original_index, "Real staging state changed"
    print(json.dumps({
        "staging_strips_outputs": True,
        "working_outputs_preserved": True,
        "nested_directory_and_spaces": True,
        "notebook_diff": True,
        "notebook_merge": True,
        "real_staging_preserved": True,
        "fresh_repository_bootstrap": True,
        "idempotent_configuration": True,
        "index_entries_sha256": hashlib.sha256(final_index).hexdigest(),
    }, indent=2))


if __name__ == "__main__":
    main()
