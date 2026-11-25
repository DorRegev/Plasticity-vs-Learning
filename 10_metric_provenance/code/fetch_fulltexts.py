"""Download the full texts used in the provenance report and convert them to plain text.

Usage:
    python 10_metric_provenance/code/fetch_fulltexts.py            # every source in SOURCES
    python 10_metric_provenance/code/fetch_fulltexts.py olsson2022 # only the named keys

Each source is downloaded once into results/cache/raw/ (not committed) and converted into
results/cache/text/<key>.txt (layout kept) and, for PDFs, <key>.reading.txt (reading order). PDFs are converted page by page with `pdftotext -layout`; pages are
separated by a line "=== PAGE n ===", so every quote in the report can give its page. HTML pages are
reduced to text with the same "=== PAGE 1 ===" header (they have no pages; the report then cites
the section heading instead).

At most one request per second, with exponential backoff on 429/5xx. The User-Agent names no person.
"""
import html
import re
import subprocess
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
CACHE = HERE.parent / "results" / "cache"
RAW = CACHE / "raw"
TEXT = CACHE / "text"
UA = "Mozilla/5.0 (compatible; metric-provenance-script/1.0)"
MIN_GAP = 1.1
_last = [0.0]

# key -> (url, kind). arXiv PDFs are the latest version at the time of the run (the version is
# recorded by arxiv_versions() into results/sources.tsv).
SOURCES = {
    # Part A
    # Lior et al.: v1 (2024-03-07) and v4 (2026-10-12, the latest version at the time of the run)
    "lior2024": ("https://www.biorxiv.org/content/10.1101/2024.03.07.583890v1.full.pdf", "pdf"),
    "lior2024v4": ("https://www.biorxiv.org/content/10.1101/2024.03.07.583890v4.full.pdf", "pdf"),
    "logitlens2020": ("https://www.lesswrong.com/posts/AcKRB8wDpdaN6v6ru/interpreting-gpt-the-logit-lens", "html"),
    "belrose2023": ("https://arxiv.org/pdf/2303.08112", "pdf"),
    "olsson2022": ("https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads/index.html", "html"),
    "bansal2023": ("https://arxiv.org/pdf/2212.09095", "pdf"),
    "wang2022": ("https://arxiv.org/pdf/2211.00593", "pdf"),
    "crosbie2025": ("https://arxiv.org/pdf/2407.07011", "pdf"),
    "meng2022": ("https://arxiv.org/pdf/2202.05262", "pdf"),
    "geva2023": ("https://arxiv.org/pdf/2304.14767", "pdf"),
    # Part B: candidate precedents (arXiv ids checked against the downloaded title page)
    "halawi2023": ("https://arxiv.org/pdf/2307.09476", "pdf"),
    "zhao2021": ("https://arxiv.org/pdf/2102.09690", "pdf"),
    "heimersheim2024": ("https://arxiv.org/pdf/2404.15255", "pdf"),
    "zhang2023": ("https://arxiv.org/pdf/2309.16042", "pdf"),
    "badia2020": ("https://arxiv.org/pdf/2003.13350", "pdf"),
    "mcdougall2023": ("https://arxiv.org/pdf/2310.04625", "pdf"),
    "gould2023": ("https://arxiv.org/pdf/2312.09230", "pdf"),
    "edelman2024": ("https://arxiv.org/pdf/2402.11004", "pdf"),
    "akyurek2024": ("https://arxiv.org/pdf/2401.12973", "pdf"),
    "singh2024": ("https://arxiv.org/pdf/2404.07129", "pdf"),
    "lad2024": ("https://arxiv.org/pdf/2406.19384", "pdf"),
    "clark2019": ("https://arxiv.org/pdf/1906.04341", "pdf"),
    "conmy2023": ("https://arxiv.org/pdf/2304.14997", "pdf"),
    "yin2025": ("https://arxiv.org/pdf/2502.14010", "pdf"),
    "todd2023": ("https://arxiv.org/pdf/2310.15213", "pdf"),
    "wu2024": ("https://arxiv.org/pdf/2404.15574", "pdf"),
    "michel2019": ("https://arxiv.org/pdf/1905.10650", "pdf"),
    "saanum2025": ("https://arxiv.org/pdf/2509.21534", "pdf"),
    "maxu2025": ("https://arxiv.org/pdf/2503.24190", "pdf"),
    "ren2024": ("https://arxiv.org/pdf/2402.13055", "pdf"),
    # Part B: candidates surfaced by search_precedents.py (screened by title/abstract, then read)
    "copyrep2026": ("https://arxiv.org/pdf/2610.26722", "pdf"),
    "matchedcompute2025": ("https://arxiv.org/pdf/2509.22947", "pdf"),
    "feucht2025": ("https://arxiv.org/pdf/2504.03022", "pdf"),
    "geominv2026": ("https://arxiv.org/pdf/2611.12206", "pdf"),
    "selective2025": ("https://arxiv.org/pdf/2509.08184", "pdf"),
    "sensitivity2026": ("https://arxiv.org/pdf/2608.03842", "pdf"),
    "stochln2026": ("https://arxiv.org/pdf/2608.30720", "pdf"),
    "iclcircuit2026": ("https://arxiv.org/pdf/2611.05344", "pdf"),
    "synthctx2024": ("https://arxiv.org/pdf/2410.22316", "pdf"),
    "logitcontrib2026": ("https://arxiv.org/pdf/2607.01002", "pdf"),
    "interpngram2026": ("https://arxiv.org/pdf/2607.02800", "pdf"),
    "prepost2022": ("https://arxiv.org/pdf/2210.01823", "pdf"),
}


