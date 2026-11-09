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

## Run 2 (default settings of the notebook)
Run 1 did Steps A and B. Run 2 (the notebook's current defaults) skips Step B (`RUN_STEP_B = False`) and runs:
- **Part 1 fresh:** no switch-off, top 16 switched off, and 16 random layer-matched heads, 20 runs each (the saved `03`
  results cannot be reused: they were made on other word streams, see the stream bug below);
- **Step C** (`LEAVE_ONE_IN = True`): all top-16 heads switched off except one, for each of the 16.

About 2.4 hours on a T4, saved to Drive as it goes. With the stream fix, a reconnect now reloads everything finished.

## Code
- [`code/head_specialization.ipynb`](code/head_specialization.ipynb): the notebook, with plain-language explanations
  before every section. [Open in Colab](https://colab.research.google.com/github/DorRegev/Plasticity-vs-Learning/blob/main/05_head_specialization/code/head_specialization.ipynb)
  - Colab T4, 8-bit model: Part 1 only loads saved results from Google Drive; Steps A–C about 2 h (plus about 2 h for
    Step C if it runs). Everything is saved to `MyDrive/plasticity_lens_cache/head_specialization`; after a disconnect:
    reconnect, **Run all**, approve the Drive popup, and it continues.
  - Part 1 never recomputes the saved results: if they are missing or were computed on different inputs (e.g. after a
    library update in Colab), it says so and skips them.

- [`code/head_specialization_run1_executed.ipynb`](code/head_specialization_run1_executed.ipynb) and
  [`code/head_specialization_run1_executed.html`](code/head_specialization_run1_executed.html): run 1 (2026-11-09;
  Steps A and B; Part 1 found no saved results; Step C skipped automatically).

## Testing before the GPU run
Run end to end on CPU with a tiny random Mistral, after a tiny run of the `03` short notebook into the same cache:
Part 1 loads every saved condition, Steps B and C reuse the saved baseline and top-k results, all conditions save and
reload, and every plot renders.

## Results

### Run 1 (2026-11-09)
**Step A, attention.** The three block-18 heads look at the correct earlier continuation for *every* transition
(generalists; 18.2 at 0.96–0.99 on every SRTT transition). In AGL, the heads divide the looking between the two ways
of leaving the end states q2, q3, q4:

| Head | END exits (q2→END, q3→END, q4→END) | word exits (q2→2, q3→3, q4→1) |
|---|---|---|
| 18.2 | **0.50, 0.40, 0.50** | 0.26, 0.25, 0.30 |
| 18.3 | 0.26, 0.22, 0.24 | **0.45, 0.42, 0.50** |
| 22.6 | **0.48, 0.42, 0.34** | 0.003, 0.05, 0.09 |
| 31.4 | 0.02, 0.02, 0.03 | 0.27, 0.14, 0.22 |

**Step B, one head switched off at a time** (20 paired runs per grammar):
- **SRTT: no single head matters.** Every change is below 0.0015 in probability. The sequence is fully covered by the
  other heads (redundancy).
- **AGL: small but structured effects.** Mean changes over all transitions are at most −0.01, but switching off
  **18.3** or **31.4** lowers the word exits of q2/q3/q4 (q2→2, q3→3, q4→1; up to −0.048) and *raises* the END exits
  (up to +0.04): these heads push "continue with a word" over "END". Switching off **18.2** lowers the END exits
  (q4→END −0.022). So the specialization is about one decision, END vs. continue at the end states, with
  complementary heads, and it matches what the heads look at in Step A (attention vs. damage, r = 0.43 in AGL;
  r = 0.18 in SRTT, where single-head effects are ~0).
- Random control heads: no effect. The specialization index (0.12–0.36) does not separate the heads from the random
  controls (0.19–0.25): it only counts drops, and these heads trade one transition against another.

**Part 1** found none of the saved `03` results on Drive, and Step C was skipped automatically (the largest
single-head change, 0.048 in AGL, was above the 0.02 threshold; for SRTT all single-head changes are tiny).

**Stream bug found in this run.** The word streams were different in every Colab session: `build_random_DFA` (paper
code, shared by every notebook) iterates over a Python `set` of strings, whose order depends on Python's hash seed,
which is random per session. So saved results never matched a later session (this is also why `03` recomputed its
baseline). Results *within* a session are paired and valid; only reuse across sessions was affected. Fix: iterate in
sorted order (tested: identical streams across hash seeds). **Applied to every clean notebook (00–05) on 2026-11-09;**
the executed notebooks stay as they ran.
