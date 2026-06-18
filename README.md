# NAIRR Workshops

Materials for workshops teaching faculty how to use NAIRR (National AI Research Resource) compute resources.

## Focus

The initial workshop series focuses on **Jetstream2** and **Jupyter notebooks** as the entry point for researchers and educators.

- Jetstream2 portal: https://jetstream2.exosphere.app/exosphere/
- NAIRR JupyterHub: https://hub.nairr250048.projects.jetstream-cloud.org/hub/spawn

## Workshops

Workshops are numbered in tens (010, 020, 030 …) so a new one can be slotted in between (e.g. 015)
without renumbering. The order also forms a **learning path** for working with LLMs:

| # | Topic | Folder | The question it answers |
|---|-------|--------|--------------------------|
| 010 | Leveraging NAIRR + local LLM frameworks | [`workshops/010-jetstream-jupyter/`](workshops/010-jetstream-jupyter/) | How do I run a model on NAIRR, and which engine? |
| 020 | Quantization: size vs. speed vs. quality | [`workshops/020-quantization/`](workshops/020-quantization/) | How small/precise a model do I need? |
| 030 | Train vs. Tune vs. RAG | [`workshops/030-train-tune-rag/`](workshops/030-train-tune-rag/) | How do I make a model do *my* task? |
| 040 | GPU showcase: throughput + a research benchmark | [`workshops/040-gpu-showcase/`](workshops/040-gpu-showcase/) | What does a big GPU (H100) unlock for research? |

*More (agents/tools, multimodal …) will be added with the next numbers as the series grows.*

## Repository Layout

```
NAIRR_Workshops/
├── README.md
├── Notes.md                    # working notes, reference links
├── workshops/                  # per-workshop materials (numbered in tens)
│   ├── 010-jetstream-jupyter/  # run a model on NAIRR + compare engines
│   │   ├── README.md
│   │   ├── notebooks/          # Jupyter notebooks
│   │   └── handouts/           # HTML guides
│   ├── 020-quantization/       # same model at Q4/Q6/Q8/F16
│   ├── 030-train-tune-rag/     # train vs fine-tune vs RAG
│   └── 040-gpu-showcase/       # H100: throughput + a research benchmark
├── shared/                     # cross-workshop material
│   ├── setup-guides/           # Jetstream onboarding, JupyterHub access
│   ├── troubleshooting/
│   └── assets/                 # logos, common images
└── archive/                    # reference material from prior talks
```

## Attribution

Workshop 010 materials are based on [MattyTheBoi/NAIRR_Intro](https://github.com/MattyTheBoi/NAIRR_Intro) (Oakland University & WPI, NAIRR Workshop Series 2026), used with permission. See [`workshops/010-jetstream-jupyter/NOTICE.md`](workshops/010-jetstream-jupyter/NOTICE.md) for details. Workshops 020+ are developed as part of **AI Horizon** (NSF #2528858, CSUSB Center for Cyber and AI).

## References

See [`Notes.md`](Notes.md) for related projects and prior workshop links.
