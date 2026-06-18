# Workshop 1 — Leveraging NAIRR for Research

**Date:** 2026-03-21

Introductory workshop on the National AI Research Resource (NAIRR) and Jetstream2, with hands-on exercises comparing local vs. cloud compute performance.

> **Attribution:** Materials in this folder are based on [MattyTheBoi/NAIRR_Intro](https://github.com/MattyTheBoi/NAIRR_Intro) by Matthew Philip Horvath Jr. (Oakland University & WPI, NAIRR Workshop Series 2026), used with permission. See [`NOTICE.md`](NOTICE.md) for full attribution.

> **Part of AI Horizon:** These workshop and outreach materials are developed as outputs of *AI Horizon — Forecasting Cybersecurity Workforce Evolution and Adaptive Skill Development* (NSF #2528858, CSUSB Center for Cyber and AI).

## Start Here

**New to NAIRR, Jetstream2, or Jupyter?** Read [`CONCEPTS.md`](CONCEPTS.md) first. It explains how all the pieces (ACCESS, NAIRR, Jetstream2, JupyterHub, GitHub) fit together — the relationships and credential chain you need before any code makes sense.

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
| 04 | [`notebooks/04_Local_LLM_Frameworks.ipynb`](notebooks/04_Local_LLM_Frameworks.ipynb) | Same model (Qwen3) benchmarked across Ollama, llama.cpp & vLLM — speed, throughput, quality; auto-adapts to CPU or GPU instances |

## Handouts

Open these HTML files in any web browser (double-click, or right-click → Open).
**New here? Open [`handouts/010-start-here.html`](handouts/010-start-here.html) first** — it routes you to the right track.

| File | Audience | Purpose |
|------|----------|---------|
| [`handouts/010-start-here.html`](handouts/010-start-here.html) | Everyone | **Start here** — roadmap: run the lab (Track A) vs. build your own (Track B) |
| [`handouts/020-roadmap.html`](handouts/020-roadmap.html) | Everyone | Visual **resource map** — every guide and how they connect (clickable diagram) |
| [`handouts/030-get-your-access-id.html`](handouts/030-get-your-access-id.html) | Students | **Do before class** — create your ACCESS ID (use your **school email, not Gmail**) and send the username to your instructor |
| [`handouts/040-what-this-demo-does.html`](handouts/040-what-this-demo-does.html) | Everyone | Plain-language overview — what the Local LLM demo (Notebook 04) does and why |
| [`handouts/050-jetstream2-local-llm-setup.html`](handouts/050-jetstream2-local-llm-setup.html) | Students | Step-by-step — launch a Jetstream2 instance and run Notebook 04 |
| [`handouts/055-request-startup-allocation.html`](handouts/055-request-startup-allocation.html) | Instructors | Apply for a NAIRR Start-Up allocation — what the form needs + ready-to-adapt title/abstract/justification text (plain-text copy: [`055a-startup-request-template.md`](handouts/055a-startup-request-template.md)) |
| [`handouts/060-instructor-allocation-setup.html`](handouts/060-instructor-allocation-setup.html) | Instructors | **Do this first** — get your allocation, exchange SUs, and add students' ACCESS IDs (pre-class admin) |
| [`handouts/070-instructor-preflight-checklist.html`](handouts/070-instructor-preflight-checklist.html) | Instructors | Run before each workshop — interactive go/no-go checklist (allocation, students added, end-to-end test) |
| [`handouts/080-instructor-notes.html`](handouts/080-instructor-notes.html) | Instructors | Talking points, teaching moments, and the capacity/disk rationale behind the lab setup |
| [`handouts/090-setup-ai-coding-assistant.html`](handouts/090-setup-ai-coding-assistant.html) | Instructors | Set up VS Code + Claude Code to build your own **Jetstream2-ready** notebooks by describing what you want to teach |
| [`handouts/095-notebook-ideas.html`](handouts/095-notebook-ideas.html) | Instructors | Menu of **AI × cybersecurity notebook ideas** to ask the AI to build (CPU & GPU), each with a copy-paste prompt |

## Local Setup

```bash
git clone https://github.com/TheAIHorizon/NAIRR_Workshops.git
cd NAIRR_Workshops/workshops/010-jetstream-jupyter
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

- [`CONCEPTS.md`](CONCEPTS.md) — **read first** — architecture and how the pieces fit together
- `slides/` — PDF presentation decks
- `notebooks/` — Jupyter notebooks for hands-on exercises
- `exercises/` — additional practice problems (TBD)
- `handouts/` — quick-reference materials and one-pagers (TBD)
- `requirements.txt` — Python dependencies
- `NOTICE.md` — attribution to original source
