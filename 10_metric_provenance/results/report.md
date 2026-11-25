# Metric provenance report

Run 2026-11-25. Two questions:
- **Part A:** does each source claim we make match the paper's full text?
- **Part B:** for the metrics we call "ours", is there a published precedent?

This report changes no slides or docs.

**How it was checked:**
- **Full texts:** 43 sources were downloaded by `code/fetch_fulltexts.py`. Versions are listed in [`sources.md`](sources.md);
  for each paper the latest version at the time of the run was used, and for Lior et al. v1 as well.
- **Quotes:** every quote below was checked by `code/find_quotes.py`. It appears verbatim in the downloaded text, apart from
  whitespace and line-break hyphens; the ids and pages are in [`quotes.md`](quotes.md).
  - Page numbers are PDF pages.
  - The two HTML sources (the logit-lens post and Olsson et al.) have no pages, so the section heading is given instead.
- **Formulas:** the extracted PDF text loses most math layout. Formulas are therefore described in words, except where the
  text survived extraction.
- **Candidate search (Part B):** `code/search_precedents.py` screened 8,040 unique papers by title and abstract. The output
  is in [`candidates.csv`](candidates.csv) and [`candidates_top.md`](candidates_top.md). The papers came from:
  - 23 Semantic Scholar searches;
  - every paper citing Wang 2022 (1,487), Meng 2022 (3,858), Geva 2023 (698), Belrose 2023 (750) and Bansal 2023 (79);
  - the 2,831 papers of `09_literature_search`, which already contain the citation trails of Olsson, Crosbie & Shutova,
    Todd, Edelman, Akyürek, Yin & Steinhardt, Wu, Ma & Xu, Saanum and Lior.
- **Full-text reading (Part B):** 33 candidates were read in full. Each was chosen either because the screen flagged it, or
  because it is a known source for that kind of measure.
- **Limits of the search:**
  - Abstracts rarely describe metric details, so the screen can miss papers. "Not found" below means not found in this
    search, not "does not exist".
  - Only open full texts could be read.

## Summary

| Metric | Status before | Status after | Key citation |
|---|---|---|---|
| A1 Lior et al.: P(correct next word) vs. a theoretical upper bound | established | **established**. The claim is correct. Their only normalization is "% of the upper bound" (model ÷ bound, no baseline subtracted). | Lior et al. 2024, bioRxiv v4 p. 8, p. 17 |
| A2 logit lens / tuned lens | established | **established**, with one correction: the original logit-lens post used the layer-norm normalization *without* its learned affine part. | nostalgebraist 2020; Belrose et al. 2023 Eq. 3, 8 |
| A3 Olsson prefix-matching and copying scores | established | **established**, with one correction. The copying score is an empirical direct-path (unembedding) score; the OV eigenvalue measure only validates it. | Olsson et al. 2022, "(3) Head activation evaluators" |
| A4 Bansal et al.: combining prefix matching and copying | established | **established**. They neither combine nor threshold the two scores (qualitative "both" plus per-property sums). | Bansal et al. 2023, §6.3, App. A.4 |
| A5 Wang mean ablation; Crosbie & Shutova top 1% / 3% vs. layer-matched random heads, prefix-only ranking | established | **established**. Correct. | Wang et al. 2022 pp. 3–4; Crosbie & Shutova 2025 §4.2–4.3 |
| A6 Meng causal tracing (3σ embedding noise, single-state restoration) | established | **established**. Correct, for GPT-2 XL; other models used a fixed ν, and MLP/attention restore windows of 10 layers. | Meng et al. 2022 App. B.1 |
| A7 Geva attention knockout | established | **established**. Correct. Details: all heads of a layer, from the last position to the chosen positions, over a window of layers. | Geva et al. 2023 §5 |
| B1 Renormalized lens readout (share of the correct answer among the 5 allowed; chance 1/5) | ours | **adapted from Zhao et al. 2021** (label probabilities renormalized to one). Applying it to lens layers is new as far as found; Halawi et al. 2023 use the lens on label tokens but read it differently. | Zhao et al. 2021 p. 5 |
| B2 Learning score (phase − baseline) ÷ (bound − baseline) | ours | **adapted**: the same algebra as Hake's normalized gain, Atari human-normalized scores and normalized patching effects. The theoretical bound is Lior et al.'s. | Badia et al. 2020; Zhang & Nanda 2023; Hake 1998 (via Cooksey & Jonsson 2022) |
| B3 Copying score as a rank of the attended token (one head, direct path, final norm + unembedding) | ours | **adapted from Olsson et al. 2022** (same pipeline, ReLU-ratio instead of rank) **and Wang et al. 2022** (rank-based top-5 copy score) | Olsson 2022; Wang 2022 §3.1 |
| B4 Induction score = prefix matching × copying | ours | **ours**. No paper found that multiplies the two. Precedents require "both" qualitatively (Olsson, Bansal) or rank by prefix matching alone (Crosbie, Yin). | Olsson 2022 (definition of "both") |
| B5 Noise at one intermediate layer, layers compared at equal general (Wikipedia) damage | ours | **ours** for matching the noise to equal damage. Gaussian-noise corruption itself is established, at the input. | Meng 2022; Zhang & Nanda 2023 (related) |
| B6 Leave-one-in restoration (16 heads off, restore one) | ours | **adapted from Wang et al. 2022**: their "minimality" test with K = the head's class minus the head is the same contrast. | Wang 2022 §4.2 |
| B7 Reading map (attention share by the transition that produced each attended token) | ours | **ours**. The diagonal corresponds to prefix matching at the level of transitions (Olsson, Edelman); a full transition × transition map with a permutation baseline was not found. | Olsson 2022; Edelman 2024 (related) |
| B8 Recency knockout (most recent earlier occurrence vs. older vs. all) | ours | **ours** for the recency split. The per-head "all occurrences" knockout is **very similar to Crosbie & Shutova 2025 §4.4**; the knockout method is Geva 2023. | Crosbie & Shutova 2025 §4.4; Geva 2023 |

