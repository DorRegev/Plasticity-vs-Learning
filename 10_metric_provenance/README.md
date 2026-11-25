# 10 · Metric provenance

**Question:**
- Do the sources we cite for our metrics say what we claim? This is checked against full texts, not abstracts (Part A).
- For the metrics we call "ours", is there a published precedent (Part B)?

This folder only reports. It changes no slides, docs or notebooks.

**The report:** [`results/report.md`](results/report.md). It has:
- a summary table (metric | status before | status after | key citation);
- Part A: a verdict, the correction, and quotes with page numbers for each claim;
- Part B: up to 5 precedents per metric, with closeness, the difference from ours, and a quote.

## Main results (run 2026-11-25)
- **Part A:** 5 of 7 claims are correct. Two are partly wrong:
  - **A2:** the original logit-lens post did not apply the final layer norm's learned affine part. Belrose et al.'s Eq. 3
    is the version we implement.
  - **A3:** Olsson et al.'s copying score is an empirical direct-path (unembedding) score; the OV eigenvalue score only
    validates it.
  - Also: neither Olsson nor Bansal uses a numeric threshold or combines the two scores. The "prefix ≥ 0.3" cut-offs in
    `03` / `08` are ours.
- **Part B:**

  | Status | Metrics |
  |---|---|
  | adapted | B1 renormalized readout, from Zhao et al. 2021 |
  | adapted | B2 learning score, a normalized-gain / human-normalized-score form |
  | adapted | B3 rank copying score, from Olsson 2022 and Wang 2022 |
  | adapted | B6 leave-one-in, from Wang 2022 "minimality" |
  | ours | B4 product score |
  | ours | B5 damage-matched layer noise |
  | ours | B7 reading map |
  | ours | B8 the recency split; its "all occurrences" condition is very similar to Crosbie & Shutova 2025 §4.4 |

## Code
| Script | What it does |
|---|---|
| [`code/fetch_fulltexts.py`](code/fetch_fulltexts.py) | Downloads the 43 full texts (arXiv, bioRxiv, transformer-circuits.pub, LessWrong) into `results/cache/`. Converts PDFs to text page by page (layout and reading order). At most 1 request per second, with backoff. |
| [`code/search_precedents.py`](code/search_precedents.py) | The Part B screen. Combines 23 Semantic Scholar searches, the citation trails of five Part A papers, and the 2,831 papers of `09_literature_search`. It writes `results/candidates.csv` and `results/candidates_top.md`, scored by title and abstract only. It reuses the `09` client: 1.1 s between requests with a key, backoff on 429 and 5xx. |
| [`code/find_quotes.py`](code/find_quotes.py) | Holds every quote used in the report. Checks that each appears verbatim in the full text (whitespace and line-break hyphens aside) and records its page. Writes `results/quotes.md` and `results/sources.md`, and fails if any quote is missing. |

## How to rerun
```
pip install requests             # pdftotext (poppler-utils) must be installed
export S2_API_KEY=...            # optional; without it Semantic Scholar often refuses searches
python 10_metric_provenance/code/fetch_fulltexts.py
python 10_metric_provenance/code/search_precedents.py
python 10_metric_provenance/code/find_quotes.py
```
- **Network:** the machine must reach api.semanticscholar.org, arxiv.org, www.biorxiv.org, transformer-circuits.pub and
  www.lesswrong.com.
- **Cache:** everything is cached in `results/cache/`, which is git-ignored (no PDFs or API responses are committed). Reruns
  are cheap and give the same outputs, except for new papers in the search.
- **Versions:** arXiv PDFs are fetched without a version number, so a rerun gets the latest version. `results/sources.md`
  records which version was read.

**Last run:** 2026-11-25. 86 of 86 quotes found; 8,040 unique papers screened.
