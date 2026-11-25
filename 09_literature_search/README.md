# 09 · Related-work search

A reproducible search for related work for the paper (a frozen Mistral-7B learning AGL and SRTT grammars in context;
induction-head ablation; "SRTT copies, AGL counts"). It uses the
[Semantic Scholar Graph API](https://api.semanticscholar.org/api-docs/graph). It only collects and keyword-scores
papers; reading and judging them is done by hand from the shortlist.

## What it does
1. **Anchors.** Resolves 10 anchor papers (by arXiv id or DOI) to Semantic Scholar ids and prints a check table. The
   table compares each resolved title with the expected one and flags any mismatch.
   - Olsson et al. 2022
   - Crosbie & Shutova 2025
   - Yin & Steinhardt 2025
   - Akyürek et al. 2024
   - Edelman et al. 2024
   - Todd et al. 2024
   - Wu et al. (Retrieval Heads)
   - Ma & Xu 2025
   - Saanum et al. 2025
   - Lior, Shalev, Stanovsky & Goldstein 2024 (our base paper)
2. **Forward citations.** Fetches every paper citing each anchor, with full pagination.
3. **Keyword search.** 11 queries, top 100 results each, years 2019 onward (listed in `code/lit_search.py`).
4. **Merge.** Deduplicates by paperId, then DOI, then arXiv id, then normalized title. For each paper it records which
   anchors it cites and which queries found it.
5. **Score.** Case-insensitive keyword matching on title + abstract. Each keyword must start at a word boundary:
   "AGL" does not match "fragile", while "ablat" matches "ablation".
   - TASK keywords: artificial grammar, AGL, Reber, finite-state, finite automat, regular language, formal language,
     serial reaction, SRTT, statistical learning, implicit learning, Markov chain, sequence learning, n-gram.
   - MECH keywords: attention head, induction head, ablat, knockout, circuit, mechanis, interpretab, function vector,
     retrieval head, activation patching.
   - Score = 2·[any TASK] + 2·[any MECH] + (number of anchors cited, at most 3) + [year ≥ 2025].
   - **TOP** = both TASK and MECH hits.
   - Papers without an abstract are kept, scored from the title only, and marked `no_abstract`.
6. **Outputs** in `results/`:
   - `all_papers.csv`: every unique paper, with all fields, the score, the flags, the anchors cited and the queries
     that found it.
   - `shortlist.md`: score ≥ 5 or TOP, sorted by score, then year.
   - `summary.md`: counts, unresolved anchors and the run date.

## How to rerun
```bash
pip install requests
export S2_API_KEY=...        # optional: a Semantic Scholar API key; read from the environment only, never saved
python 09_literature_search/code/lit_search.py            # reuses cached responses
python 09_literature_search/code/lit_search.py --refresh  # asks the API again (picks up new papers)
python 09_literature_search/code/lit_search.py --max-retries 30   # more patience when the public pool is busy
```
- **Without a key** the script shares Semantic Scholar's public rate limit, which can refuse most requests for a while.
  If it still gets 429 after all retries, it stops with a message. Everything fetched so far stays cached, so running
  it again continues where it stopped.
- **Cache.** Every raw API response is cached as JSON in `results/cache/`. The cache is git-ignored, so a rerun on the
  same machine makes no requests.
- **Rate limits.** There is a 1.5 s pause between requests (1.1 s with a key). Responses 429 and 5xx are retried with
  exponential backoff: 2, 4, 8 … up to 120 s, at most 8 times.
- **Determinism.** The output is fully sorted. With the same cache the outputs are identical; new papers appear only
  after `--refresh` or when the cache is deleted.

## Last run
2026-11-25: 2,831 unique papers; shortlist 213 (67 TOP). Run with an API key. See `results/summary.md` for the full counts.
