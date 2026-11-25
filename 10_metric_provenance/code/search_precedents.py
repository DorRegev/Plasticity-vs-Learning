"""Part B candidate search: which published papers might use the same metrics as ours?

Three sources of candidates, all screened by title + abstract only (the full-text check is done
afterwards, see find_quotes.py and results/report.md):
  1. Semantic Scholar keyword searches, a few per metric (QUERIES below).
  2. Citation trails: every paper citing the Part A papers that were not anchors in
     09_literature_search (Wang 2022, Meng 2022, Geva 2023, Belrose 2023, Bansal 2023).
  3. The 2,831 papers of 09_literature_search/results/all_papers.csv.

Every candidate is scored per metric by the number of that metric's regex patterns matching its
title + abstract. Output: results/candidates.csv (all candidates with a hit) and
results/candidates_top.md (top 15 per metric). This is a screening list, not a judgment.

Uses the Semantic Scholar client of 09_literature_search (same retry/backoff, 1.1 s between
requests when S2_API_KEY is set) with its own cache in results/cache/s2/ (not committed).

    S2_API_KEY=... python 10_metric_provenance/code/search_precedents.py
"""
import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULTS = HERE.parent / "results"
sys.path.insert(0, str(ROOT / "09_literature_search" / "code"))
import lit_search  # noqa: E402

lit_search.CACHE = RESULTS / "cache" / "s2"
csv.field_size_limit(10**8)

TRAILS = {
    "Wang et al. 2022": "ARXIV:2211.00593",
    "Meng et al. 2022": "ARXIV:2202.05262",
    "Geva et al. 2023": "ARXIV:2304.14767",
    "Belrose et al. 2023": "ARXIV:2303.08112",
    "Bansal et al. 2023": "ARXIV:2212.09095",
}

QUERIES = {
    "B1": ["logit lens label words probability", "probability normalized over label words in-context learning",
           "restricted to answer options renormalized probability language model"],
    "B2": ["normalized gain pre post maximum", "human normalized score random baseline",
           "normalized logit difference activation patching", "fraction of performance recovered circuit"],
    "B3": ["copy score attention head unembedding", "copying score attention head direct path logits",
           "copy suppression attention head"],
    "B4": ["induction head score prefix matching copying", "identifying induction heads large language models"],
    "B5": ["gaussian noise intermediate layer residual stream robustness", "activation noise injection layer sensitivity language model",
           "perturbation residual stream layer equal KL divergence"],
    "B6": ["restoring attention heads ablated circuit recovery", "denoising activation patching", "path patching restore single head"],
    "B7": ["attention to previous occurrences in-context markov chain statistical induction head",
           "attention weights grouped by token category syntactic relation heads"],
    "B8": ["attention knockout most recent occurrence", "recency bias induction heads in-context",
           "block attention to earlier occurrences in-context learning"],
}

# Regexes on title + abstract (case-insensitive, word start). Deliberately broad: this is a screen.
PATTERNS = {
    "B1": [r"logit lens", r"label (word|token|space)s?", r"renormali[sz]", r"answer (option|choice)s?", r"calibrat"],
    "B2": [r"normali[sz]ed (gain|score|metric|logit)", r"human[- ]normali[sz]ed", r"(fraction|proportion|percentage) of .{0,40}(recover|restor)",
           r"upper bound", r"min[- ]max"],
    "B3": [r"copy(ing)? scor", r"copy suppression", r"unembedd", r"direct (logit|path|effect)", r"OV circuit"],
    "B4": [r"induction head", r"prefix[- ]matching", r"copying"],
    "B5": [r"gaussian noise", r"noise injection", r"inject(ed|ing)? noise", r"perturb", r"intermediate layer", r"robustness .{0,30}layer"],
    "B6": [r"restor", r"denois", r"activation patching", r"path patching", r"causal (tracing|mediation)", r"ablat"],
    "B7": [r"attention (pattern|weight|distribution)s?", r"statistical induction", r"previous occurrence", r"markov chain", r"n-gram"],
    "B8": [r"attention knockout", r"knock(ing)? ?out", r"recen(cy|t)", r"most recent", r"block(ing)? attention"],
}
COMPILED = {m: [re.compile(r"(?<![a-z0-9])" + p, re.I) for p in ps] for m, ps in PATTERNS.items()}


