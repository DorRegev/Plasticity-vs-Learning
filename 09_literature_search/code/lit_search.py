#!/usr/bin/env python3
"""Reproducible related-work search with the Semantic Scholar Graph API.

Steps: resolve the anchor papers -> fetch every paper citing them -> keyword searches -> merge and deduplicate ->
keyword relevance score -> results/all_papers.csv, results/shortlist.md, results/summary.md.

Raw API responses are cached in results/cache/ (one JSON file per request), so a rerun only asks for what is not
cached. Delete the cache (or pass --refresh) to pick up new papers.

Usage:  python 09_literature_search/code/lit_search.py [--refresh] [--date YYYY-MM-DD]
Optional API key: environment variable S2_API_KEY (sent as the x-api-key header; never written to disk).
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import re
import sys
import time
import unicodedata
from pathlib import Path

import requests

API = "https://api.semanticscholar.org/graph/v1"
HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
CACHE = RESULTS / "cache"

PAPER_FIELDS = "paperId,title,abstract,year,venue,authors,externalIds,citationCount,url"
SEARCH_YEARS = "2019-"
SEARCH_LIMIT = 100
CITATION_PAGE = 1000          # the API's maximum page size for /citations
SLEEP_NO_KEY = 1.5            # seconds between uncached requests (shared public rate limit)
SLEEP_WITH_KEY = 1.1          # keyed limit: 1 request per second
MAX_RETRIES = 8

ANCHORS = [  # (label, Semantic Scholar id, expected first words of the title, for the check table)
    ("Olsson et al. 2022", "ARXIV:2209.11895", "In-context Learning and Induction Heads"),
    ("Crosbie & Shutova 2025", "ARXIV:2407.07011", "Induction Heads as an Essential Mechanism"),
    ("Yin & Steinhardt 2025", "ARXIV:2502.14010", "Which Attention Heads Matter"),
    ("Akyurek et al. 2024", "ARXIV:2401.12973", "In-Context Language Learning"),
    ("Edelman et al. 2024", "ARXIV:2402.11004", "The Evolution of Statistical Induction Heads"),
    ("Todd et al. 2024", "ARXIV:2310.15213", "Function Vectors"),
    ("Wu et al. (Retrieval Heads)", "ARXIV:2404.15574", "Retrieval Head"),
    ("Ma & Xu 2025", "ARXIV:2503.24190", "Implicit In-context Learning"),
    ("Saanum et al. 2025", "ARXIV:2509.21534", "A circuit for predicting hierarchical structure"),
    ("Lior, Shalev, Stanovsky & Goldstein 2024", "DOI:10.1101/2024.03.07.583890", "Computation or Weight Adaptation"),
]

QUERIES = [
    "artificial grammar learning language model",
    "Reber grammar transformer",
    "serial reaction time task language model",
    "statistical learning large language model",
    "in-context learning regular languages",
    "in-context learning Markov chains",
    "induction heads ablation in-context learning",
    "attention head ablation in-context learning",
    "n-gram heads",
    "implicit learning large language models",
    "formal language learning in-context LLM",
]

TASK_KEYWORDS = ["artificial grammar", "AGL", "Reber", "finite-state", "finite automat", "regular language",
                 "formal language", "serial reaction", "SRTT", "statistical learning", "implicit learning",
                 "Markov chain", "sequence learning", "n-gram"]
MECH_KEYWORDS = ["attention head", "induction head", "ablat", "knockout", "circuit", "mechanis", "interpretab",
                 "function vector", "retrieval head", "activation patching"]


# ---------------------------------------------------------------------------------------------- API with cache
class Client:
    def __init__(self, refresh=False):
        self.key = os.environ.get("S2_API_KEY") or None
        self.sleep = SLEEP_WITH_KEY if self.key else SLEEP_NO_KEY
        self.refresh = refresh
        self.session = requests.Session()
        self.calls = 0
        self.cache_hits = 0
        self._last = 0.0
        CACHE.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _cache_path(path, params):
        key = json.dumps([path, sorted((params or {}).items())], sort_keys=True)
        return CACHE / (hashlib.sha1(key.encode()).hexdigest() + ".json")

    def get(self, path, params=None):
        """GET API + path. Returns the JSON body, or None for a 404. Cached on disk (404s too)."""
        cache_file = self._cache_path(path, params)
        if cache_file.exists() and not self.refresh:
            self.cache_hits += 1
            body = json.loads(cache_file.read_text())
            return None if body.get("_status") == 404 else body
        headers = {"x-api-key": self.key} if self.key else {}
        for attempt in range(MAX_RETRIES + 1):
            wait = self.sleep - (time.time() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.time()
            self.calls += 1
            try:
                r = self.session.get(API + path, params=params, headers=headers, timeout=60)
            except requests.RequestException as error:
                status, r = f"network error: {error}", None
            else:
                status = r.status_code
            if r is not None and r.status_code == 200:
                body = r.json()
                cache_file.write_text(json.dumps({"_path": path, "_params": params, **body}, sort_keys=True))
                return body
            if r is not None and r.status_code == 404:
                cache_file.write_text(json.dumps({"_status": 404, "_path": path, "_params": params}))
                return None
            if r is not None and r.status_code not in (429,) and r.status_code < 500:
                raise RuntimeError(f"{path} {params}: HTTP {r.status_code}: {r.text[:300]}")
            backoff = min(2 ** attempt * 2, 120)
            print(f"  [{status}] {path} - retry {attempt + 1}/{MAX_RETRIES} in {backoff}s", file=sys.stderr)
            time.sleep(backoff)
        raise RuntimeError(f"{path} {params}: gave up after {MAX_RETRIES} retries")


# ---------------------------------------------------------------------------------------------- steps
def resolve_anchors(client):
    resolved, failed = [], []
    for label, ident, expected in ANCHORS:
        body = client.get(f"/paper/{ident}", {"fields": "paperId,title,year,venue,externalIds,citationCount"})
        if body is None or not body.get("paperId"):
            failed.append((label, ident))
            continue
        title = body.get("title") or ""
        ok = expected.lower() in title.lower()
        resolved.append({"label": label, "id": ident, "paperId": body["paperId"], "title": title, "year": body.get("year"),
                         "citationCount": body.get("citationCount"), "title_matches": ok})
    return resolved, failed


def fetch_citations(client, paper_id):
    papers, offset = [], 0
    while True:
        body = client.get(f"/paper/{paper_id}/citations", {"fields": PAPER_FIELDS, "limit": CITATION_PAGE, "offset": offset})
        if body is None:
            break
        papers += [item["citingPaper"] for item in body.get("data", []) if item.get("citingPaper", {}).get("paperId")]
        if body.get("next") is None:
            break
        offset = body["next"]
    return papers


def keyword_search(client, query):
    body = client.get("/paper/search", {"query": query, "fields": PAPER_FIELDS, "limit": SEARCH_LIMIT, "offset": 0,
                                        "year": SEARCH_YEARS})
    return [p for p in (body or {}).get("data", []) if p.get("paperId")]


# ---------------------------------------------------------------------------------------------- merge + score
def normalize_title(title):
    title = unicodedata.normalize("NFKD", title or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", title).strip()


def merge(records):
    """records: list of (paper dict, anchor label or None, query or None). Deduplicates by paperId, then DOI/arXiv id,
    then normalized title (union-find). Returns {canonical paperId: merged paper}."""
    by_id = {}
    for paper, anchor, query in records:
        entry = by_id.setdefault(paper["paperId"], {"paper": paper, "anchors": set(), "queries": set()})
        if not entry["paper"].get("abstract") and paper.get("abstract"):
            entry["paper"] = paper
        if anchor:
            entry["anchors"].add(anchor)
        if query:
            entry["queries"].add(query)
    parent = {pid: pid for pid in by_id}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for key_fn in (lambda p: ("doi", ((p.get("externalIds") or {}).get("DOI") or "").lower()),
                   lambda p: ("arxiv", ((p.get("externalIds") or {}).get("ArXiv") or "").lower()),
                   lambda p: ("title", normalize_title(p.get("title")))):
        seen = {}
        for pid in sorted(by_id):
            kind, value = key_fn(by_id[pid]["paper"])
            if not value or (kind == "title" and len(value) < 20):
                continue
            if (kind, value) in seen:
                a, b = find(seen[(kind, value)]), find(pid)
                if a != b:
                    parent[max(a, b)] = min(a, b)
            else:
                seen[(kind, value)] = pid
    merged = {}
    for pid in sorted(by_id):
        root = find(pid)
        entry = by_id[pid]
        if root not in merged:
            merged[root] = {"paper": dict(by_id[root]["paper"]), "anchors": set(), "queries": set(), "merged_ids": set()}
        m = merged[root]
        m["anchors"] |= entry["anchors"]
        m["queries"] |= entry["queries"]
        if pid != root:
            m["merged_ids"].add(pid)
        if not m["paper"].get("abstract") and entry["paper"].get("abstract"):
            m["paper"]["abstract"] = entry["paper"]["abstract"]
    return merged


def compile_keywords(words):
    # word boundary at the start (stems like "ablat" match "ablation"); case-insensitive
    return [(w, re.compile(r"(?<![a-z0-9])" + re.escape(w.lower()))) for w in words]


TASK_RE, MECH_RE = compile_keywords(TASK_KEYWORDS), compile_keywords(MECH_KEYWORDS)


def score(entry):
    p = entry["paper"]
    text = f"{p.get('title') or ''} {p.get('abstract') or ''}".lower()
    task = [w for w, rx in TASK_RE if rx.search(text)]
    mech = [w for w, rx in MECH_RE if rx.search(text)]
    year = p.get("year") or 0
    value = 2 * bool(task) + 2 * bool(mech) + min(len(entry["anchors"]), 3) + (1 if year >= 2025 else 0)
    return value, task, mech


def first_sentences(text, n=2):
    if not text:
        return ""
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", " ".join(text.split()))
    return " ".join(parts[:n])


def md_cell(text):
    return (text or "").replace("|", "\\|").replace("\n", " ")


# ---------------------------------------------------------------------------------------------- main
def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--refresh", action="store_true", help="ignore the cache and ask the API again")
    parser.add_argument("--date", default=dt.date.today().isoformat(), help="run date written to summary.md")
    args = parser.parse_args()
    client = Client(refresh=args.refresh)
    RESULTS.mkdir(parents=True, exist_ok=True)

    print("Step 1: anchors")
    anchors, failed = resolve_anchors(client)
    print(f"{'anchor':42} {'id':32} {'paperId':42} {'year':5} {'cites':>6}  title (check)")
    for a in anchors:
        flag = "" if a["title_matches"] else "   <-- CHECK: title differs from the expected one"
        print(f"{a['label'][:42]:42} {a['id']:32} {a['paperId']:42} {str(a['year']):5} {str(a['citationCount']):>6}  {a['title'][:70]}{flag}")
    for label, ident in failed:
        print(f"{label[:42]:42} {ident:32} NOT RESOLVED")

    print("Step 2: forward citations")
    records, citation_counts = [], {}
    for a in anchors:
        citing = fetch_citations(client, a["paperId"])
        citation_counts[a["label"]] = (len(citing), a["citationCount"])
        print(f"  {a['label']}: {len(citing)} citing papers (Semantic Scholar count: {a['citationCount']})")
        records += [(p, a["label"], None) for p in citing]

    print("Step 3: keyword search")
    query_counts = {}
    for q in QUERIES:
        hits = keyword_search(client, q)
        query_counts[q] = len(hits)
        print(f"  {q!r}: {len(hits)} results")
        records += [(p, None, q) for p in hits]

    print("Step 4: merge and deduplicate")
    merged = merge(records)
    anchor_ids = {a["paperId"]: a["label"] for a in anchors}

    print("Step 5: score")
    rows = []
    for pid, entry in merged.items():
        p = entry["paper"]
        value, task, mech = score(entry)
        ext = p.get("externalIds") or {}
        rows.append({
            "paperId": pid, "title": p.get("title") or "", "year": p.get("year") or "", "venue": p.get("venue") or "",
            "authors": "; ".join(a.get("name", "") for a in (p.get("authors") or [])),
            "doi": ext.get("DOI", ""), "arxiv": ext.get("ArXiv", ""), "citationCount": p.get("citationCount") or 0,
            "url": p.get("url") or f"https://www.semanticscholar.org/paper/{pid}",
            "score": value, "TOP": bool(task and mech), "no_abstract": not p.get("abstract"),
            "is_anchor": anchor_ids.get(pid, ""), "task_hits": "; ".join(task), "mech_hits": "; ".join(mech),
            "n_anchors_cited": len(entry["anchors"]), "anchors_cited": "; ".join(sorted(entry["anchors"])),
            "queries": "; ".join(sorted(entry["queries"])), "merged_ids": "; ".join(sorted(entry["merged_ids"])),
            "abstract": " ".join((p.get("abstract") or "").split()),
        })
    rows.sort(key=lambda r: (-r["score"], -(r["year"] or 0), r["title"].lower(), r["paperId"]))

    print("Step 6: outputs")
    with open(RESULTS / "all_papers.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["paperId"])
        writer.writeheader()
        writer.writerows(rows)

    shortlist = [r for r in rows if r["score"] >= 5 or r["TOP"]]
    lines = ["# Shortlist", "",
             f"Papers with score >= 5 or flagged TOP (TASK and MECH keywords both present), sorted by score, then year. "
             f"{len(shortlist)} papers. Generated by `code/lit_search.py`; see `summary.md` for the run date.", "",
             "| # | Title | Year | Venue | Score | Why | Abstract (first 2 sentences) |", "|---|---|---|---|---|---|---|"]
    for i, r in enumerate(shortlist, 1):
        why = []
        if r["TOP"]:
            why.append("**TOP**")
        if r["task_hits"]:
            why.append("TASK: " + r["task_hits"])
        if r["mech_hits"]:
            why.append("MECH: " + r["mech_hits"])
        if r["anchors_cited"]:
            why.append("cites: " + r["anchors_cited"])
        if r["queries"]:
            why.append("queries: " + r["queries"])
        if r["no_abstract"]:
            why.append("no_abstract")
        if r["is_anchor"]:
            why.append("anchor")
        lines.append(f"| {i} | [{md_cell(r['title'])}]({r['url']}) | {r['year']} | {md_cell(r['venue'])} | {r['score']} | "
                     f"{md_cell('; '.join(why))} | {md_cell(first_sentences(r['abstract']))} |")
    (RESULTS / "shortlist.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = ["# Literature search summary", "", f"- Run date: {args.date}",
               f"- API requests this run: {client.calls} (cached responses used: {client.cache_hits}); API key used: {'yes' if client.key else 'no'}",
               f"- Unique papers after deduplication: {len(rows)}",
               f"- Shortlist (score >= 5 or TOP): {len(shortlist)}; TOP: {sum(r['TOP'] for r in rows)}; "
               f"without abstract: {sum(r['no_abstract'] for r in rows)}", "",
               "## Anchors", "", "| Anchor | Id | Resolved title | Year | Citing papers fetched | Semantic Scholar citation count |",
               "|---|---|---|---|---|---|"]
    for a in anchors:
        fetched, reported = citation_counts[a["label"]]
        check = "" if a["title_matches"] else " (CHECK: title differs from the expected one)"
        summary.append(f"| {a['label']} | {a['id']} | [{md_cell(a['title'])}](https://www.semanticscholar.org/paper/{a['paperId']}){check} | "
                       f"{a['year']} | {fetched} | {reported} |")
    summary += ["", "Anchors that failed to resolve: " + (", ".join(f"{l} ({i})" for l, i in failed) if failed else "none"), "",
                "## Keyword searches (top 100 each, years 2019 onward)", "", "| Query | Results |", "|---|---|"]
    summary += [f"| {q} | {n} |" for q, n in query_counts.items()]
    (RESULTS / "summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print(f"done: {len(rows)} unique papers, {len(shortlist)} on the shortlist -> {RESULTS}")


if __name__ == "__main__":
    main()
