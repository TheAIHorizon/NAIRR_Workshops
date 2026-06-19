#!/usr/bin/env bash
# Run a notebook headless (no browser) in the terminal.
#
# Why this wrapper: vLLM starts its engine in a separate process via "spawn",
# which re-imports the running script. A plain `python run.py` then re-executes
# everything and crashes ("An attempt has been made to start a new process...").
# Wrapping the converted script in an `if __name__ == "__main__":` guard fixes it.
#
# Usage:  bash run_headless.sh [notebook.ipynb]
set -e
# Activate the workshop venv if it exists (so `jupyter`/`python` are on PATH).
[ -f "$HOME/llmdemo/bin/activate" ] && source "$HOME/llmdemo/bin/activate"
NB="${1:-notebooks/010_H100_Research_Showcase.ipynb}"
echo ">> Converting $NB to a guarded script ..."
jupyter nbconvert --to script --stdout "$NB" > /tmp/_nb_body.py
{ echo "if __name__ == '__main__':"; sed 's/^/    /' /tmp/_nb_body.py; } > run.py
echo ">> Running (first run is slow: installs + model download) ..."
python run.py