def polite_get(url, tries=8):
    for attempt in range(tries):
        wait = MIN_GAP - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=60, allow_redirects=True)
        except requests.RequestException as e:
            r, err = None, str(e)
        if r is not None and r.status_code == 200:
            return r
        status = r.status_code if r is not None else err
        if r is not None and r.status_code < 500 and r.status_code != 429:
            raise RuntimeError(f"{url}: HTTP {status}")
        delay = min(2 ** attempt * 2, 120)
        print(f"  [{status}] {url} - retry {attempt + 1}/{tries} in {delay}s", flush=True)
        time.sleep(delay)
    raise RuntimeError(f"{url}: gave up after {tries} tries")


def html_to_text(raw):
    raw = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", raw)
    raw = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</h[1-6]>|</li>|</tr>", "\n", raw)
    raw = re.sub(r"(?i)<h([1-6])[^>]*>", lambda m: "\n\n" + "#" * int(m.group(1)) + " ", raw)
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = html.unescape(raw)
    raw = re.sub(r"[ \t\xa0]+", " ", raw)
    raw = re.sub(r"\n\s*\n+", "\n\n", raw)
    return raw.strip()


def pdf_to_text(path, layout=True):
    args = ["pdftotext"] + (["-layout"] if layout else []) + [str(path), "-"]
    out = subprocess.run(args, capture_output=True, text=True, check=True).stdout
    pages = out.split("\f")
    return "\n".join(f"=== PAGE {i + 1} ===\n{p}" for i, p in enumerate(pages) if p.strip())


def fetch(key, url, kind):
    RAW.mkdir(parents=True, exist_ok=True)
    TEXT.mkdir(parents=True, exist_ok=True)
    raw_path = RAW / f"{key}.{kind}"
    txt_path = TEXT / f"{key}.txt"
    if not raw_path.exists():
        r = polite_get(url)
        if kind == "pdf" and not r.content.startswith(b"%PDF"):
            raise RuntimeError(f"{url}: not a PDF (got {r.headers.get('content-type')})")
        raw_path.write_bytes(r.content)
    if kind == "pdf":
        txt = pdf_to_text(raw_path)
        # reading-order version (two-column papers read column by column); used by find_quotes.py
        (TEXT / f"{key}.reading.txt").write_text(pdf_to_text(raw_path, layout=False))
    else:
        txt = "=== PAGE 1 ===\n" + html_to_text(raw_path.read_text(errors="replace"))
    txt_path.write_text(txt)
    return txt_path


def main(keys):
    failed = []
    for key in keys or SOURCES:
        url, kind = SOURCES[key]
        try:
            p = fetch(key, url, kind)
            print(f"ok   {key:16s} {p.stat().st_size:>9,d} chars  {url}")
        except Exception as e:  # noqa: BLE001 - report and continue
            failed.append(key)
            print(f"FAIL {key:16s} {e}")
    if failed:
        print("failed:", ", ".join(failed))


if __name__ == "__main__":
    main(sys.argv[1:])
