# 06 · Transition memory: which attention reads which earlier transition?

**Question:** The weights are frozen, so a transition's only "memory" is the earlier places in the stream where it
already happened. When the model predicts transition T, which heads read from the earlier occurrences of T (or of
other transitions), and does the prediction depend on that reading?

## Method
1. **Step 1, reading map (~10 min):** for each of the top-16 induction heads and the four block-18 heads, how its
   attention splits over the earlier words of every source transition S, per predicted transition T (an S × T matrix),
   plus a recency profile (attention on the most recent, 2nd, …, 10th most recent earlier occurrence of T). 5 runs per
   grammar, 400 query positions each.
2. **Step 2, attention knockout (causal):** in the selected heads, block all attention to the earlier words of one
   transition S (for each S), and measure the change in P(correct next word) for every transition T, paired per run
   against a **no-block baseline of the same heads** (same custom-attention code path, nothing blocked, so rounding
   differences between attention implementations cancel). One S × T effect map per head set, and a **diagonal score** (mean diagonal effect − mean
   off-diagonal effect, per run).
   - **2a:** the top-16 induction heads together, with two controls: blocking the same number of random earlier words
     (of other transitions), and blocking S in 16 random layer-matched heads.
   - **2b:** the block-18 heads 18.0, 18.1, 18.2, 18.3 one at a time.
3. **Step 3, recency knockout (top 16):** for every predicted word, block only the most recent earlier occurrence of its
   transition, all older ones, or all of them, plus a matched random control. Copying vs. pooling.

10 paired runs per grammar in Steps 2–3; final output, last 1,000 grammar words.

