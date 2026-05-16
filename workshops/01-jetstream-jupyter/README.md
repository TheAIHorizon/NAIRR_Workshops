# Workshop 1 — Leveraging NAIRR for Research

**Date:** 2026-03-21

Introductory workshop on the National AI Research Resource (NAIRR) and Jetstream2, with hands-on exercises comparing local vs. cloud compute performance.

> **Attribution:** Materials in this folder are based on [MattyTheBoi/NAIRR_Intro](https://github.com/MattyTheBoi/NAIRR_Intro) by Matthew Philip Horvath Jr. (Oakland University & WPI, NAIRR Workshop Series 2026), used with permission. See [`NOTICE.md`](NOTICE.md) for full attribution.

## Slides

| File | Topic |
|------|-------|
| [`slides/01_Lecture.pdf`](slides/01_Lecture.pdf) | What is NAIRR, Jetstream2, and why it matters |
| [`slides/02_Setup.pdf`](slides/02_Setup.pdf) | Connecting to Jetstream2, Jupyter crashcourse |
| [`slides/03_Exercises.pdf`](slides/03_Exercises.pdf) | Exercise overviews and timing framework |
| [`slides/Lecture_01_Slides.pdf`](slides/Lecture_01_Slides.pdf) | Combined lecture deck |

## Notebooks

| # | Notebook | Topic |
|---|----------|-------|
| 00 | [`notebooks/00_Jupyter_Crashcourse.ipynb`](notebooks/00_Jupyter_Crashcourse.ipynb) | Jupyter basics, Python refresher |
| 01 | [`notebooks/01_NAIRR_Models_and_HuggingFace.ipynb`](notebooks/01_NAIRR_Models_and_HuggingFace.ipynb) | NASA sentence transformer, semantic search |
| 02 | [`notebooks/02_Bulk_Data_Processing.ipynb`](notebooks/02_Bulk_Data_Processing.ipynb) | 500K-row dataset, sklearn, grid search |
| 03 | [`notebooks/03_NAIRR_Open_Datasets.ipynb`](notebooks/03_NAIRR_Open_Datasets.ipynb) | AG News, TF-IDF, text classification |

## Local Setup

```bash
git clone https://github.com/TheAIHorizon/NAIRR_Workshops.git
cd NAIRR_Workshops/workshops/01-jetstream-jupyter
python -m venv nairr-workshop
```

Activate:

- **Windows (PowerShell):** `.\nairr-workshop\Scripts\Activate.ps1`
- **macOS/Linux:** `source nairr-workshop/bin/activate`

```bash
pip install -r requirements.txt
```

Open the notebooks in VS Code (or JupyterLab), select the `nairr-workshop` kernel, and run.

## On Jetstream2 / NAIRR JupyterHub

- Jetstream2 portal: https://jetstream2.exosphere.app/exosphere/
- NAIRR JupyterHub: https://hub.nairr250048.projects.jetstream-cloud.org/hub/spawn

See `slides/02_Setup.pdf` for step-by-step access instructions.

## Resources Used in the Workshop

The notebooks pull from:

- HuggingFace Hub — NASA sentence transformer model
- AG News dataset (text classification)
- Scikit-learn, PyTorch, sentence-transformers (see `requirements.txt`)

## Folder Contents

- `slides/` — PDF presentation decks
- `notebooks/` — Jupyter notebooks for hands-on exercises
- `exercises/` — additional practice problems (TBD)
- `handouts/` — quick-reference materials and one-pagers (TBD)
- `requirements.txt` — Python dependencies
- `NOTICE.md` — attribution to original source
