# 05 · Head specialization: does each induction head serve particular transitions?

**Question:** Switching off the top induction heads together cut in-context grammar learning (`03_induction_heads`).
Are the heads interchangeable copies of one mechanism, or does each serve **particular transitions** of the grammar,
so that switching off one head breaks exactly those transitions? (A head cannot store a word pair: the weights are
frozen and every run uses new random words. It can specialize in a *kind* of transition.)

## Transitions
- **SRTT:** the 9 positions of the sequence `0 1 2 2 0 2 3 1 END`, labelled previous word → next word. Only `3→1`
  and `END→0` are unique for simple copying; after `0`, `1` and `2` several words can follow, so the other 7 need
  more context.
- **AGL:** the 11 transitions (state before the word → word, e.g. `q1 → 3`). Every state has 2–3 options. The previous
  word alone identifies the state only after `END` (always `q0`); every other word can lead into two states.

## Method
1. **Part 1 (no new runs):** the saved `03_induction_heads` short-rerun results (50 runs per grammar; top 4, 8, 16 and
   2 random draws of 16 switched off) split per transition: paired per-run change from no switch-off, ± SE. For SRTT,
   ambiguous vs. unique transitions are compared directly.
2. **Step A (attention map, ~15 min):** for each head and transition, the share of attention on the correct earlier
   continuation (earlier places where the same transition happened). 5 runs per grammar, 400 query positions each.
3. **Step B (single heads, ~1.5 h):** the top 12 heads, block 12 head 6, and 2 random layer-matched control heads,
   each switched off alone (mean ablation), 20 paired runs per grammar. Per transition: paired change ± SE (`*` when
   above 3 SE). Per head: mean change, largest drop, number of clear drops, and a **specialization index** (0 = damage
   spread evenly over transitions, 1 = all on one; the random heads show the noise level). Step A vs. Step B are
   compared per (head, transition).
4. **Step C (leave one in, ~2 h, only if single-head effects are tiny):** all top-16 heads switched off except one,
   for each of the 16; what that one head restores per transition, relative to all 16 off.

All steps read the model's final output (probability of the correct next word, last 1,000 grammar words).

## Code
- [`code/head_specialization.ipynb`](code/head_specialization.ipynb): the notebook, with plain-language explanations
  before every section. [Open in Colab](https://colab.research.google.com/github/DorRegev/Plasticity-vs-Learning/blob/main/05_head_specialization/code/head_specialization.ipynb)
  - Colab T4, 8-bit model: Part 1 only loads saved results from Google Drive; Steps A–C about 2 h (plus about 2 h for
    Step C if it runs). Everything is saved to `MyDrive/plasticity_lens_cache/head_specialization`; after a disconnect:
    reconnect, **Run all**, approve the Drive popup, and it continues.
  - Part 1 never recomputes the saved results: if they are missing or were computed on different inputs (e.g. after a
    library update in Colab), it says so and skips them.

## Testing before the GPU run
Run end to end on CPU with a tiny random Mistral, after a tiny run of the `03` short notebook into the same cache:
Part 1 loads every saved condition, Steps B and C reuse the saved baseline and top-k results, all conditions save and
reload, and every plot renders.

## Results
To be added after the run.