**How the knockout works:** a custom attention function (registered with `transformers`' `AttentionInterface`) runs
the normal attention for every head, then recomputes each selected head on its own (float32), with the scores of the
blocked (query, key) links set to −∞ before the softmax, and replaces that head's output; all other heads and layers
are unchanged. One head at a time keeps the extra GPU memory to ~0.1 GB for 4,000-token streams (all 32 heads at once
needed several GB and ran out of memory on the T4). The blocked links are chosen per run
from the stream itself, and only **strictly earlier** words are ever blocked: a word always keeps access to itself
(otherwise blocking S would also cut the current word off from itself whenever it was produced by S, and hurt the
*next* transition, a spurious off-diagonal effect). The reading map likewise leaves out the query's own position.
Only grammar-phase occurrences count as occurrences of a transition (the same words in the random prefix are not
blocked).

## Code
- [`code/transition_memory_run1_executed.ipynb`](code/transition_memory_run1_executed.ipynb)
  ([HTML](code/transition_memory_run1_executed.html)): the run, with all outputs (2026-11-15/16, two Colab sessions,
  resumed from the Drive cache).
- [`code/transition_memory.ipynb`](code/transition_memory.ipynb): the notebook, with plain-language explanations
  before every section. [Open in Colab](https://colab.research.google.com/github/DorRegev/Plasticity-vs-Learning/blob/main/06_transition_memory/code/transition_memory.ipynb)
  - Colab T4, 8-bit model, about **5.5 hours** in total (including one no-block baseline per head set), in this order so that a short session already answers the main
    question: Step 1 (~10 min), Step 2a with controls (~2 h), Step 3 (~20 min), Step 2b (~2.7 h). Everything is saved
    to `MyDrive/plasticity_lens_cache/transition_memory`; after a disconnect: reconnect, **Run all**, approve the
    Drive popup, and it continues.

## Testing before the GPU run
- The custom attention, on a tiny Mistral: with no layer selected it reproduces the model's normal attention exactly;
  computing a selected layer itself (nothing blocked) differs by ~1e-7; blocked links get exactly zero attention.
- The whole notebook, on CPU with a tiny random Mistral: every step, caching, and every plot. Built-in sanity checks:
  no blocking = normal output; blocked links get zero attention in the selected head and the other heads are
  untouched; every blocked word in a transition knockout is the word that transition produces; a word is never blocked
  from itself; the per-run mask reaches the attention end to end (input → stream → mask). A separate check of the
  mask rules (recent / older / all / random: exact sets, strictly earlier, never the start token, random control
  count-matched and disjoint from the transition's words). A second session with a different hash seed loaded every
  condition from the cache.

## Reports
- [`reports/2026-11-16_meeting6_transition_memory.pdf`](reports/2026-11-16_meeting6_transition_memory.pdf) (meeting 6)

## Results

### Run 1 (2026-11-15/16; 10 paired runs per grammar)
Sanity checks on the real model: the recomputed head matches the normal attention (relative error 0.4%; other heads
of the layer bit-identical); recomputing all 16 heads with nothing blocked changes the logits by 0.04 on average
(rounding through the 8-bit layers, which cancels against the no-block baselines); blocking reaches the attention
(up to 3.7 log-prob).

**Step 2a: each transition is retrieved from its own earlier occurrences.** Blocking the earlier words of transition
S in the top-16 induction heads hurts the prediction of S and almost nothing else (a red diagonal in both grammars).
Both controls are about zero.

| Diagonal score (diagonal − off-diagonal, ± SE) | AGL | SRTT |
|---|---|---|
| Top-16 induction heads, block S | **−0.278 ± 0.008** | **−0.423 ± 0.029** |
| Control: top-16, as many random earlier words | +0.022 ± 0.001 | 0.000 |
| Control: 16 random heads, block S | +0.004 ± 0.001 | 0.000 |

Mean drop on the diagonal: AGL −0.26 (per transition −0.16 to −0.35), SRTT −0.42.

**AGL: the occurrences act as competing evidence.** The off-diagonal effects come in blue pairs inside each state
(q0→0 / q0→1, q1→3 / q1→0 / q1→2, q2→END / q2→2, q3→END / q3→3, q4→END / q4→1): hiding the earlier occurrences of one
continuation *raises* the probability of the other continuations of the same state. The reading map shows the same
structure: in AGL the heads spread their attention over all continuations of the current state (a block per state),
not only the correct one. So the heads gather the history of every possible continuation, and the prediction weighs
them against each other. In SRTT the reading map is a sharp diagonal: the heads read exactly the transition being
predicted, including the ambiguous ones (2→2, 2→0, 2→3), so they use more than the previous word.

**Step 3: pooling (AGL) vs. one example (SRTT).**

| Block, in the top 16 (mean change in P(correct)) | AGL | SRTT |
|---|---|---|
| most recent occurrence only | −0.003 | 0.000 |
| all older ones (keep the most recent) | −0.245 | −0.255 |
| all earlier occurrences | −0.249 | −0.696 |
| control: as many random earlier words | +0.034 | 0.000 |

- The most recent occurrence alone never matters, and the recency profile shows why: attention is spread almost evenly
  over all (~200) earlier occurrences of the transition, about 0.002 each.
- **AGL:** keeping the most recent occurrence rescues nothing (−0.245 vs. −0.249). The heads pool many occurrences,
  like counting how often each continuation happened, which a probabilistic choice needs.
- **SRTT:** keeping the most recent occurrence rescues about 60% of the loss (−0.26 vs. −0.70). In a deterministic
  sequence one example already says what comes next.
- Caveat: in AGL the random control *improves* the prediction (+0.034, up to +0.11 for q0→0 and q0→1), because the
  random words include the other continuations of the same state: removing competing evidence. It fits the picture
  above, but this control is not neutral.

**Step 2b: single block-18 heads.** Each head alone shows the same AGL pattern (red diagonal, blue sibling pairs) at
about 1/6 to 1/5 of the group effect: diagonal score 18.0 −0.042, 18.1 −0.034, 18.2 −0.049, 18.3 −0.039 (± 0.001 to
0.002). The four together add up to −0.16, about 60% of the group's −0.26 mean diagonal drop. In SRTT a single head
does almost nothing (at most −0.003): the other heads cover for it, the same redundancy as in `05`.

**In short:** the in-context "memory" of a transition is the set of its earlier occurrences in the stream, read by
the induction heads. In AGL many occurrences of every continuation of the current state are read and weighed against
each other (counting); in SRTT the heads read exactly the transition being predicted and one recent example is
largely enough (copying). The memory is shared across many heads, in AGL roughly additively.
