# 03 · Induction heads: do they carry the in-context grammar learning?

**Question:** Is the in-context grammar learning carried by **induction heads** (Olsson et al., 2022), the attention
heads that do *[A][B] … [A] → [B]*: attend to the token right after the previous occurrence of the current token
and copy it? Hypothesis: they sit around layers 13–19 (where the lenses showed the step and the jump), and ablating
them destroys SRTT learning (pure copying) and reduces AGL learning partly or fully.

## Method
1. **Find induction heads.** Score all 32 × 32 heads on 25 random tokens repeated 4 times:
   - **prefix matching**: attention to the token after earlier copies of the current token;
   - **copying**: does the head's direct contribution to the output raise the token it attends to? (range −1 to +1).

   Also scored: previous-token heads (Wikipedia) and prefix matching on our own SRTT streams.
2. **Ablate.** Replace a head's 128 numbers at the input of `o_proj` with their mean on Wikipedia (mean ablation;
   zero ablation as a check). Conditions on AGL and SRTT: no ablation; top-k induction heads, k = 4, 8, 16, 32;
   32 random non-induction heads matched by layer (3 draws); zero ablation of the top 32; optional previous-token heads.
3. **General-ability controls** per condition: Wikipedia loss and Olsson's ICL score (loss at token 500 − loss at token 50).
4. **Measurements:** learning curves, dose-response (learning, Wikipedia loss and ICL score vs. k), the AGL state-q1
   check (allowed vs. forbidden continuations), and the per-layer logit lens for the baseline and the top-32 ablation.

## Code
- [`code/induction_heads.ipynb`](code/induction_heads.ipynb): the notebook, with plain-language explanations before
  every section. [Open in Colab](https://colab.research.google.com/github/DorRegev/Plasticity-vs-Learning/blob/main/03_induction_heads/code/induction_heads.ipynb)
  - Colab T4, 8-bit model. With the default `N_RUNS = 50` paired runs per grammar it takes **about 4–5 hours**. A
    runtime-estimate cell prints the remaining time before the long part starts.
  - Every finished condition (and every 10 runs within one) is saved to Google Drive
    (`MyDrive/plasticity_lens_cache/induction_heads`). After a disconnect: reconnect, **Run all**, approve the
    Drive popup, and it continues where it stopped.

## Testing before the GPU run
The whole notebook was run end to end on CPU with a tiny random Mistral (4 layers × 4 heads): scoring, the hooks,
every condition, caching and resuming, and all plots. Built-in sanity checks:
- toy patterns for the prefix-matching score (perfect induction head = 1, previous-token head = 0);
- the copying score gives +1 / −1 for a head that only raises / lowers its target;
- the 32 single-head `o_proj` outputs add up to the layer's output;
- ablating one head changes exactly its 128 numbers and nothing else in that layer;
- random draws have the same per-layer counts as the induction set;
- the baseline reproduces the earlier layer-32 numbers (~0.79 AGL, ~1.0 SRTT, candidates only).

A tiny model trained on repeated random sequences solved the task with a *shifted* copying circuit (it moved tokens
two positions forward and attended two positions past the classic target), which Olsson's prefix-matching score
does not detect. This is a caveat for interpreting low scores in Mistral as well.

## Results
To be added after the run.
