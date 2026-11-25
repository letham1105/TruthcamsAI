
import re
from collections import Counter
from pathlib import Path

INPUT_FILE = Path("filtered_verification_results.txt")
THRESHOLDS = [0.05, 0.08, 0.10]

LABELS = [
    "supported",
    "refuted",
    "not_enough_information",
]

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Cannot find {INPUT_FILE}. "
        "Run test_filtered_verification.py first."
    )

text = INPUT_FILE.read_text(encoding="utf-8")

articles = []
current_article = None

# Parse article headers and sentence result lines
for line in text.splitlines():

    if line.strip() in [
        "CafeF Rank 1",
        "Kenh14 Rank 3",
        "Dan Tri Rank 5",
    ]:
        current_article = {
            "name": line.strip(),
            "sentences": [],
        }
        articles.append(current_article)
        continue

    pattern = (
        r"S\d+\s*\|\s*"
        r"relevance=([\d.]+)\s*\|\s*"
        r"group=(\w+)\s*\|\s*"
        r"label=([\w]+)\s*\|\s*"
        r"confidence=([\d.]+)"
    )

    match = re.search(pattern, line)

    if match and current_article is not None:
        relevance = float(match.group(1))
        label = match.group(3)
        confidence = float(match.group(4))

        sentence = line.split("\n", 1)[0]

        current_article["sentences"].append({
            "raw_line": line,
            "relevance": relevance,
            "label": label,
            "confidence": confidence,
        })

# The report contains sentence text on following lines.
# Extract each sentence block using a separate parser.
# This section reads sentence blocks from the full report.

pattern = (
    r"(S\d+\s*\|\s*relevance=([\d.]+)\s*\|\s*"
    r"group=(\w+)\s*\|\s*label=([\w]+)\s*\|\s*"
    r"confidence=([\d.]+)\n)(.*?)(?=\nS\d+\s*\||"
    r"\n-+\n|\nARTICLE SUMMARY|\Z)"
)

matches = list(re.finditer(pattern, text, re.DOTALL))

records = []
current_article_name = None

for line in text.splitlines():
    if line.strip() in [
        "CafeF Rank 1",
        "Kenh14 Rank 3",
        "Dan Tri Rank 5",
    ]:
        current_article_name = line.strip()

    # Article name is resolved below from match position.

for match in matches:
    start = match.start()

    article_name = "Unknown"
    for name in [
        "CafeF Rank 1",
        "Kenh14 Rank 3",
        "Dan Tri Rank 5",
    ]:
        header_pos = text.rfind(name, 0, start)
        if header_pos >= 0:
            # Ensure this is the closest preceding article header
            candidates = [
                (text.rfind(n, 0, start), n)
                for n in [
                    "CafeF Rank 1",
                    "Kenh14 Rank 3",
                    "Dan Tri Rank 5",
                ]
            ]
            article_name = max(candidates)[1]
            break

    sentence_text = match.group(6).strip()

    records.append({
        "article": article_name,
        "relevance": float(match.group(2)),
        "label": match.group(4),
        "confidence": float(match.group(5)),
        "sentence": sentence_text,
    })

if not records:
    raise RuntimeError(
        "No sentence records parsed. "
        "Check the format of filtered_verification_results.txt."
    )

# Compare thresholds
output_lines = []

def log(msg=""):
    print(msg)
    output_lines.append(str(msg))

log("=" * 100)
log("THRESHOLD COMPARISON")
log("=" * 100)

log(f"Total sentences: {len(records)}")

for threshold in THRESHOLDS:

    kept = [
        r for r in records
        if r["relevance"] >= threshold
    ]

    rejected = [
        r for r in records
        if r["relevance"] < threshold
    ]

    kept_counts = Counter(r["label"] for r in kept)
    rejected_counts = Counter(r["label"] for r in rejected)

    log("\n" + "=" * 100)
    log(f"THRESHOLD: {threshold}")
    log("=" * 100)

    log(f"Kept: {len(kept)} / {len(records)}")
    log(f"Rejected: {len(rejected)} / {len(records)}")

    log("\n[KEPT]")
    for label in LABELS:
        log(f"{label}: {kept_counts[label]}")

    log("\n[REJECTED]")
    for label in LABELS:
        log(f"{label}: {rejected_counts[label]}")

    log("\n[REJECTED SENTENCES]")

    for r in rejected:
        log(
            f"\n{r['article']} | "
            f"score={r['relevance']:.4f} | "
            f"label={r['label']} | "
            f"confidence={r['confidence']:.4f}"
        )
        log(r["sentence"])

# Per-threshold comparison table
log("\n" + "=" * 100)
log("COMPARISON TABLE")
log("=" * 100)

log(
    f"{'Threshold':<12}"
    f"{'Kept':<12}"
    f"{'Rejected':<12}"
    f"{'Supported':<14}"
    f"{'Refuted':<14}"
    f"{'NEI':<14}"
)

for threshold in THRESHOLDS:

    kept = [
        r for r in records
        if r["relevance"] >= threshold
    ]

    rejected = [
        r for r in records
        if r["relevance"] < threshold
    ]

    counts = Counter(r["label"] for r in kept)

    log(
        f"{threshold:<12}"
        f"{len(kept):<12}"
        f"{len(rejected):<12}"
        f"{counts['supported']:<14}"
        f"{counts['refuted']:<14}"
        f"{counts['not_enough_information']:<14}"
    )

output_file = Path("threshold_comparison_results.txt")
output_file.write_text(
    "\n".join(output_lines),
    encoding="utf-8",
)

print(f"\nSaved report to: {output_file}")

