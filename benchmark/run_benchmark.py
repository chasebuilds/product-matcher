"""Score the matcher on generated lists with known true pairs; write BENCHMARK.md and README."""

from __future__ import annotations

import argparse
import datetime as dt
import platform
import re
import time
from dataclasses import dataclass
from pathlib import Path

from benchmark.generate import generate
from product_matcher.io import find_column, to_rows
from product_matcher.match import match

ROOT = Path(__file__).resolve().parent.parent


@dataclass
class Score:
    rows_a: int
    rows_b: int
    true_pairs: int
    matched: int
    matched_right: int
    by_code: int
    review: int
    review_right: int
    seconds: float


def pct(a: int, b: int) -> str:
    return f"{100 * a / b:.1f}%" if b else "n/a"


def score(seed: int, n: int, auto: float = 0.92, review: float = 0.75) -> Score:
    ta, tb = generate(seed, n)
    rows = []
    for t in (ta, tb):
        h = list(t[0])
        rows.append(to_rows(t, {r: find_column(h, r, None) for r in ("name", "gtin", "sku",
                                                                       "price")}))
    start = time.perf_counter()
    res = match(rows[0], rows[1], auto, review)
    seconds = time.perf_counter() - start
    ids_b = {r["true_id"] for r in tb}
    true_pairs = sum(r["true_id"] in ids_b for r in ta)

    def right(p: object) -> bool:
        return bool(ta[p.a]["true_id"] == tb[p.b]["true_id"])  # type: ignore[attr-defined]

    return Score(len(ta), len(tb), true_pairs, len(res.matched),
                 sum(right(p) for p in res.matched),
                 sum(p.reason.startswith("same") for p in res.matched), len(res.review),
                 sum(right(p) for p in res.review), seconds)


def table(s: Score, n: int) -> str:
    return "\n".join([
        "| Measure | Result |",
        "|---|---:|",
        f"| Products invented / rows in list A / rows in list B | {n:,} / {s.rows_a:,} / "
        f"{s.rows_b:,} |",
        f"| True pairs (same product in both lists) | {s.true_pairs:,} |",
        f"| Auto-matched pairs that were right (precision) | **{pct(s.matched_right, s.matched)}**"
        f" ({s.matched_right:,} of {s.matched:,}) |",
        f"| True pairs auto-matched (recall) | **{pct(s.matched_right, s.true_pairs)}** "
        f"({s.matched_right:,} of {s.true_pairs:,}) |",
        f"| Auto-matches made by GTIN or SKU | {pct(s.by_code, s.matched)} ({s.by_code:,}) |",
        f"| List A rows sent to review | {pct(s.review, s.rows_a)} ({s.review:,}) |",
        f"| Review pairs that were right | {pct(s.review_right, s.review)} "
        f"({s.review_right:,} of {s.review:,}) |",
        f"| True pairs found if review is checked by a person | "
        f"**{pct(s.matched_right + s.review_right, s.true_pairs)}** |",
    ])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20261121)
    ap.add_argument("--products", type=int, default=3000)
    args = ap.parse_args()
    s = score(args.seed, args.products)
    t = table(s, args.products)
    print(t)
    body = f"""# Benchmark

Written by `benchmark/run_benchmark.py` on {dt.date.today()} from a real run.
No number on this page was typed by hand.

Command: `python -m benchmark.run_benchmark --seed {args.seed} --products {args.products}`
Python {platform.python_version()} on {platform.system()}, default thresholds `--auto 0.92
--review 0.75`. Matching took {s.seconds:.2f} s.

## Method

1. Invent {args.products:,} products from made-up brands, product types, flavors, sizes and pack
   counts. Many share brand, type and flavor and differ only in size or pack, so near misses are
   common. Every product gets a 13-digit GTIN. No real brand or product is used.
2. List A (a supplier price list) holds about 92% of them, written upper case as
   `BRAND TYPE FLAVOR 12X500ML`. Half its rows carry the GTIN.
3. List B (a store catalog) holds about 92% of them, so some products are in only one list. Names
   are written a different way: flavor before type or after it, sizes as `0.5 L`, `50cl` or
   `1 kg`, packs as `(12 pack)`, `12 x` or `12pk`. 15% drop the brand and 15% have two letters
   swapped in one word. 40% carry the GTIN, with the leading zero dropped. SKUs never match
   across lists.
4. Run the matcher. A pair is right when both rows came from the same invented product.

## Result

{t}

## What this does not show

The data is generated, so it only has the kinds of mess the generator writes. Real lists have
others: abbreviations (`Choc`, `Org`), house-brand renames, sizes missing from one side,
multi-buy bundles. See [LIMITATIONS.md](LIMITATIONS.md).
"""
    (ROOT / "BENCHMARK.md").write_text(body, encoding="utf-8")
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    text = re.sub(r"(<!-- benchmark:start -->\n).*?(\n<!-- benchmark:end -->)",
                  lambda m: m.group(1) + t + m.group(2), text, flags=re.S)
    readme.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
