#!/bin/sh
# Git invokes drivers from the worktree root; resolve tools without changing cwd.
set -eu
tool=${1:?Specify a notebook Git tool}
shift
case "$tool" in
    nbstripout|nbdime|git-nbdiffdriver|git-nbmergedriver|nbdiff-web|git-nbmergetool|git-nbdifftool) ;;
    *) printf 'Unsupported notebook Git tool: %s\n' "$tool" >&2; exit 2 ;;
esac
if [ ! -f /.dockerenv ]; then
    printf '%s\n' 'Run notebook Git operations inside the Kaggle Dev Container.' >&2
    exit 127
fi
tools=/opt/kaggle-git-tools
if [ ! -x "$tools/bin/$tool" ]; then
    printf 'Notebook Git tool missing: %s. Rebuild the Dev Container.\n' "$tools/bin/$tool" >&2
    exit 127
fi
unset PYTHONPATH PYTHONHOME
export PYTHONNOUSERSITE=1
exec "$tools/bin/$tool" "$@"
