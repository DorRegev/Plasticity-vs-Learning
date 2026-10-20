# 01 · Per-layer decoding with the logit lens (meeting 1)

**Question:** At which of the 32 layers does the in-context grammar become readable?

**Method (logit lens):** apply the model's own final norm + output layer to the hidden state after every layer,
as if the network stopped there, and score the word that actually comes next. Two scores:
- **full vocabulary:** probability of the correct word among all ~32k tokens (what the model would say);
- **candidates only:** share of the probability among the 5 possible answers (4 words + END) that goes to the
  correct one (chance = 0.2).

Each layer is compared with its own score in the random phase: (structured − baseline) / (bound − baseline).

## Code
- [`code/layerwise_decoding.ipynb`](code/layerwise_decoding.ipynb): clean notebook (paper reproduction + logit
  lens), with plain-language explanations of every plot.
  [Open in Colab](https://colab.research.google.com/github/DorRegev/Plasticity-vs-Learning/blob/main/01_logit_lens/code/layerwise_decoding.ipynb)
- [`code/layerwise_decoding_executed.ipynb`](code/layerwise_decoding_executed.ipynb) and
  [`code/layerwise_decoding_executed.html`](code/layerwise_decoding_executed.html): the full run
  (100 runs per grammar, Mistral-7B-v0.3 in 8-bit, Colab T4).

## Results
- Checks pass: layer 32 through the lens equals the model's output exactly; layer-0 controls show no learning.
- **The grammar appears abruptly at layer 19**: within one layer, AGL jumps from ~2% to ~40% of the bound and
  SRTT from ~8% to ~53% (candidates-only score). Layers 0–18 are at or near chance.
- After layer 19 the score keeps rising with depth up to the last layer.
- The correct word is *preferred among the candidates* from layer 19, but becomes the model's actual word
  output (full vocabulary) only from ~layer 22.

## Report
[`reports/2026-10-13_meeting1_in_context_grammar_learning.pdf`](reports/2026-10-13_meeting1_in_context_grammar_learning.pdf)
