# 02 · Tuned lens vs. logit lens (meeting 2)

**Question:** Is the abrupt onset at layer 19 a property of the model, or an artifact of the logit lens (which
reads every layer with the last layer's output map)?

**Method:** a **tuned lens** (Belrose et al. 2023) learns one affine correction per layer that translates that
layer's state into the last layer's format. It is trained on generic text (WikiText-103), **never on the grammar
task**, so it cannot learn the grammar itself. One forward pass per run reads every layer through both lenses.

## Code
- [`code/layerwise_decoding_tuned_lens.ipynb`](code/layerwise_decoding_tuned_lens.ipynb): clean notebook. It
  only runs the lens tests (no paper reproduction).
  [Open in Colab](https://colab.research.google.com/github/DorRegev/Plasticity-vs-Learning/blob/main/02_tuned_lens/code/layerwise_decoding_tuned_lens.ipynb)
  - Trains the tuned lens (~40 min on a T4; 400 steps × 2 × 512 tokens, 128 sampled positions per sequence) and
    saves it to Google Drive (`MyDrive/plasticity_lens_cache`); later runs reload it.
  - Training and the lens passes save their progress, so a Colab disconnect only costs a few minutes:
    reconnect, **Run all**, approve the Drive popup, and it resumes.
- [`code/layerwise_decoding_tuned_lens_executed.ipynb`](code/layerwise_decoding_tuned_lens_executed.ipynb) and
  [`code/layerwise_decoding_tuned_lens_executed.html`](code/layerwise_decoding_tuned_lens_executed.html): the
  full run (Colab T4, 8-bit model).

## Results
- The tuned lens is much closer to the model's final output than the logit lens on held-out text
  (e.g. layer 15: 2.4 vs. 7.3 nats KL).
- **Candidates-only score: both lenses show the same abrupt onset at layer 19**, with a faint precursor
  (~5–10% of the bound) at layers 13–18. The onset is a property of the model, not of the logit lens.
- SRTT reaches the bound at the last layer; AGL reaches ~80%.
- On the full-vocabulary score the tuned lens rises *later* than the logit lens: trained on Wikipedia, it spreads
  probability over typical text tokens on our unusual word stream. Its ranking of the candidates is the same.
- Caveats: small training budget (~400k tokens vs. ~65M in the paper); 8-bit model; a tuned lens only finds
  linearly readable information. Next step: a probe on the DFA state.

## Report
[`reports/2026-10-20_meeting2_in_context_grammar_learning.pdf`](reports/2026-10-20_meeting2_in_context_grammar_learning.pdf)
