#!/usr/bin/env bash
# Only repository-local notebook driver settings; never alter authentication.
set -euo pipefail
repository=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repository"
sh .devcontainer/git-tools.sh nbstripout --version >/dev/null
sh .devcontainer/git-tools.sh git-nbdiffdriver --help >/dev/null
sh .devcontainer/git-tools.sh git-nbmergedriver --help >/dev/null
git config --local filter.nbstripout.clean 'sh .devcontainer/git-tools.sh nbstripout'
git config --local filter.nbstripout.smudge cat
git config --local filter.nbstripout.required true
git config --local diff.jupyternotebook.command 'sh .devcontainer/git-tools.sh git-nbdiffdriver diff'
git config --local merge.jupyternotebook.driver 'sh .devcontainer/git-tools.sh git-nbmergedriver merge %O %A %B %L %P'
git config --local merge.jupyternotebook.name 'Jupyter notebook merge driver'
git config --local difftool.nbdime.cmd 'sh .devcontainer/git-tools.sh git-nbdifftool diff "$LOCAL" "$REMOTE" "$BASE"'
git config --local mergetool.nbdime.cmd 'sh .devcontainer/git-tools.sh git-nbmergetool merge "$BASE" "$LOCAL" "$REMOTE" "$MERGED"'
printf '%s\n' 'Repository notebook Git filter and diff/merge drivers configured.'
