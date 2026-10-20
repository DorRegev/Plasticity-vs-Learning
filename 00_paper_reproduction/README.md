# 00 · Paper reproduction

**Question:** Does a frozen Mistral-7B-v0.3 learn an artificial grammar purely in context, as reported in
*Computation or Weight Adaptation?* (bioRxiv 2024.03.07.583890)?

**Setup:** One long word stream per run, in three phases: random words → a grammar (SRTT: one fixed 8-word
sequence; AGL: a 5-state rule system with random choices) → random words again. At every position we record the
probability the model gives to the word that actually comes next. 100 runs, each with a different random
4-word vocabulary.

## Code
- [`code/computation_or_weight_adaptation.ipynb`](code/computation_or_weight_adaptation.ipynb): the
  reproduction notebook (adapted from the authors' notebook): learning curves, per-state probabilities,
  vocabulary switch, swapped-token control, SRTT, KL divergence.
  [Open in Colab](https://colab.research.google.com/github/DorRegev/Plasticity-vs-Learning/blob/main/00_paper_reproduction/code/computation_or_weight_adaptation.ipynb)

The same reproduction is also the first part of [`01_logit_lens/code/layerwise_decoding.ipynb`](../01_logit_lens/code/layerwise_decoding.ipynb),
which is the notebook whose run produced the numbers below.

## Results
- **AGL:** the model reaches ~0.39 of the 0.46 theoretical bound (~85%; paper: 79%).
- **SRTT:** near perfect, ~0.99 (paper: 92% of the bound).
- Probability returns to chance (0.2) when the grammar is removed; the controls behave as in the paper.
- Our runs use the 8-bit model (the paper used float16).

The write-up is part of the meeting-1 report:
[`01_logit_lens/reports/2026-10-13_meeting1_in_context_grammar_learning.pdf`](../01_logit_lens/reports/2026-10-13_meeting1_in_context_grammar_learning.pdf).
