# 07 · Continuation balance and induction-head stability

Two follow-ups in one notebook, so that one Colab session runs both.

## Part A: are the allowed continuations learned evenly?
**Question:** In AGL, q1 continues with 3, 0 or 2 (true 1/3 each). Test 3 showed the *mean* of the three rising toward
1/3. Does each word end near 1/3, or is one favoured and the mean hides it?

**Method:** for every visit to each AGL state (q0–q4), the model's final-output probability of each of the five words,
averaged over the 20 streams of `05`:
- each allowed word as its own curve, plus their mean, the true value 1/n, and the forbidden words;
- the actual share of each word among the earlier visits in that stream (the counts the model has seen);
- end of learning (last 100 visits): each word's probability ± SE and the spread between allowed words;
- does the model follow the counts it has seen? Per stream, the model's share of each word vs. its actual share, in an
  **early window (visits 20–150)**, where the counts still differ between streams, and at the end (last 100 visits),
  where every stream is within about ±0.02 of 1/n and there is little to follow. Reported as Pearson r, a one-sided
  **permutation p-value over the 20 streams** (actual counts shuffled between streams, so n = streams, not points; for
  two-word states one word only, since the two shares mirror each other), and the slope (how much of a stream's
  departure from 1/n the model reproduces).

Conditions: no switch-off, top-16 induction heads switched off, 16 random heads switched off (mean ablation, as in
`03`/`05`). The `05` (run 2) results are reused from Drive when present.

## Part B: are the same induction heads found with every test sequence?
**Question:** the induction heads were found with one test (25 random tokens repeated 4 times). Do other lengths and
numbers of repeats find the same heads?

**Method:** the `03` test on a grid of block lengths L = 10, 25, 50, 100, 250, 500, 1000 and repeats R = 2, 3, 4, 8
(up to 4,000 tokens; 26 combinations, e.g. 1000 × 2, 500 × 3, 25 × 4), 8 new random sequences each. For every
combination, all 1,024 heads get:
- a prefix-matching score;
- a copying score;
- an induction score (prefix × copying, the `03` ranking);
- for R ≥ 3, the share of the induction attention on the **most recent** earlier copy vs. older copies (how far back
  the head looks).

The score maps are then compared between combinations, and with the `03` maps, in this order of importance:
- **overlap of the top 16**;
- rank (Spearman) correlation;
- Pearson correlation over the 1,024 heads. It is pushed up automatically because ~1,000 heads score ≈ 0 in every
  shape, so it is reported last.

Caution for the look-back plot: recency and distance are mixed. In a 1,000-token block the most recent copy is already
1,000 tokens back, so a preference for the most recent copy only in short blocks may be about distance.

A table lists the heads that are in the top 16 for every combination.

**How "looking back" is measured:** at a position whose token appeared before, the induction target is the token right
after each earlier occurrence; the prefix-matching score is the share of the head's attention on those targets,
averaged over the positions in repeats 2 … R. Every earlier copy counts, however far back.

**Implementation:** a custom attention function (as in `06`) keeps the normal attention output. It also computes each
head's attention in float32 for up to 512 sampled query positions per sequence and reduces it to scores right away, so
4,000-token sequences fit in memory.

## Code
- [`code/balance_and_head_stability_run1_executed.ipynb`](code/balance_and_head_stability_run1_executed.ipynb)
  ([HTML](code/balance_and_head_stability_run1_executed.html)): the run, with all outputs (2026-11-17; Part A loaded
  from Drive, Part B 38 min).