def main():
    client = lit_search.Client()
    papers = {}  # paperId -> dict(title, year, venue, url, abstract, sources:set)

    def add(p, source):
        if not p or not p.get("paperId") or not p.get("title"):
            return
        e = papers.setdefault(p["paperId"], {"title": p["title"], "year": p.get("year"), "venue": p.get("venue") or "",
                                             "url": p.get("url") or "", "abstract": p.get("abstract") or "",
                                             "arxiv": (p.get("externalIds") or {}).get("ArXiv") or "", "sources": set()})
        e["sources"].add(source)

    for metric, qs in QUERIES.items():
        for q in qs:
            res = client.get("/paper/search", {"query": q, "limit": 50, "fields": lit_search.PAPER_FIELDS})
            n = 0
            for p in (res or {}).get("data", []):
                add(p, f"search {metric}: {q}")
                n += 1
            print(f"  [{metric}] '{q}': {n}")
    for label, pid in TRAILS.items():
        cites = lit_search.fetch_citations(client, pid)
        for p in cites:
            add(p, f"cites {label}")
        print(f"  citations of {label}: {len(cites)}")
    with open(ROOT / "09_literature_search" / "results" / "all_papers.csv", newline="") as f:
        n09 = 0
        for row in csv.DictReader(f):
            add({"paperId": row["paperId"], "title": row["title"], "year": int(row["year"]) if row["year"] else None,
                 "venue": row["venue"], "url": row["url"], "abstract": row["abstract"],
                 "externalIds": {"ArXiv": row["arxiv"]}}, "09 list")
            n09 += 1
        print(f"  09 list: {n09}")

    rows = []
    for pid, e in papers.items():
        text = f"{e['title']} {e['abstract']}"
        hits = {m: [p.pattern.replace('(?<![a-z0-9])', '') for p in ps if p.search(text)] for m, ps in COMPILED.items()}
        found_by = {m for m in QUERIES if any(s.startswith(f"search {m}:") for s in e["sources"])}
        for m in QUERIES:
            score = len(hits[m]) + (1 if m in found_by else 0)
            if hits[m] or m in found_by:
                rows.append({"metric": m, "score": score, "paperId": pid, "title": e["title"], "year": e["year"] or "",
                             "venue": e["venue"], "arxiv": e["arxiv"], "url": e["url"], "hits": "; ".join(hits[m]),
                             "no_abstract": not e["abstract"], "sources": " | ".join(sorted(e["sources"]))})
    rows.sort(key=lambda r: (r["metric"], -r["score"], -(r["year"] or 0), r["title"], r["paperId"]))
    out = RESULTS / "candidates.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with open(RESULTS / "candidates_top.md", "w") as f:
        f.write("# Part B screening: top 15 candidates per metric (title + abstract only)\n\n"
                f"{len(papers)} unique papers screened. Generated by `code/search_precedents.py`. "
                "A high score means only that the abstract uses related words; see report.md for the full-text check.\n")
        for m in QUERIES:
            sub = [r for r in rows if r["metric"] == m][:15]
            f.write(f"\n## {m}\n\n| Score | Title | Year | Hits |\n|---|---|---|---|\n")
            for r in sub:
                t = r["title"].replace("|", "\\|")
                f.write(f"| {r['score']} | [{t}]({r['url']}) | {r['year']} | {r['hits']} |\n")
    print(f"done: {len(papers)} unique papers, {len(rows)} metric-candidate rows -> {out}")


if __name__ == "__main__":
    main()
