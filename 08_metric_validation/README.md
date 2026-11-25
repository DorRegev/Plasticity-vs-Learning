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
  - a permutation baseline: the earlier words' transition labels are shuffled within each run 1,000 times (100 in run
    1), and the real diagonal share is compared with the shuffled ones (p-value; the smallest possible p is ≈ 0.001).
- **3b, leave-one-in:** 4 random non-induction heads from blocks 18–19, each measured like the `05` Step C heads. With
  the 16 induction heads off, the head is compared on vs. off (on the same 20 + 20 streams, paired). Expected restored
  learning ≈ 0.
  - Since run 2, the cell lists the `allbut` files on Drive.
  - It loads `05` Step C under its exact name, or under any other digest whose streams match.
  - Anything still missing is recomputed and saved under `05`'s name (`RUN_MISSING_STEP_C = True`, about 8 min per
    head).
  - It then compares induction heads with random heads per stream: the mean restored learning over the 16 induction
    heads minus that over the 4 random heads (95% CI, sign-flip p).
- **3c, FDR:** every heatmap with significance stars gets per-cell p-values (paired t-test) and Benjamini–Hochberg
  stars (q < 0.05), next to the 3-SE stars. The maps:
  - the `06` knockout maps (top 16, both controls, the four block-18 heads);
  - `05` Step C;
  - the 3b controls.

  The table also gives the number of significant cells in the random controls.
- **3e, the `06` knockout per stream (added after run 1):** for the real transition knockout of the top 16 and for the
  random-position control, each stream gives:
  - the mean change on the diagonal (blocking a transition's own words, measured at that transition);
  - the mean change off the diagonal.

  Reported:
  - effect sizes: mean, 95% CI and Cohen's d_z for each;
  - paired tests over the 10 `06` streams (an exact sign-flip test over all 2^10 sign patterns, plus a paired t-test):
    - real diagonal − control diagonal;
    - (real diagonal − real off-diagonal) − (control diagonal − control off-diagonal).
  - AGL is the case in question; SRTT is shown for comparison.
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
    | Part 3b | ~30 min (+ ~2.2 h if the `05` Step C results must be recomputed) |
    | Part 3c | ~0 min |
    | Part 3e | ~0 min |
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

## Results (run 1, Colab T4)

Run 2 (3a with 1,000 shuffles, 3b with `05` Step C, the new 3e) is pending; its results will be added here.

- Executed notebook: [`code/metric_validation_run1_executed.ipynb`](code/metric_validation_run1_executed.ipynb).
  HTML: [`code/metric_validation_run1_executed.html`](code/metric_validation_run1_executed.html).
- 20 runs per grammar. Paired 95% bootstrap intervals; sign-flip p-values.

### Part 1. The layer-19 jump does not depend on how the score is normalized
- **Renormalized readings (both lenses, both grammars):** the largest one-layer increase is at layer 19 for all 16 versions (phase mean,
  normalized score, difference, ratio). Layer 21 is second in most of them.
- **Per run, at layer 19:**
  - SRTT: 90–100% of runs;
  - AGL: 50–70% of runs.
- **Full-vocabulary readings:** the jump is not at 19 except for the ratio. Probabilities stay below 0.001 until layer 19 and rise late
  (largest increase at layers 25–32). So the layer-19 result is a property of the renormalized reading, which is the reading we report.
- **Raw numbers, renormalized logit lens, AGL:**
  - baseline ≈ 0.19–0.20 at every layer (chance 0.2);
  - phase mean 0.195 at layer 18, 0.298 at 19, 0.406 at 32.
- **Same reading, SRTT:** 0.241 → 0.619 → 0.999 for the same layers. The baseline stays near 0.2.

### Part 2. Copying score and head selection
- **Our rank-based copying vs. Olsson's OV-eigenvalue copying:**
  - all 1,024 heads: Spearman 0.67, Pearson 0.76;
  - top 50 heads by prefix matching: Spearman 0.93.
  - Block 12 copies weakly in both: OV score 0.29–0.49, against ≥ 0.74 for the block-18/19 heads.
- **Head sets:**
  - (d) top 16 by prefix × OV copying: shares 13 of 16 heads with ours.
  - (b) Olsson thresholds: 14 heads, sharing 10 with ours. It adds 12.6, 2.21, 12.4 and 14.18 (high prefix, low copying) and drops
    31.31, 27.29, 22.6, 22.4, 29.10 and 18.1.
  - (c) top 16 by prefix alone: shares only 8 of 16 with ours. It includes anti-copying heads (28.0, 22.29).
- **Switching off set (b) vs. our set (a)**, change in learning against no heads off:
  - AGL: −0.431 for (b) vs. −0.356 for (a); (b) − (a) = −0.075 [−0.099, −0.051].
  - SRTT: −0.087 for (b) vs. −0.267 for (a); (b) − (a) = +0.180 [+0.150, +0.210].
  - 16 random heads: ≈ 0 in both grammars.
  - So both sets hurt learning, but the size depends on the set, and on the grammar in opposite directions. The ablation results are not
    invariant to the selection rule.

### Part 3. Controls
- **3a, reading map:**
  - **Induction heads:** all 16 heads are above the shuffled baseline in both grammars (p ≈ 0.01, the minimum with 100 permutations).
    Their diagonal share is 0.25–0.44 in AGL (shuffled ≈ 0.16) and 0.53–1.00 in SRTT (shuffled ≈ 0.11).
  - **Random heads:** 5 of 8 random head × grammar cases are also above the shuffled baseline. For example, 18.22 and 19.11 in AGL:
    0.19 and 0.18 vs. 0.16 shuffled. Their excess is much smaller (≤ 0.03 in AGL), so the test is sensitive; use the size of the
    excess, not the p-value alone.
- **3b, leave-one-in:**
  - **Random heads:** restoring one gives between −0.015 and +0.005 learning, at most 5.7% of the loss (|share|). Some of these values
    are nonzero by the sign-flip test.
  - **Induction heads: not run.** The `05` Step C results were not found on Drive for any of the 16 heads (`allbut_*` files), so the
    comparison with the induction heads is missing. It needs the `05` Step C run, or a fix to the cache names.
- **3c, FDR:**
  - **`06` top-16 knockout:** the diagonal survives FDR in AGL (11 / 11 cells) and partly in SRTT (6 / 9).
  - **Random controls:** 62 of 484 cells survive FDR. Almost all of them come from the random-position control (blocking random
    positions in the same 16 heads): 54 cells in AGL, including the whole diagonal.
    - Interpretation: in AGL, blocking random earlier positions in the induction heads hurts the same transitions. The AGL
      transition-specific claim of `06` therefore does not survive this control.
    - The SRTT diagonal survives it: 0 / 9 cells for random positions vs. 6 / 9 for the transition's own words.
  - **Random heads (random16):** 1 cell in AGL, 0 in SRTT.
  - **Missing:** the 18.2 and 18.3 maps of `06`, and the SRTT map of 18.1, were not found.
- **3d, noise at matched damage** (0.035–0.048 nats of Wikipedia damage per layer):
  - **AGL:** noise at layers 15–18 costs −0.049 to −0.054 learning; at 19–22, −0.002 to −0.014. Before minus after = −0.044
    [−0.048, −0.040]; 20 of 20 streams.
  - **SRTT:** the same direction, but tiny (−0.0014 [−0.0017, −0.0010]).
  - So the `04` result (learning is most sensitive just before block 18–19) holds at equal general damage.

