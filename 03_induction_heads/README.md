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
| File | What it is |
|---|---|
| [`code/induction_heads.ipynb`](code/induction_heads.ipynb) | **Full notebook, corrected** (all conditions: k = 4, 8, 16, 32, 3 random draws, zero ablation; ~4–5 h). [Open in Colab](https://colab.research.google.com/github/DorRegev/Plasticity-vs-Learning/blob/main/03_induction_heads/code/induction_heads.ipynb) |
| [`code/induction_heads_short.ipynb`](code/induction_heads_short.ipynb) | **Short rerun** with the corrected copying score: k = 4, 8, 16 (per-layer lens at 16), 2 random draws, no zero ablation; reuses run 1's baseline from Drive; ~2–2.5 h. [Open in Colab](https://colab.research.google.com/github/DorRegev/Plasticity-vs-Learning/blob/main/03_induction_heads/code/induction_heads_short.ipynb) |
| [`code/induction_heads_run1_executed.ipynb`](code/induction_heads_run1_executed.ipynb), [`.html`](code/induction_heads_run1_executed.html) | **Run 1** (full notebook, 50 runs per grammar), kept as it ran, with a correction note at the top. |

Both notebooks run on a Colab T4 (8-bit model). Every finished condition (and every 10 runs within one) is saved to
Google Drive (`MyDrive/plasticity_lens_cache/induction_heads`). After a disconnect: reconnect, **Run all**, approve
the Drive popup, and it continues where it stopped.

**Layer numbering.** Head scores index heads by transformer block (0–31). The logit lens's "layer N" is the state
*after* block N−1. So heads in block 12 write into lens layer 13 (the small step) and heads in block 18 into lens
layer 19 (the jump).

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

### Run 1 (2026-10-21; copying score flawed, see below)
- **Strong induction heads by prefix matching** (score ≈ 0.9, also active on our SRTT streams): **block 18, heads 0,
  2, 3** and **block 12, heads 6, 7** (head 4 ≈ 0.6), plus block 28 head 0. These feed exactly lens layers 19 (the
  jump) and 13 (the small step).
- **Bug:** the copying score (share of the raised logit mass on the attended token) was ~0 for every head, so the
  prefix × copying ranking was close to arbitrary. The ablated top-32 set contained the three block-18 heads plus 29
  weak heads, and missed the block-12 heads. Fixed in both notebooks (rank-based copying score).
- **32 random layer-matched heads: no effect.** The top-32 set: **AGL 0.745 → 0.405, SRTT 0.997 → 0.872**, with
  Wikipedia loss +1.4% (random: +0.5%) and Olsson's ICL score on Wikipedia unchanged. Zero ≈ mean ablation.
- **Per-layer lens:** the jump at lens layer 19 halves (AGL 0.41 → 0.19, SRTT 0.51 → 0.25), layers 0–18 are
  unchanged, later layers recover part of it.
- **AGL state q1:** allowed and forbidden continuations still separate (0.26 vs. 0.035; baseline 0.30 vs. 0.03).
- Reading: specific, not general damage; AGL depends on these heads more than SRTT. Since the block-12 heads were not
  ablated, the short rerun with the corrected ranking is needed for a clean test.

### Short rerun
To be added.
