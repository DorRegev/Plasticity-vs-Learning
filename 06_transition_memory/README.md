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

**How the knockout works:** a custom attention function (registered with `transformers`' `AttentionInterface`) sets
the scores of the blocked (query, key) links to −∞ in the selected heads only, before the softmax; all other heads and
layers run unchanged (layers without a selected head use the normal attention). The blocked links are chosen per run
from the stream itself, and only **strictly earlier** words are ever blocked: a word always keeps access to itself
(otherwise blocking S would also cut the current word off from itself whenever it was produced by S, and hurt the
*next* transition, a spurious off-diagonal effect). The reading map likewise leaves out the query's own position.
Only grammar-phase occurrences count as occurrences of a transition (the same words in the random prefix are not
blocked).

## Code
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

## Results
To be added after the run.