**Two follow-ups for our own text and code. Not acted on; you asked for no changes.**
- The notebooks label the head set "prefix ≥ 0.3, OV copying > 0" as "Olsson thresholds" (`08`), and `03` uses "prefix ≥ 0.3,
  copying ≥ 0.7". No numeric threshold appears in Olsson et al. 2022 or Bansal et al. 2023 (A3, A4), so these are our
  cut-offs.
- Wherever our slides say "the copying score of Olsson et al. is based on OV eigenvalues", the paper's own copying score is
  the direct-path evaluator. Their eigenvalue score is a validation measure (A3). Our `08` "OV copying" is that validation
  measure.

---

## Part A. Source claims checked against the full texts

### A1. Lior, Shalev, Stanovsky & Goldstein 2024 (bioRxiv 10.1101/2024.03.07.583890)
**Claim:** they measure learning as the probability of the correct next word, and compare it with the best possible
(upper bound) for each grammar.

**Verdict: CORRECT.**

**Normalization, exactly:**
- The per-word measure is the raw probability of the actual next word under the model's full next-word distribution; it
  is not renormalized.
- The upper bound is a reference value: the true DFA transition probability of each step, averaged over the sequence. It
  is 1 for SRTT and about 0.45 for AGL.
- The only normalization is a summary ratio: the model's mean probability ÷ the upper bound, over the last 1,000 words of
  the structured part (92% for SRTT, 79% for AGL).
- No baseline is subtracted.
- v4 adds a KL divergence to the true transition probabilities. That is not a normalization of P(correct).
- v1 (2024-03-07) has the same 92% / 79% sentence (A1-f, p. 5). v4 (2026-10-12) is the latest version.

**Unverifiable:** how a word that spans several tokens is scored. The text speaks of "words" and "tokens" interchangeably.