- [`code/balance_and_head_stability.ipynb`](code/balance_and_head_stability.ipynb), with plain-language explanations
  before every section. [Open in Colab](https://colab.research.google.com/github/DorRegev/Plasticity-vs-Learning/blob/main/07_balance_and_head_stability/code/balance_and_head_stability.ipynb)
  - Colab T4, 8-bit model, about 30–50 minutes in total:
    - setup and model loading, ~10 min;
    - Part A, 0–15 min (0 when the `05` results load from Drive);
    - Part B, ~20–30 min.
  - Results are saved to `MyDrive/plasticity_lens_cache` (`head_specialization/`, `induction_patterns/`).

## Testing before the GPU run
- The whole notebook ran on CPU with a tiny random Mistral, with a small grid, including every plot and table.
- Built-in sanity checks:
  - the stream's continuation shares add up to 1 in every state;
  - the most recent copy is always one of the induction targets;
  - the custom attention recomputes the `03` test (same tokens) and must match the saved `03` prefix-matching scores
    (on the tiny model: max |diff| 0.000, r = 1.000).

## Results

### Run 1 (2026-11-17)
The sanity check passed: the custom attention reproduces the saved `03` prefix-matching scores (max |diff| 0.003,
r = 1.000).

#### Part A: balanced on average, not within a stream
**q1, last 100 visits (20 streams, ± SE):**

| | P('3') | P('0') | P('2') | mean | forbidden total |
|---|---|---|---|---|---|
| no switch-off | 0.282 ± 0.028 | 0.307 ± 0.031 | 0.296 ± 0.034 | 0.295 | 0.069 |
| top 16 off | 0.188 ± 0.030 | **0.257 ± 0.036** | 0.210 ± 0.031 | 0.218 | 0.264 |
| 16 random off | 0.287 ± 0.030 | 0.297 ± 0.031 | 0.300 ± 0.036 | 0.294 | 0.072 |

- **On average over streams, the three q1 words are learned evenly.** They differ by at most 0.025, within the SE.
  They end near 0.30 rather than 1/3 because 7% is still on the forbidden words.
- **Within each stream they are not even.** The gap between a stream's most and least likely allowed word is 0.28 on
  average in q1, and 0.14–0.24 in the other states. Single streams range from about 0.05 to 0.80 for one word.
  Averaging over streams cancels these preferences.
- **The per-stream preferences do not follow the counts the model has seen.** Model share vs. actual share, per stream,
  with a permutation p over 20 streams:

  | Window | q0 | q1 | q2 | q3 | q4 |
  |---|---|---|---|---|---|
  | early (visits 20–150), r (p) | −0.07 (0.62) | **0.33 (0.021)** | 0.05 (0.41) | −0.34 (0.93) | 0.11 (0.31) |
  | end (last 100), r (p) | −0.07 (0.62) | 0.21 (0.10) | −0.13 (0.70) | 0.06 (0.41) | 0.22 (0.17) |

  Only q1 early reaches p < 0.05, and it is 1 of 10 tests (not significant after a Bonferroni correction, p × 10 =
  0.21). The model's per-stream preferences (spread 0.14–0.28) are 3–10 times larger than the differences in the actual
  counts between streams (SD 0.04–0.06 early, 0.02–0.04 at the end). So something other than the counts sets them,
  most likely the particular random words a stream uses (an untested guess).
- **Small systematic preferences across streams, at the end states:** END is above the word exit in q3 (0.42 vs. 0.31)
  and in q2 (0.41 vs. 0.37), and in q0 '1' is above '0' (0.47 vs. 0.39). The symbols get different words in every
  stream, so these come from the structure, not from the words.
- **Without the top 16, the balance breaks:** in q1, '0' stays at 0.26 while '3' and '2' fall to about 0.19–0.21. The
  word exits of q2/q3 fall much more than END (q3: '3' 0.15 vs. END 0.34; q2: '2' 0.19 vs. END 0.34). This matches `05`,
  where these heads mainly support the word exits over END. 16 random heads change nothing.

#### Part B: the same core of induction heads, whatever the test
Grid: 27 shapes (L = 10 … 1,000 tokens × R = 2, 3, 4, 8, up to 4,000 tokens), 8 new random sequences each.

- **Top-16 overlap (main measure):** 13.4 of the `03` top 16 on average are again in the top 16 (range 11–15). The
  lowest values, 11, come from two repeats of long blocks (250 × 2, 500 × 2, 1000 × 2). The best are mid-length blocks
  with 3–4 repeats (15).
- **Heads in the top 16 for every one of the 27 shapes:** 18.0, 18.2, 18.3, 19.9, 26.6, 30.2; plus 12.7 and 19.8 in
  26 of 27. 12 of the `03` top 16 are in the top 16 in at least 75% of shapes. The edge of the set changes:
  - 20.28 is in the top 16 in only 14 of 27 shapes, and 29.10 in 9;
  - 24.5 (19 of 27) and 12.6 (11 of 27, strong prefix matching but weak copying) come in.
- **Rank correlation with `03`:** prefix matching 0.77–0.996; induction score 0.64–0.77. Both drop as blocks get
  longer (1000 × 2 lowest), so the ordering of the weaker heads depends on the test.
- **Pearson with `03`** (inflated by the ~1,000 heads near 0): prefix 0.85–0.998, mean 0.96.
- **Stability per head:**
  - 18.0, 18.2, 18.3 keep prefix matching at 0.8–0.95 in every shape (12.7: at least 0.75).
  - The weaker heads (19.8, 19.9, 26.6, 30.2, 31.4) rise with more repeats (highest at R = 8) and are lowest at R = 2
    with long blocks: they need more evidence before they attend.
- **How far back (R ≥ 3):** the top heads favour the most recent earlier copy.
  - R = 3: 0.9–1.0 on the most recent copy, where spreading evenly would give 0.75.
  - R = 4: 0.7–0.85, vs. 0.61.
  - R = 8: close to even (0.3–0.55, vs. 0.37). 18.2 has the strongest recency preference; 18.0 is closest to even.

  The pattern is about the same for L = 10 as for L = 1,000. So within this range it is not the distance in tokens that
  matters, but whether a copy is the most recent one.
- **Contrast with `06`:** on the grammar streams, with ~200 earlier occurrences, the same heads spread their attention
  almost evenly. Here, with only 2–7 earlier copies, they favour the most recent one. With many copies the preference
  flattens (already at R = 8), so the two results fit together.
