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

- [`code/noise_robustness_executed.ipynb`](code/noise_robustness_executed.ipynb) and
  [`code/noise_robustness_executed.html`](code/noise_robustness_executed.html): the full run (2026-11-08; Colab T4,
  8-bit model, 10 runs per grammar).

## Testing before the GPU run
Run end to end on CPU with a tiny random Mistral: all conditions, caching and resuming, and every plot. Built-in
sanity checks: α = 0 changes nothing; the noise has exactly relative size α at the chosen layer; BOS and all earlier
layers are untouched; the same input always gets the same noise.

## Results (run of 2026-11-08)
- **The model is very robust to small noise.** Up to α = 0.2 (a 20% push on every word's state) nothing changes at any
  layer: neither the learning nor the Wikipedia loss.
- **SRTT survives everything.** Its learning stays at 0.985–0.997 in every condition. Copying a fixed sequence is not
  disturbed by this kind of noise.
- **AGL: noise just before the jump hurts the learning most, noise after the jump does not hurt it at all.**

| Lens layer with noise α = 0.8 | 10 | 13 | 15 | **17** | **18** | 19 | 20 | 22 | 25 | 28 |
|---|---|---|---|---|---|---|---|---|---|---|
| AGL learning (no noise: 0.752) | 0.683 | 0.735 | 0.656 | **0.609** | **0.611** | 0.720 | 0.748 | 0.748 | 0.770 | 0.745 |
| extra Wikipedia loss (nats) | 0.074 | 0.079 | 0.071 | 0.092 | 0.115 | 0.138 | 0.186 | 0.245 | 0.251 | 0.182 |

- **A double dissociation.** Noise at layers 17–18 removes ~19% of the AGL learning while costing only ~0.1 nats on
  Wikipedia. Noise at layers 20–28 costs about twice as much on Wikipedia (0.18–0.25 nats) and removes none of the
  learning. At the same general damage (0.05 nats), AGL learning left is 0.68–0.69 for layers 15–18 versus
  0.74–0.76 for layers 19–28.
- **Reading:** the state just before the jump, which the induction heads in blocks 18–19 read the earlier words from,
  is the fragile part for in-context learning. Once the jump has happened (lens layer 19 is intermediate: 0.720),
  the learned prediction survives noise that hurts general language modelling more. This confirms, with a third
  independent method, that the in-context computation happens at the jump.
- Caveats: 10 paired runs per grammar (level SE ≈ 0.016, but conditions share the same streams, so differences are
  more precise); random noise mostly points in directions the model does not use, so compare layers, not absolute
  α values. Layer 13 (the small step) is surprisingly robust (0.735 at α = 0.8); with this design that is not
  interpretable on its own.