**Evidence (v4, https://www.biorxiv.org/content/10.1101/2024.03.07.583890v4.full.pdf):**
> "the model assigns a probability for each word in its vocabulary to be the next word, and we extract the probability
> that the model assigns to the actual next input word" (p. 6, Fig. 2 caption)

> "The improvement of the performance is defined by the increase in the probability that the LLM assigns to the correct
> next token." (p. 6)

> "Then, the theoretical upper bound for the sequence is the average of all transition probabilities between each pair of
> consecutive states" (p. 17, SI section B)

> "The model reaches 92% of the SRTT upper bound and 79% of the AGL upper bound, averaging the last 1000 iterations of the
> structured part." (p. 8)

> "we compute the KL divergence between the model's predicted next-token distribution and the true transition
> probabilities at each state" (p. 12)

Version dates come from the page headers: v4 "this version posted October 12, 2026", v1 "this version posted March 7,
2024".

### A2. nostalgebraist 2020 (logit lens); Belrose et al. 2023 (tuned lens, arXiv 2303.08112)
**Claim:** the logit lens decodes intermediate layers with the model's own final norm + unembedding; the tuned lens trains
an affine translator per layer.

**Verdict: PARTLY WRONG** (the logit-lens half, as attributed to the original post). The tuned-lens half is correct.

**Correction:**
- The original post (GPT-2) decodes the intermediate "activations" after layer norm but *before the learned point-wise
  (affine) transformation*, through the tied embedding matrix W.
- The formulation "final LayerNorm, then W_U" is Belrose et al.'s Eq. 3, the version most code (and ours) implements. Cite
  Belrose et al. for the exact operation, and nostalgebraist for the idea.
- Tuned lens: one affine translator (A_ℓ, b_ℓ) per layer, followed by the logit lens, trained with a KL (distillation)
  loss to the final-layer output. The translators are initialized at the identity.

**Evidence:**
- nostalgebraist, "interpreting GPT: the logit lens", sections "background on GPT's structure" and "the logit lens"
  (https://www.lesswrong.com/posts/AcKRB8wDpdaN6v6ru/interpreting-gpt-the-logit-lens):
  > "We have a "dictionary," W , that lets us convert between vocab space and embedding space at any point."

  > "For transformer experts: the "activations" here are the block outputs after layer norm, but before the learned
  > point-wise transformation."
- Belrose et al. 2023, arXiv v6 (https://arxiv.org/abs/2303.08112):
  > "The logit lens consists of setting the residuals to zero: LogitLens(hℓ ) = LayerNorm[hℓ ]WU ." (p. 2, Eq. 3)

  > "We train L affine transformations, one for each layer of the network, with a distillation loss: transform the hidden
  > state so that its image under the unembedding matches the final layer logits as closely as possible." (p. 2)

  > "We refer to (Aℓ , bℓ ) as the translator for layer ℓ." (p. 4; the tuned lens is LogitLens(Aℓhℓ + bℓ), Eq. 8)

  > "We initialized all translators to the identity" (p. 5)

### A3. Olsson et al. 2022 (arXiv 2209.11895)
**Claim:** the prefix-matching score is measured on repeated random tokens as attention to the token after the earlier
copy; the copying score is based on the OV circuit's eigenvalues.

**Verdict: PARTLY WRONG** (the copying half). The prefix-matching half is correct.

**Exact definitions (both averaged over 10 examples):**
- **Prefix matching:** 25 random tokens, without the most and least common tokens, repeated 4 times, with a
  start-of-sequence token prepended. The score is the average attention from each token to "the tokens that preceded the
  same token in earlier repeats". The wording is ambiguous on its own; the Key Concepts definition makes clear that this is
  the token that *followed* the earlier copy ("it attends to the token which induction would suggest comes next").
- **Copying:** 25 random tokens, with no start-of-sequence token, "by mistake".
  1. The head's output is taken along the direct path and passed through the unembedding to logits.
  2. The mean is subtracted, then a ReLU is applied.
  3. The score is the ratio of the attended token's raise to the raise of all tokens, rescaled from [0, 0.5] to [−1, 1].
- **The OV eigenvalue measure** (sum of eigenvalues ÷ sum of their absolute values) is *not* the copying score. It appears
  only in the appendix "Validating head activation evaluators" as a weight-based check that the copying evaluator
  correlates with.
- **No numeric threshold:** induction heads are those with both properties, measured as a continuum.

**Evidence:** transformer-circuits.pub, sections "Key Concepts / Induction Heads", "Model Analysis Table / (3) Head
activation evaluators" and "Validating head activation evaluators"
(https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads/index.html):
> "Prefix matching: Generate a sequence of 25 random tokens, excluding the most common and the least common tokens. Repeat
> this sequence 4 times and prepend a "start of sequence" token." … "The prefix matching score is the average of all
> attention pattern entries attending from a given token back to the tokens that preceded the same token in earlier
> repeats."

> "That is, it attends to the token which induction would suggest comes next."

> "It would've been better if we had used a start of sequence token for the copying head evaluator as well, but we
> omitted it by mistake."

> "Copying : Generate a sequence of 25 random tokens, excluding the most common and the least common tokens. Compute this
> head's contribution to the residual stream, then convert that using the unembeddings (i.e. along the "direct path") to
> impacts on each logit. Logits are transformed by subtracting the mean of the logits and passing through a ReLU, allowing
> the evaluator to focus on where logits are raised. Compute the ratio of the amount it raises the logits of the token
> being attended to, to that of all tokens in this sample. This value ranges from 0 (only raises other tokens) to 0.5
> (only raises the present token), so we scale it into the range of -1 to 1."

> "Our copying evaluator correlates well with the OV matrix of each head. Specifically here we plot against the sum of
> the eigenvalues, divided by the absolute value of the eigenvalues, which is a measure of what fraction of the
> eigenvalues are positive vs. negative."

> "In practice, induction heads don't exhibit these properties perfectly, and our measurements give us a continuum, but
> there is a clear subset of heads which exhibit these properties with much greater than random chance."

### A4. Bansal et al. 2023 (arXiv 2212.09095)
**Claim:** they score heads on both prefix matching and copying. How do they combine or threshold them?

**Verdict: CORRECT** that they score both. **They neither combine nor threshold.**
- **The scores:** they follow Olsson et al., with 100 sequences of varying length; 4% of the most and least frequent tokens
  are excluded.
- **Reading the two together:** qualitatively, from the two heatmaps. Heads high in both "can be deemed plausible induction
  heads".
- **Aggregates:** each property is summed over heads ("total capacity") and tracked under pruning.
- **Their copying algorithm differs from Olsson's text** (App. A.4, Algorithm 2):
  - it applies a softmax over the vocabulary;
  - it takes the most-attended token;
  - it restricts the mean and ReLU to the attendable input tokens.

**Evidence:** arXiv v2 (https://arxiv.org/abs/2212.09095):
> "We follow the approach described by Olsson et al. (2022), but instead of computing scores using 10 sequences with fixed
> length of 25, we compute these scores using 100 sequences with varying lengths" (p. 14, App. A.4)

> "When seen in conjunction, these observations indicate that there is a sparse set of attention heads that are capable
> of performing both primitive operations and thus can be deemed plausible induction heads." (p. 9, §6.3)

> "we first formalize the total capacity of a model to perform prefix matching (or copying) to be the sum of the
> respective scores for individual attention heads in the model." (p. 9)

> "remove 4% most & least common tokens" (p. 15, Algorithm 1)

> "logits ← softmax(logits, dim = 1)" … "temp_score ← relu_raised_logit_max_ind/sum(relu_raised_logits)" (p. 16, Algorithm 2)

### A5. Wang et al. 2022 (arXiv 2211.00593); Crosbie & Shutova 2025 (arXiv 2407.07011)
**Claims:**
- Wang et al. mean-ablate heads.
- Crosbie & Shutova mean-ablate the top 1% and 3% of induction heads, against random heads matched to the induction heads'
  layer distribution, with heads ranked by prefix matching only.

**Verdict: CORRECT** (both).

**Details:**
- **Wang et al.:**
  - nodes are (head, position) pairs;
  - the mean is taken over a reference distribution, pABC (three unrelated names), separately for each template.
- **Crosbie & Shutova:**
  - head means come from MNLI premises concatenated to 3,000 tokens;
  - the mean is taken per position and truncated to the prompt length;
  - prefix matching uses 50 random tokens repeated 4 times.

**Evidence:**
- Wang et al. 2022, arXiv v1 (https://arxiv.org/abs/2211.00593):
  > "we instead knockout nodes through mean ablation: replacing them with their average activation value across some
  > reference distribution" (p. 3)

  > "In this work, all knockouts are performed in a modified pIOI distribution called pABC ." … "When knocking out a
  > single node, a (head, token position) pair in our circuit" … "we compute the mean of a node across samples of the
  > same template." (p. 4)
- Crosbie & Shutova 2025, arXiv v3 (https://arxiv.org/abs/2407.07011):
  > "we conduct mean-ablations of 1% and 3% of the heads with the highest prefix matching scores" (p. 4, §4.3)

  > "we also randomly ablate 1% and 3% of the model's heads, which are selected following the layer distribution of the
  > previously ablated induction heads." (p. 4)

  > "We argue that focusing solely on prefix matching scores is sufficient for our analysis" (p. 4, §4.2)

  > "We generate a sequence of 50 random tokens, excluding the 4% most common and least common tokens. This sequence is
  > repeated four times to form the input to the model." (p. 4)

  > "premises are concatenated to create 500 samples, each comprising of 3000 tokens" (p. 4)

  > "During inference, the activations of the ablated heads are replaced with the mean activations by truncating them to
  > the length of the current prompt." (p. 4)

### A6. Meng et al. 2022 (arXiv 2202.05262)
**Claim:** causal tracing adds Gaussian noise (3× the embedding standard deviation) to the subject token embeddings, then
restores single hidden states from the clean run and measures the recovery.

**Verdict: CORRECT.**

**Details:**
- σ is the standard deviation of token embeddings over a body of text.
- Noise is redrawn 10 times per text.
- For GPT-NeoX and GPT-J, ν is a fixed value instead (0.03 and 0.025).
- Hidden states are restored singly, but MLP and attention outputs are restored as windows of 10 layers.

**Evidence:** arXiv v5 (https://arxiv.org/abs/2202.05262):
> "we corrupt the embeddings of the token naming the subject s by adding Gaussian noise" … "is set to be three times
> larger than the observed standard deviation σt of token embeddings as sampled over a body of text. For each run of
> text, the process is repeated ten times with different samples of corruption noise." (p. 15, App. B.1)

> "When we restore hidden states from the original run, we substitute the originally calculated values from the same
> layer and the same token, and then we allow subsequent calculations to proceed without further intervention." (p. 15)

> "restored runs of ten values of mi (and ai , respectively) for an interval of layers ranging from" (p. 15)

> "For GPT-NeoX we adjust the injected noise to ν = 0.03 and in GPT-J we use ν = 0.025 to match embedding magnitudes."
> (p. 16)

### A7. Geva et al. 2023 (arXiv 2304.14767, EMNLP)
**Claim:** attention knockout blocks attention edges from chosen positions.

**Verdict: CORRECT.** More precisely:
- The attention mask entry is set to −∞ from a source position (the last position) to the chosen target positions.
- This is done in **all heads** of the layer.
- It is applied over **a window of k layers** (9 for GPT-2, 5 for GPT-J) to limit leakage.
- Our per-head knockout is closer to Crosbie & Shutova 2025 §4.4 (see B8).

**Evidence:** arXiv v3 (https://arxiv.org/abs/2304.14767):
> "We block xℓr from attending to xℓc at a layer ℓ < L by updating the attention weights to that layer" (p. 4, §5; the
> mask is set to −∞ for all heads j ∈ [1, H], Eq. 7)

> "For each layer ℓ, we block the attention edges from the last position to each of S, R and the last" … "for a window
> of k layers around the ℓ-th layer, and measure the change in prediction probability. We set k = 9 (5) for GPT-2
> (GPT-J)." (p. 4)

> "For this reason, we block a range of layers rather than a single layer" (p. 9, Limitations)

---

## Part B. Precedents for the metrics we call "ours"

Closeness scale:
- **SAME:** the same quantity.
- **VERY SIMILAR:** the same construction, with a different detail.
- **RELATED:** the same idea, a different construction.

### B1. Renormalized lens readout
**Ours:** lens probabilities, restricted to the task's 5 allowed answers, renormalized to sum to 1; we read the correct
answer's share (chance 1/5).

| Precedent | Closeness | Difference from ours | Quote |
|---|---|---|---|
| Zhao, Wallace, Feng, Klein & Singh 2021, *Calibrate Before Use*, [arXiv 2102.09690](https://arxiv.org/abs/2102.09690) | VERY SIMILAR | Final-layer output, not a lens. The renormalized label probabilities are the input to a calibration step, not reported as a share against chance. | "For classification tasks, p̂ is the set of probabilities that are associated with each label name, renormalized to one." (p. 5) |
| Halawi, Denain & Steinhardt 2024, *Overthinking the Truth* (ICLR), [arXiv 2307.09476](https://arxiv.org/abs/2307.09476) | RELATED | Logit lens on label tokens at every layer, but the readout is "calibrated accuracy" (correct label above its median probability), not a renormalized share. Their permuted score is divided by chance (1/#labels). | "we decode next-token probabilities for each intermediate layer, using the "logit lens" method" (p. 5); "we measure how often the correct label has a higher probability than its median probability over the dataset." (p. 4); "To make the results comparable across datasets, we divide the permuted scores by this random baseline." (p. 5) |

No paper was found that renormalizes logit- or tuned-lens probabilities over a task's allowed answers and reads the correct
share against chance. **Status: adapted from Zhao et al. 2021, applied per lens layer** (Halawi et al. 2023 is the closest
lens use).

### B2. Learning score per layer
**Ours:** (mean P(correct) in the learning phase − mean in the random baseline phase) ÷ (theoretical upper bound −
baseline).

| Precedent | Closeness | Difference from ours | Quote |
|---|---|---|---|
| Badia et al. 2020, *Agent57*, [arXiv 2003.13350](https://arxiv.org/abs/2003.13350) (human-normalized score) | VERY SIMILAR | The same (score − random) ÷ (reference − random) form. The ceiling is human performance, not a theoretical bound. | "In addition to using human normalized scores HNS =" (p. 5; the formula follows as (Agent score − Random score) ÷ (Human score − Random score), with a capped version clipped to [0, 1]) |
| Zhang & Nanda 2024, *Towards Best Practices of Activation Patching* (ICLR), [arXiv 2309.16042](https://arxiv.org/abs/2309.16042) | VERY SIMILAR | The same min–max form; the floor and ceiling are the corrupted and clean runs. Uses logit difference, not probability. | "we always normalize this by LDcl (r, r′ ) − LD∗ (r, r′ ), so it typically lies in [0, 1], where 1 corresponds to fully restored performance and 0 to the corrupted run performance." (p. 3) |
| Hake 1998, normalized gain, *Am. J. Phys.* 66, 64 (closed access; quoted through Cooksey & Jonsson 2022, [arXiv 2210.01823](https://arxiv.org/abs/2210.01823)) | VERY SIMILAR | g = (post − pre) ÷ (100% − pre): the baseline is a pre-test and the ceiling is the maximum score. The primary source could not be read (UNVERIFIABLE from Hake directly). | "this can be quantified as the normalized gain (Hake, 1998):" (p. 3; the formula follows as g = (Post[%] − Pre[%]) ÷ (100% − Pre[%])) |
| Lior et al. 2024 (A1) | RELATED | Model ÷ upper bound, without subtracting the baseline. | "The model reaches 92% of the SRTT upper bound and 79% of the AGL upper bound…" (v4 p. 8) |
| Halawi et al. 2024 | RELATED | Divides by chance only, with no ceiling. | "we divide the permuted scores by this random baseline." (p. 5) |

**Status: adapted.** The normalization is a standard normalized-gain / min–max form. The pieces specific to us are:
- the random-sequence phase as the floor;
- Lior et al.'s theoretical bound as the ceiling;
- the per-layer application.

### B3. Copying score as a rank
**Ours:** one head's output (direct path) → final norm + unembedding → the rank of the attended token among the
vocabulary, mapped to +1 (top) … 0 (chance).

| Precedent | Closeness | Difference from ours | Quote |
|---|---|---|---|
| Olsson et al. 2022, copying evaluator (A3) | VERY SIMILAR | The same pipeline (head output → direct path → unembedding → the attended token). They read it as a ReLU-ratio of logit raises, rescaled to [−1, 1], instead of a rank; on random tokens; the text does not mention a final norm. | "Compute this head's contribution to the residual stream, then convert that using the unembeddings (i.e. along the "direct path") to impacts on each logit." ("(3) Head activation evaluators") |
| Wang et al. 2022, copy score, [arXiv 2211.00593](https://arxiv.org/abs/2211.00593) | VERY SIMILAR | Rank-based and through the final norm, like ours. But it is binary (top 5) and simulates perfect attention: OV applied to the residual at the name token after MLP0, not the head's actual output. | "we multiplied this by the OV matrix of a Name Mover Head (simulating what would happen if the head attended perfectly to that token), multiplied by the unembedding matrix, and applied the final layer norm to obtain logit probabilities. We compute the proportion of samples that contain the input name token in the top 5 logits" (p. 6) |
| Bansal et al. 2023, Algorithm 2 (A4) | VERY SIMILAR | Olsson's evaluator with a softmax, the most-attended token, and only the attendable tokens. Not a rank. | "temp_score ← relu_raised_logit_max_ind/sum(relu_raised_logits)" (p. 16) |
| McDougall et al. 2023, *Copy Suppression*, [arXiv 2310.04625](https://arxiv.org/abs/2310.04625) | RELATED | A rank of the token itself in the head's (effective) OV circuit, but static (weights) and for suppression (most negative). | "84.70% of the tokens in GPT-2 Small's vocabulary have their diagonal elements as one of the top 10 most negative values in their columns" (p. 5) |
| Gould et al. 2023, *Successor Heads*, [arXiv 2312.09230](https://arxiv.org/abs/2312.09230) | RELATED | A rank among the task tokens in the effective OV circuit, testing for the successor rather than the same token. | "We call the proportion of succession dataset tokens on which an attention head performs succession the succession score." (p. 3) |

**Status: adapted from Olsson et al. 2022 and Wang et al. 2022.** Our continuous rank (+1 … 0) on the head's actual output
and task tokens was not found as such.

### B4. Induction score = prefix matching × copying
**Ours:** the product of the two scores, used to rank heads.

| Precedent | Closeness | Difference from ours | Quote |
|---|---|---|---|
| Olsson et al. 2022 (A3) | RELATED | Requires both properties, but as a definition; no combined number and no threshold. | "a head with both a "copying" OV circuit and a "prefix matching" QK circuit is thereby an induction head by our definition" ("(3) Head activation evaluators") |
| Bansal et al. 2023 (A4) | RELATED | "Both" is read qualitatively from heatmaps; each property is summed separately. | "…capable of performing both primitive operations and thus can be deemed plausible induction heads." (p. 9) |
| Wu et al. 2024, *Retrieval Head*, [arXiv 2404.15574](https://arxiv.org/abs/2404.15574) | RELATED | A per-event conjunction (the head's most-attended token = the generated token, within the needle), counted as a frequency; not a product of two head scores. | "we say an attention head h copies and pastes a token from the needle to the output sentence if it follows two criteria" (p. 3) |
| Crosbie & Shutova 2025 (A5); Yin & Steinhardt 2025, [arXiv 2502.14010](https://arxiv.org/abs/2502.14010) | RELATED | Rank by prefix matching alone. | Crosbie: "We argue that focusing solely on prefix matching scores is sufficient for our analysis" (p. 4); Yin: "To identify and analyze induction heads, we measure their induction scores using the TransformerLens framework" (p. 2; the score is the attention from r′ᵢ to rᵢ₊₁ on a repeated random sequence) |

Also read, with no combined score found:
- Singh et al. 2024 (arXiv 2404.07129);
- Feucht et al. 2025 (arXiv 2504.03022);
- *Induction Signatures Are Not Enough* (arXiv 2509.22947);
- *Copying Under Repetition* (arXiv 2610.26722);
- *A Geometric Invariant of Attention…* (arXiv 2611.12206);
- *A Circuit for In-Context Learning* (arXiv 2611.05344).

**No precedent for the product was found. Status: ours.** The product is a continuous form of Olsson's "both".

### B5. Noise at one intermediate layer, compared at equal general damage
**Ours:** Gaussian noise added at one layer (all positions). The noise size is set per layer so that the increase in
Wikipedia loss is the same.

| Precedent | Closeness | Difference from ours | Quote |
|---|---|---|---|
| Meng et al. 2022 (A6) | RELATED | Noise on the subject's input embeddings only, with a fixed size (3σ). Used to corrupt, then restore; not compared across layers at matched damage. | "we corrupt the embeddings of the token naming the subject s by adding Gaussian noise" (p. 15) |
| Zhang & Nanda 2024, [arXiv 2309.16042](https://arxiv.org/abs/2309.16042) | RELATED | Gaussian noising as a corruption method, on input tokens. | "Gaussian noising (GN) adds a large Gaussian noise to the token embeddings of the tokens that contain the key information to completing a prompt" (p. 2) |
| Heimersheim & Nanda 2024, *How to use and interpret activation patching*, [arXiv 2404.15255](https://arxiv.org/abs/2404.15255) | RELATED | Points out the sensitivity to the noise level; this is the problem that matched damage addresses. No layer comparison. | "The success of Gaussian noise corruption is highly sensitive to the noise level." (p. 4) |
| *Tracing distinguishability through transformer processing with stochastic LayerNorm* 2026, [arXiv 2608.30720](https://arxiv.org/abs/2608.30720) | RELATED | Gaussian noise at every residual read, with per-read noise scales set by an information budget, not by downstream damage. | "We normalize the residual-stream state, add isotropic Gaussian noise, and renormalize" (p. 3) |
| Lad, Gurnee & Tegmark 2024, [arXiv 2406.19384](https://arxiv.org/abs/2406.19384) | RELATED | Layer-by-layer interventions compared across depth (deletion, swap), not noise and not damage-matched. | "we perform layer-wise interventions—deleting individual layers or swapping adjacent ones" (p. 2) |

Also read: *Sensitivity, Causality, and Repair Dissociate* (arXiv 2608.03842). It has layer-wise perturbation analyses, but
of input perturbations ("When a language model fails on surface-perturbed input (typos, OCR noise, homophones)", p. 1),
not of noise matched in size.

**Status: ours** for the matched-damage comparison across layers. Gaussian-noise corruption itself is established.

### B6. Leave-one-in restoration
**Ours:** ablate 16 heads, restore one at a time, and measure how much task performance comes back (per transition).

| Precedent | Closeness | Difference from ours | Quote |
|---|---|---|---|
| Wang et al. 2022, minimality, [arXiv 2211.00593](https://arxiv.org/abs/2211.00593) | VERY SIMILAR | With K = (the head's class) \ {v}, the score \|F(C \ (K ∪ {v})) − F(C \ K)\| is the effect of the head when the rest of its class is off, i.e. our contrast. Differences: it is computed inside the circuit C (everything outside C also ablated), as an absolute logit-difference change, with K chosen per head. | "This can be evaluated by showing that v can significantly recover F after knocking out a set of nodes K." (p. 10); "Formally, the minimality criterion is whether for every node v ∈ C there exists a subset K ⊆ C \ {v} that has high minimality score \|F (C \ (K ∪ {v})) − F (C \ K)\|." (p. 10); "For most heads, removing the class of heads G that v is a part of provides" … "a reasonable minimality score, but in some instances a more careful choice is needed" (pp. 10–11) |
| Meng et al. 2022 (A6) | RELATED | The same "restore one component into a broken run" logic. The run is broken by input noise, not by head ablation. | "When we restore hidden states from the original run, we substitute the originally calculated values…" (p. 15) |
| Todd et al. 2024, *Function Vectors* (ICLR), [arXiv 2310.15213](https://arxiv.org/abs/2310.15213) | RELATED | One head's mean task activation is patched into a corrupted prompt (shuffled labels) and the recovery is measured; nothing else is ablated. | "We also make use of uninformative ICL prompts p̃ti ∈ P̃t for which the labels are shuffled" … "measure its causal indirect effect (CIE) towards recovering the correct answer" (p. 3) |
| Heimersheim & Nanda 2024 | RELATED | Defines denoising (clean → corrupted patching) in general. | "then running the model on the corrupted prompt while overwriting some of its activations with previously saved clean-prompt activations" (p. 3) |
| Michel, Levy & Neubig 2019, [arXiv 1905.10650](https://arxiv.org/abs/1905.10650) | RELATED | Keeps one head per layer (all others masked) to test redundancy within a layer, not restoration within an ablated set. | "many attention layers can even be individually reduced to a single attention head" (p. 2) |

**Status: adapted from Wang et al. 2022 (minimality).**

### B7. Reading map
**Ours:** a head's attention share, grouped by which earlier transition (grammar state → next word) produced each attended
token. This gives a transition × transition map, tested against shuffled transition labels.

| Precedent | Closeness | Difference from ours | Quote |
|---|---|---|---|
| Olsson et al. 2022, prefix matching (A3) | RELATED | One category only: attention to the token after an earlier copy of the current token. This is our diagonal at the token level. | "That is, it attends to the token which induction would suggest comes next." ("Key Concepts") |
| Edelman et al. 2024, [arXiv 2402.11004](https://arxiv.org/abs/2402.11004) | RELATED | Markov chains; attention inspected visually for tokens that follow the same token as the current one (the diagonal for bigram states); no grouped map or test. | "we inspected the attention in each layer throughout training" … "the second layer attending to tokens that follow the same token as the current one" (p. 8) |
| Akyürek et al. 2024, [arXiv 2401.12973](https://arxiv.org/abs/2401.12973) | RELATED | "n-gram heads": attention to tokens after matching n-gram contexts, described and hard-coded, not measured as a share map. | "We find that Transformers develop "n-gram heads" that attend to the next token after contexts matching the current context window." (p. 9) |
| Crosbie & Shutova 2025 §4.4 | RELATED | Groups attended positions by "followed a token of the same category", but as a knockout target, not a map. | "we block attention from each token to all tokens that directly followed tokens of the same category" (p. 9) |
| Clark, Khandelwal, Levy & Manning 2019, [arXiv 1906.04341](https://arxiv.org/abs/1906.04341) | RELATED | Per-head attention evaluated against linguistic relation categories (BERT), not grammar transitions. | "we treat each head as a simple no-training-required classifier that, given a word as input, outputs the most-attended-to other word." (p. 1) |

Also read, with no transition-level map found:
- *Selective induction heads* (arXiv 2509.08184);
- *Induction Heads Interpolate N-Grams* (arXiv 2607.02800);
- Saanum et al. 2025 (arXiv 2509.21534).

**Status: ours.** Its diagonal generalizes prefix matching (Olsson; Edelman) from tokens to grammar transitions.

### B8. Recency knockout
**Ours:** in chosen heads, block attention to only the most recent earlier occurrence of the current transition, vs. to
all older ones, vs. to all.

| Precedent | Closeness | Difference from ours | Quote |
|---|---|---|---|
| Crosbie & Shutova 2025 §4.4, [arXiv 2407.07011](https://arxiv.org/abs/2407.07011) | VERY SIMILAR (to our "all" condition) | A per-head knockout of attention to *all* tokens that followed a same-category token; no split by recency. | "we block attention from each token to all tokens that directly followed tokens of the same category" (p. 9); "we prevent xhc from attending to xhr in head h by modifying the attention weights in that layer" (p. 5) |
| Geva et al. 2023 (A7) | RELATED | The knockout method itself: all heads of a layer, a window of layers, from the last position. | "We block xℓr from attending to xℓc at a layer ℓ < L by updating the attention weights to that layer" (p. 4) |
| Edelman et al. 2024 | RELATED | Raises the recency question (induction looks for "recent occurrence(s)") but does not test it by knockout. | "a circuit that looks for recent occurrence(s) of the current token" (p. 2) |

Also read, with no recency-split knockout found:
- *A Circuit for In-Context Learning* (arXiv 2611.05344), which studies heads that read or suppress the most recent *label*
  ("dozen heads writes against whichever label the model saw most recently", p. 2);
- *Understanding Synthetic Context Extension via Retrieval Heads* (arXiv 2410.22316).

**Status: ours** for the most-recent vs. older split. The "all occurrences" condition is very similar to Crosbie & Shutova
2025.

---

## Files
- `quotes.md`: every quote with its page and a found / not-found check (all 86 found).
- `sources.md`: every downloaded source with its URL and version.
- `candidates.csv`, `candidates_top.md`: the Part B screen (title and abstract only).
