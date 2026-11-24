# 08 · Validating our own measures

**Question:** before writing the paper, do our conclusions depend on how we defined our own scores, on how we picked
the heads, or on missing controls?

## Part 1. Learning score vs. raw numbers
**The score being checked:** our learning score is (phase mean − baseline) ÷ (bound − baseline).

**Method:**
- Per layer, both lenses, both readings (full vocabulary, renormalized) and both grammars, it is shown next to:
  - the raw phase mean and the raw baseline (± SE over runs);
  - two alternatives: the difference (phase mean − baseline) and the ratio (phase mean ÷ baseline).
- For every version: the layer with the largest one-layer increase (expected: 19), and the share of single runs whose
  largest increase is at 19.
- A table of raw numbers at layers 0, 13, 18, 19, 24 and 32.
- The `02` lens results were computed before the stream fix, so the lens pass is redone on 20 runs per grammar. The
  tuned lens itself loads from Drive.

## Part 2. Our copying score vs. Olsson et al. (2022), and the head selection
**Olsson's OV-circuit copying score, for all 1,024 heads:**
- Score = sum(eigenvalues) ÷ sum(|eigenvalues|) of W_U · N_final · W_O^h · W_V^h · N_in · W_E.
- Computed from the 128 × 128 matrix (W_V^h · N_in · W_E) · (W_U · N_final · W_O^h), which has the same nonzero
  eigenvalues.
- The RMSNorm weights are folded in.
- GQA: query head h uses value head h // 4.
- The 8-bit weights are read back one layer at a time by passing the identity through each layer.
- Sanity checks: the read-back weights reproduce each layer, and the small matrix's trace equals the full circuit's
  trace.

**Comparison with our rank-based copying:** Pearson and Spearman correlation over all heads and over the top 50 by
prefix matching, plus a scatter plot with blocks 12 and 18 marked.

**Head sets:**
- (a) our top 16 by prefix × copying;
- (b) Olsson thresholds: prefix ≥ 0.3 and OV copying > 0;
- (c) top 16 by prefix alone;
- (d) top 16 by prefix × OV copying.

If (b) differs from (a) by more than 4 heads, (b) is switched off on the 20 + 20 streams of `05`. It is compared, run
by run, with (a) and with 16 random heads.

## Part 3. Controls for our new analyses
- **3a, reading map:**
  - the `06` map for 4 random non-induction heads from blocks 18–19;
  - a permutation baseline: the earlier words' transition labels are shuffled within each run 100 times, and the
    real diagonal share is compared with the shuffled ones (p-value).
- **3b, leave-one-in:** 4 random non-induction heads from blocks 18–19, each measured like the `05` Step C heads. With
  the 16 induction heads off, the head is compared on vs. off (on the same 20 + 20 streams, paired). Expected restored
  learning ≈ 0.
- **3c, FDR:** every heatmap with significance stars gets per-cell p-values (paired t-test) and Benjamini–Hochberg
  stars (q < 0.05), next to the 3-SE stars. The maps:
  - the `06` knockout maps (top 16, both controls, the four block-18 heads);
  - `05` Step C;
  - the 3b controls.

  The table also gives the number of significant cells in the random controls.
- **3d, noise:**
  1. For lens layers 15–22, the noise size giving 0.05 nats of Wikipedia damage is taken from the `04` Wikipedia
     losses on Drive.
  2. The 20 + 20 streams run with that noise.
  3. Per stream: learning with noise − without (the `05` baseline). Reported as the mean with 95% bootstrap intervals,
     plus a paired test of layers 15–18 vs. 19–22 (sign-flip and t-test).

  The random-direction control (noise orthogonal to the top principal components) is not included; the paired test is
  the alternative that was asked for.

A summary cell collects the pass/fail criteria. A final cell explains how to read every result.

## Code
- [`code/metric_validation.ipynb`](code/metric_validation.ipynb), with plain-language explanations before every part.
  [Open in Colab](https://colab.research.google.com/github/DorRegev/Plasticity-vs-Learning/blob/main/08_metric_validation/code/metric_validation.ipynb)
  - Colab T4, 8-bit model, about 3–3.5 h in total:

    | Step | Time |
    |---|---|
    | Setup | ~10 min |
    | Part 1 | ~30–45 min |
    | Part 2 | ~5 min (+ ~10 min if the threshold set needs its own ablation) |
    | Part 3a | ~10 min |
    | Part 3b | ~30 min |
    | Part 3c | ~0 min |
    | Part 3d | ~75 min |

    The notebook measures the time per run first and prints an estimate per part.
  - Reused from Drive:
    - the `05` (run 2) switch-off and Step C results;
    - the `06` knockout results;
    - the tuned lens and the induction scores;
    - the `04` Wikipedia damage curves.
  - New results are saved under `MyDrive/plasticity_lens_cache/metric_validation/`; after a disconnect, **Run all**
    continues.

## Testing before the GPU run
- The whole notebook ran on CPU with a tiny random Mistral, including every plot and table. The `06` FDR maps were
  loaded from the `06` test caches, and the noise comparison ran with a tiny damage level so that every code path ran.
- Built-in sanity checks:
  - the per-run scores reproduce `lens_phase_summary`;
  - both lenses share the last layer;
  - the read-back weights reproduce each layer (tiny model: relative error 0);
  - the trace of each 128 × 128 matrix equals the trace of the full OV circuit (relative difference ≤ 6e-6);
  - the eigenvalue score is +1 for the identity and −1 for its negative;
  - the random control heads are not induction heads.

## Results
To be added after the run.
