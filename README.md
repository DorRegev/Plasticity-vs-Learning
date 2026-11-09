# Plasticity vs. Learning: where does in-context grammar learning happen in an LLM?

Thesis project. It builds on *Computation or Weight Adaptation? Rethinking the role of plasticity in learning*
(bioRxiv 2024.03.07.583890), which shows that a **frozen** LLM (Mistral-7B) learns an artificial grammar from
examples in its prompt alone, with no weight updates. We reproduce that result, then ask **at which of the
model's 32 layers the learning becomes visible**, and how to read it out.

## Repository map

Every experiment theme has its own numbered folder with the same layout:

```
NN_theme/
├── README.md     what was tested, how to run it, key results
├── code/         notebook.ipynb (clean, open this in Colab), notebook_executed.ipynb + .html (a finished run)
└── reports/      meeting reports (PDF), named YYYY-MM-DD_meetingN_....pdf
```

| Folder | Theme | Main question |
|---|---|---|
| [`00_paper_reproduction/`](00_paper_reproduction/) | Reproducing the paper | Does a frozen Mistral-7B learn the grammars in context, as reported? |
| [`01_logit_lens/`](01_logit_lens/) | Per-layer decoding with the logit lens | At which layer does the learned grammar become readable? |
| [`02_tuned_lens/`](02_tuned_lens/) | Tuned lens vs. logit lens | Is that layer a property of the model, or of the logit lens? |
| [`03_induction_heads/`](03_induction_heads/) | Induction heads and ablation | Do induction heads carry the in-context learning? |
| [`04_noise_robustness/`](04_noise_robustness/) | Noise at each layer | Which layers are most fragile for in-context learning, compared with general ability? |
| [`05_head_specialization/`](05_head_specialization/) | Single induction heads, per transition | Does each induction head serve particular transitions of the grammar? |

## Meeting log

| Date | Meeting | Theme | Report | Main finding |
|---|---|---|---|---|
| 2026-10-13 | 1 | `01_logit_lens` (with the reproduction) | [PDF](01_logit_lens/reports/2026-10-13_meeting1_in_context_grammar_learning.pdf) | Reproduction matches the paper. The grammar appears abruptly at **layer 19**; it becomes the model's actual word output from ~layer 22. |
| 2026-10-20 | 2 | `02_tuned_lens` | [PDF](02_tuned_lens/reports/2026-10-20_meeting2_in_context_grammar_learning.pdf) | A tuned lens shows the **same abrupt onset at layer 19** (faint 5–10% precursor at layers 13–18): the onset is a property of the model, not of the logit lens. |
| 2026-11-01 | 3 | `03_induction_heads` | [PDF](03_induction_heads/reports/2026-11-01_meeting3_induction_heads.pdf) | The strongest **induction heads** sit in blocks 18 and 12, which write lens layers 19 and 13. Ablating 16 of 1,024 heads cuts learning (AGL 0.75 → 0.37, SRTT 1.00 → 0.71) and removes the layer-19 jump; 16 random heads have no effect, and Wikipedia loss rises only 0.8%. |
| 2026-11-08 | 4 | `04_noise_robustness` | [noise PDF](04_noise_robustness/reports/2026-11-08_meeting4_noise_robustness.pdf), [updated induction-heads PDF](04_noise_robustness/reports/2026-11-08_meeting4_induction_heads_and_noise.pdf) | At equal general damage, noise just before the induction heads (lens layers 15–18) costs about 10% of AGL learning, while noise after lens layer 19 costs none, even where it hurts general ability most. SRTT is too robust to be affected; the weakest of the three lines of evidence, but it points the same way. |
| 2026-11-09 | 5 | `05_head_specialization` | [specialization PDF](05_head_specialization/reports/2026-11-09_meeting5_head_specialization.pdf), [full induction-heads report](05_head_specialization/reports/2026-11-09_meeting5_induction_heads_full_report.pdf) | In SRTT the block-18 induction heads are interchangeable copies of one mechanism: any one of them restores most of the learning. In AGL they are partly divided, some pushing toward END and others toward continuing, and the learning needs their combination. |

## Adding a new experiment

1. Create the next numbered folder, e.g. `03_state_probe/`, with `code/`, `reports/` and a `README.md`.
2. Put the clean notebook in `code/`. After a run, add the executed notebook and its HTML export
   (`jupyter nbconvert --to html <notebook>_executed.ipynb`) next to it.
3. Add the meeting report to `reports/` as `YYYY-MM-DD_meetingN_<topic>.pdf` and one line to the meeting log above.

## Note on reproducibility (2026-11-09)
Before 2026-11-09, every Colab session generated different random word streams: the shared stream code (from the
paper) iterated over a Python `set`, whose order changes per session. Comparisons *within* a run were unaffected
(all conditions of a run share its streams), but saved results could not be reused in a later session. All clean
notebooks now iterate in sorted order, so every session generates the same streams.

## Running the notebooks

The notebooks run on Google Colab with a T4 GPU (Mistral-7B in 8-bit). Each theme's README has an
"Open in Colab" link. A Hugging Face token with access to `mistralai/Mistral-7B-v0.3` must be stored as the
Colab secret `HF_TOKEN`.
