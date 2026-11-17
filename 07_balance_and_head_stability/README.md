# 07 · Continuation balance and induction-head stability

Two follow-ups in one notebook, so that one Colab session runs both.

## Part A: are the allowed continuations learned evenly?
**Question:** In AGL, q1 continues with 3, 0 or 2 (true 1/3 each). Test 3 showed the *mean* of the three rising toward
1/3. Does each word end near 1/3, or is one favoured and the mean hides it?

**Method:** for every visit to each AGL state (q0–q4), the model's final-output probability of each of the five words,
averaged over the 20 streams of `05`:
- each allowed word as its own curve, plus their mean, the true value 1/n, and the forbidden words;
- the actual share of each word among the earlier visits in that stream (the counts the model has seen);
- end of learning (last 100 visits): each word's probability ± SE, the spread between allowed words, and, per stream,
  the correlation between the model's share of each word and that word's actual share in the stream.

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

The score maps are then compared between combinations, and with the `03` maps, using:
- Pearson correlation over the 1,024 heads;
- rank (Spearman) correlation;
- overlap of the top 16.

A table lists the heads that are in the top 16 for every combination.

**How "looking back" is measured:** at a position whose token appeared before, the induction target is the token right
after each earlier occurrence; the prefix-matching score is the share of the head's attention on those targets,
averaged over the positions in repeats 2 … R. Every earlier copy counts, however far back.

**Implementation:** a custom attention function (as in `06`) keeps the normal attention output. It also computes each
head's attention in float32 for up to 512 sampled query positions per sequence and reduces it to scores right away, so
4,000-token sequences fit in memory.

## Code
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
To be added after the run.
