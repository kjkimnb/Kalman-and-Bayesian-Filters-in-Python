# AGENTS.md

## Cursor Cloud specific instructions

### What this repo is

Interactive Jupyter textbook **Kalman and Bayesian Filters in Python** — not a multi-service web app. Local development means installing Python deps and running a **Jupyter Notebook** server.

### Services

| Service | Required | How to start |
|---------|----------|--------------|
| Jupyter Notebook | Yes | `jupyter notebook --no-browser --ip=0.0.0.0 --port=8888` from repo root |
| Web browser | Yes | Open the URL printed by Jupyter (typically `http://127.0.0.1:8888/tree`) |

No databases, Redis, or Docker Compose are required.

### PATH

`pip install --user` puts `jupyter` and `jupyter-notebook` under `~/.local/bin`. Add to PATH before running Jupyter:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

### Install dependencies

See `README.md` and `requirements.txt`. Typical install:

```bash
pip3 install -r requirements.txt ipywidgets nbconvert
```

Conda alternative: `conda env update -f environment.yml` then `conda activate kf_bf`.

### Lint / test

There is no project-wide linter or CI. Optional checks:

- **Installation smoke test:** `python3 -c "import book_format"` (runs version checks in `book_format.py`)
- **Headless notebook run:** `jupyter nbconvert --execute 02-Discrete-Bayes.ipynb` (validates chapter execution)
- **FilterPy demo:** run a small Kalman filter script with `filterpy` (see README)

`experiments/test_stats.py` expects a local `stats` module that is not in this repo; do not treat it as a standard test target.

### Gotchas

- **ipywidgets** is used in early chapters but is not listed in `requirements.txt`; install it for interactive sliders.
- **nbconvert** is needed for `jupyter nbconvert --execute` but is not in `requirements.txt`.
- `book_format.py` uses deprecated `distutils.version.LooseVersion`; it still works on Python 3.12 but may warn.
- PDF build under `pdf/` requires LaTeX and is optional maintainer tooling, not needed for notebook development.
