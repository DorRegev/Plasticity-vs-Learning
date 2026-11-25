"""Check that every quote used in results/report.md appears verbatim in the downloaded full text.

For each (id, source key, quote) in QUOTES the quote is searched, after collapsing whitespace and
undoing line-break hyphenation and ligatures, in results/cache/text/<key>.reading.txt (PDF reading
order) and <key>.txt (layout / HTML). The page is the "=== PAGE n ===" block it falls in (PDF page;
HTML sources have one page, and the report cites the section instead).

Writes results/quotes.md (id, source, page, found, quote) and results/sources.md (every downloaded
source with its URL and arXiv/bioRxiv version). Exits with an error if any quote is not found.

    python 10_metric_provenance/code/find_quotes.py
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
TEXT = RESULTS / "cache" / "text"
sys.path.insert(0, str(HERE))
from fetch_fulltexts import SOURCES  # noqa: E402

QUOTES = [
    # ---------- Part A ----------
    # A1 Lior et al. (v4 = latest; v1 checked for the same sentences)
    ("A1-a", "lior2024v4", "After each concatenation of a word, we extract the probability that the model assigns to the next word"),
    ("A1-b", "lior2024v4", "The improvement of the performance is defined by the increase in the probability that the LLM assigns to the correct next token."),
    ("A1-c", "lior2024v4", "Then, the theoretical upper bound for the sequence is the average of all transition probabilities between each pair of consecutive states"),
    ("A1-d", "lior2024v4", "The model reaches 92% of the SRTT upper bound and 79% of the AGL upper bound, averaging the last 1000 iterations of the structured part."),
    ("A1-e", "lior2024v4", "we compute the KL divergence between the model's predicted next-token distribution and the true transition probabilities at each state"),
    ("A1-f", "lior2024", "The model reaches 92% of the SRTT upper bound and 79% of the AGL upper bound, averaging the last 1000 iterations of the structured part."),
    ("A1-h", "lior2024v4", "this version posted October 12, 2026"),
    ("A1-i", "lior2024", "this version posted March 7, 2024"),
    ("A1-g", "lior2024v4", "the model assigns a probability for each word in its vocabulary to be the next word, and we extract the probability that the model assigns to the actual next input word"),
    # A2 logit lens / tuned lens
    ("A2-a", "logitlens2020", "We have a \"dictionary,\" W , that lets us convert between vocab space and embedding space at any point."),
    ("A2-b", "logitlens2020", "For transformer experts: the \"activations\" here are the block outputs after layer norm, but before the learned point-wise transformation."),
    ("A2-c", "belrose2023", "The logit lens consists of setting the residuals to zero: LogitLens(hℓ ) = LayerNorm[hℓ ]WU ."),
    ("A2-d", "belrose2023", "We train L affine transformations, one for each layer of the network, with a distillation loss: transform the hidden state so that its image under the unembedding matches the final layer logits as closely as possible."),
    ("A2-e", "belrose2023", "We refer to (Aℓ , bℓ ) as the translator for layer ℓ."),
    ("A2-f", "belrose2023", "We initialized all translators to the identity"),
    # A3 Olsson et al.
    ("A3-a", "olsson2022", "Prefix matching: Generate a sequence of 25 random tokens, excluding the most common and the least common tokens. Repeat this sequence 4 times and prepend a “start of sequence” token."),
    ("A3-b", "olsson2022", "The prefix matching score is the average of all attention pattern entries attending from a given token back to the tokens that preceded the same token in earlier repeats."),
    ("A3-c", "olsson2022", "That is, it attends to the token which induction would suggest comes next."),
    ("A3-d", "olsson2022", "Copying : Generate a sequence of 25 random tokens, excluding the most common and the least common tokens. Compute this head’s contribution to the residual stream, then convert that using the unembeddings (i.e. along the “direct path”) to impacts on each logit. Logits are transformed by subtracting the mean of the logits and passing through a ReLU, allowing the evaluator to focus on where logits are raised. Compute the ratio of the amount it raises the logits of the token being attended to, to that of all tokens in this sample. This value ranges from 0 (only raises other tokens) to 0.5 (only raises the present token), so we scale it into the range of -1 to 1."),
    ("A3-e", "olsson2022", "Our copying evaluator correlates well with the OV matrix of each head. Specifically here we plot against the sum of the eigenvalues, divided by the absolute value of the eigenvalues, which is a measure of what fraction of the eigenvalues are positive vs. negative."),
    ("A3-f", "olsson2022", "In more detail, each head evaluator is implemented as follows, and each score is averaged over 10 examples."),
    ("A3-g", "olsson2022", "a head with both a “copying” OV circuit and a “prefix matching” QK circuit is thereby an induction head by our definition"),
    ("A3-i", "olsson2022", "It would’ve been better if we had used a start of sequence token for the copying head evaluator as well, but we omitted it by mistake."),
    ("A3-h", "olsson2022", "In practice, induction heads don't exhibit these properties perfectly, and our measurements give us a continuum, but there is a clear subset of heads which exhibit these properties with much greater than random chance."),
    # A4 Bansal et al.
    ("A4-a", "bansal2023", "We follow the approach described by Olsson et al. (2022), but instead of computing scores using 10 sequences with fixed length of 25, we compute these scores using 100 sequences with varying lengths"),
    ("A4-b", "bansal2023", "When seen in conjunction, these observations indicate that there is a sparse set of attention heads that are capable of performing both primitive operations and thus can be deemed plausible induction heads."),
    ("A4-c", "bansal2023", "we first formalize the total capacity of a model to perform prefix matching (or copying) to be the sum of the respective scores for individual attention heads in the model."),
    ("A4-d", "bansal2023", "temp_score ← relu_raised_logit_max_ind/sum(relu_raised_logits)"),
    ("A4-e", "bansal2023", "logits ← softmax(logits, dim = 1)"),
    ("A4-f", "bansal2023", "remove 4% most & least common tokens"),
    # A5 Wang et al., Crosbie & Shutova
    ("A5-a", "wang2022", "we instead knockout nodes through mean ablation: replacing them with their average activation value across some reference distribution"),
    ("A5-b", "wang2022", "In this work, all knockouts are performed in a modified pIOI distribution called pABC ."),
    ("A5-c", "wang2022", "we compute the mean of a node across samples of the same template."),
    ("A5-i", "wang2022", "When knocking out a single node, a (head, token position) pair in our circuit"),
    ("A5-j", "crosbie2025", "We generate a sequence of 50 random tokens, excluding the 4% most common and least common tokens. This sequence is repeated four times to form the input to the model."),
    ("A5-k", "crosbie2025", "premises are concatenated to create 500 samples, each comprising of 3000 tokens"),
    ("A5-d", "crosbie2025", "we conduct mean-ablations of 1% and 3% of the heads with the highest prefix matching scores"),
    ("A5-e", "crosbie2025", "we also randomly ablate 1% and 3% of the model’s heads, which are selected following the layer distribution of the previously ablated induction heads."),
    ("A5-f", "crosbie2025", "We argue that focusing solely on prefix matching scores is sufficient for our analysis"),
    ("A5-g", "crosbie2025", "These activations are then averaged to generate a mean embedding vector for each head."),
    ("A5-h", "crosbie2025", "During inference, the activations of the ablated heads are replaced with the mean activations by truncating them to the length of the current prompt."),
    # A6 Meng et al.
    ("A6-a", "meng2022", "we corrupt the embeddings of the token naming the subject s by adding Gaussian noise"),
    ("A6-b", "meng2022", "is set to be three times larger than the observed standard deviation σt of token embeddings as sampled over a body of text. For each run of text, the process is repeated ten times with different samples of corruption noise."),
    ("A6-c", "meng2022", "When we restore hidden states from the original run, we substitute the originally calculated values from the same layer and the same token, and then we allow subsequent calculations to proceed without further intervention."),
    ("A6-d", "meng2022", "For GPT-NeoX we adjust the injected noise to ν = 0.03 and in GPT-J we use ν = 0.025 to match embedding magnitudes."),
    ("A6-e", "meng2022", "restored runs of ten values of mi (and ai , respectively) for an interval of layers ranging from"),
    # A7 Geva et al.
    ("A7-a", "geva2023", "We block xℓr from attending to xℓc at a layer ℓ < L by updating the attention weights to that layer"),
    ("A7-b", "geva2023", "For each layer ℓ, we block the attention edges from the last position to each of S, R and the last"),
    ("A7-e", "geva2023", "for a window of k layers around the ℓ-th layer, and measure the change in prediction probability. We set k = 9 (5) for GPT-2 (GPT-J)."),
    ("A7-c", "geva2023", "this is different from"),
    ("A7-d", "geva2023", "For this reason, we block a range of layers rather than a single layer"),
    # ---------- Part B ----------
    # B1
    ("B1-a", "zhao2021", "For classification tasks, p̂ is the set of probabilities that are associated with each label name, renormalized to one."),
    ("B1-b", "halawi2023", "we measure how often the correct label has a higher probability than its median probability over the dataset."),
    ("B1-c", "halawi2023", "To make the results comparable across datasets, we divide the permuted scores by this random baseline."),
    ("B1-d", "halawi2023", "we decode next-token probabilities for each intermediate layer, using the “logit lens” method"),
    # B2
    ("B2-a", "badia2020", "In addition to using human normalized scores HNS ="),
    ("B2-b", "zhang2023", "we always normalize this by LDcl (r, r′ ) − LD∗ (r, r′ ), so it typically lies in [0, 1], where 1 corresponds to fully restored performance and 0 to the corrupted run performance."),
    ("B2-c", "prepost2022", "this can be quantified as the normalized gain (Hake, 1998):"),
    ("B2-d", "prepost2022", "The normalized gain is the ratio of what a student learned to what they knew entering"),
    # B3
    ("B3-a", "wang2022", "we multiplied this by the OV matrix of a Name Mover Head (simulating what would happen if the head attended perfectly to that token), multiplied by the unembedding matrix, and applied the final layer norm to obtain logit probabilities. We compute the proportion of samples that contain the input name token in the top 5 logits"),
    ("B3-b", "mcdougall2023", "84.70% of the tokens in GPT-2 Small’s vocabulary have their diagonal elements as one of the top 10 most negative values in their columns"),
    ("B3-c", "gould2023", "We call the proportion of succession dataset tokens on which an attention head performs succession the succession score."),
    # B4
    ("B4-a", "wu2024", "we say an attention head h copies and pastes a token from the needle to the output sentence if it follows two criteria"),
    ("B4-b", "yin2025", "To identify and analyze induction heads, we measure their induction scores using the TransformerLens framework"),
    # B5
    ("B5-a", "zhang2023", "Gaussian noising (GN) adds a large Gaussian noise to the token embeddings of the tokens that contain the key information to completing a prompt"),
    ("B5-e", "sensitivity2026", "When a language model fails on surface"),
    ("B5-d", "lad2024", "we perform layer-wise interventions—deleting individual layers or swapping adjacent ones"),
    ("B5-b", "heimersheim2024", "The success of Gaussian noise corruption is highly sensitive to the noise level."),
    ("B5-c", "stochln2026", "We normalize the residual-stream state, add isotropic Gaussian noise, and renormalize"),
    # B6
    ("B6-a", "wang2022", "This can be evaluated by showing that v can significantly recover F after knocking out a set of nodes K."),
    ("B6-b", "wang2022", "For most heads, removing the class of heads G that v is a part of provides"),
    ("B6-e", "wang2022", "a reasonable minimality score, but in some instances a more careful choice is needed"),
    ("B6-f", "wang2022", "Formally, the minimality criterion is whether for every node v ∈ C there exists a subset K ⊆ C \\ {v} that has high minimality score |F (C \\ (K ∪ {v})) − F (C \\ K)|."),
    ("B6-c", "todd2023", "measure its causal indirect effect (CIE) towards recovering the correct answer"),
    ("B6-g", "todd2023", "The intuition here is to measure the degree to which using the “correct” mean attention head output"),
    ("B6-h", "heimersheim2024", "then running the model on the corrupted prompt while overwriting some of its activations with previously saved clean-prompt activations"),
    ("B6-i", "todd2023", "We also make use of uninformative ICL prompts p̃ti ∈ P̃t for which the labels are shuffled"),
    ("B6-d", "michel2019", "many attention layers can even be individually reduced to a single attention head"),
    # B7
    ("B7-a", "edelman2024", "the second layer attending to tokens that follow the same token as the current one"),
    ("B7-b", "akyurek2024", "We find that Transformers develop “n-gram heads” that attend to the next token after contexts matching the current context window."),
    ("B7-c", "clark2019", "we treat each head as a simple no-training-required classifier that, given a word as input, outputs the most-attended-to other word."),
    # B8
    ("B8-a", "crosbie2025", "we block attention from each token to all tokens that directly followed tokens of the same category"),
    ("B8-b", "crosbie2025", "we prevent xhc from attending to xhr in head h by modifying the attention weights in that layer"),
    ("B7-d", "edelman2024", "we inspected the attention in each layer throughout training"),
    ("B8-d", "iclcircuit2026", "dozen heads writes against whichever label the model saw most recently"),
    ("B8-c", "edelman2024", "a circuit that looks for recent occurrence(s) of the current token"),
]


def norm(s):
    s = s.replace("ﬁ", "fi").replace("ﬂ", "fl").replace("­", "")
    s = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", s)  # undo line-break hyphenation
    return re.sub(r"\s+", " ", s).strip()


def pages(path):
    out, page, buf = [], 1, []
    for line in path.read_text(errors="replace").splitlines():
        m = re.match(r"=== PAGE (\d+) ===", line)
        if m:
            if buf:
                out.append((page, "\n".join(buf)))
            page, buf = int(m.group(1)), []
        else:
            buf.append(line)
    if buf:
        out.append((page, "\n".join(buf)))
    return out


def find(key, quote):
    q = norm(quote)
    q_loose = norm(re.sub(r"(\w)-(\w)", r"\1\2", quote))
    for suffix in (".reading.txt", ".txt"):
        path = TEXT / f"{key}{suffix}"
        if not path.exists():
            continue
        pg = pages(path)
        for page, text in pg:  # a quote on one page
            t = norm(text)
            if q in t or q_loose in t:
                return page
        for (p1, a), (_, b) in zip(pg, pg[1:]):  # a quote across a page break
            t = norm(a + "\n" + b)
            if q in t or q_loose in t:
                return f"{p1}-{p1 + 1}"
    return None


def version(key):
    url, kind = SOURCES[key]
    m = re.search(r"arxiv\.org/pdf/(\d{4}\.\d{4,5})", url)
    path = TEXT / f"{key}.txt"
    if m and path.exists():
        v = re.search(re.escape(m.group(1)) + r"(v\d+)", path.read_text(errors="replace"))
        return f"arXiv {m.group(1)}{v.group(1) if v else ' (version not printed)'}"
    if "biorxiv" in url:
        return "bioRxiv " + url.rsplit("/", 1)[-1].replace(".full.pdf", "")
    return "web page"


def main():
    missing = []
    lines = ["# Quote check", "", "Every quote in `report.md` and where it was found in the downloaded full text "
             "(PDF page; HTML sources have no pages). Generated by `code/find_quotes.py`.", "",
             "| Id | Source | Page | Found | Quote |", "|---|---|---|---|---|"]
    for qid, key, quote in QUOTES:
        page = find(key, quote)
        if page is None:
            missing.append(qid)
        q = quote.replace("|", "\\|")
        lines.append(f"| {qid} | {key} | {page if page is not None else '-'} | {'yes' if page else 'NO'} | {q} |")
    (RESULTS / "quotes.md").write_text("\n".join(lines) + "\n")
    src = ["# Sources", "", "Full texts downloaded by `code/fetch_fulltexts.py` (cached, not committed).", "",
           "| Key | Version | URL |", "|---|---|---|"]
    for key, (url, _) in SOURCES.items():
        src.append(f"| {key} | {version(key)} | {url} |")
    (RESULTS / "sources.md").write_text("\n".join(src) + "\n")
    print(f"{len(QUOTES) - len(missing)} of {len(QUOTES)} quotes found")
    if missing:
        sys.exit("not found: " + ", ".join(missing))


if __name__ == "__main__":
    main()
