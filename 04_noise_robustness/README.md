# 04 · Noise robustness: how fragile is each layer for in-context grammar learning?

**Question:** If we disturb the model's internal state at one layer with random noise, how much of the in-context
grammar learning is lost, compared with how much general ability is lost? Is noise just *before* the jump at lens
layer 19 (where the induction heads read the earlier words) more harmful than noise just *after* it?

## Method
- **Noise:** at one lens layer L (the output of transformer block L−1, i.e. the state the logit lens reads at
  layer L), every token's state gets a random vector added. Its direction is random, and its size is **α times
  that token's own state size**, so layers with very different state sizes are compared fairly. The first token
  (BOS) is left alone. Each run gets its own noise draw, reproducibly.
- **Conditions:** lens layers 10, 13, 15, 17, 18, 19, 20, 22, 25, 28 × α = 0.05, 0.1, 0.2, 0.4, 0.8, plus no noise.
  AGL and SRTT, 10 paired runs per grammar (the same streams in every condition), final output only.
- **Measures:** normalized learning (same score as all earlier themes), and general damage = extra loss on 25
  held-out Wikipedia texts.
- **Key comparison:** learning against general damage, one line per layer. Layers are compared at the same damage
  (`DAMAGE_LEVEL`), so a layer that loses much learning for little general damage is specifically important for
  in-context learning.

## Code
- [`code/noise_robustness.ipynb`](code/noise_robustness.ipynb): the notebook, with plain-language explanations
  before every section. [Open in Colab](https://colab.research.google.com/github/DorRegev/Plasticity-vs-Learning/blob/main/04_noise_robustness/code/noise_robustness.ipynb)
  - Colab T4, 8-bit model, about **3.5 hours**. Every finished condition is saved to Google Drive
    (`MyDrive/plasticity_lens_cache/noise_robustness`); after a disconnect: reconnect, **Run all**, approve the
    Drive popup, and it continues where it stopped.

## Testing before the GPU run
Run end to end on CPU with a tiny random Mistral: all conditions, caching and resuming, and every plot. Built-in
sanity checks: α = 0 changes nothing; the noise has exactly relative size α at the chosen layer; BOS and all earlier
layers are untouched; the same input always gets the same noise.

## Results
To be added after the run.
