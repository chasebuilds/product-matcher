# Benchmark

Written by `benchmark/run_benchmark.py` on 2026-11-21 from a real run.
No number on this page was typed by hand.

Command: `python -m benchmark.run_benchmark --seed 20261121 --products 3000`
Python 3.11.15 on Windows, default thresholds `--auto 0.92
--review 0.75`. Matching took 0.21 s.

## Method

1. Invent 3,000 products from made-up brands, product types, flavors, sizes and pack
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

| Measure | Result |
|---|---:|
| Products invented / rows in list A / rows in list B | 3,000 / 2,762 / 2,779 |
| True pairs (same product in both lists) | 2,541 |
| Auto-matched pairs that were right (precision) | **100.0%** (2,216 of 2,216) |
| True pairs auto-matched (recall) | **87.2%** (2,216 of 2,541) |
| Auto-matches made by GTIN or SKU | 22.6% (500) |
| List A rows sent to review | 5.5% (151) |
| Review pairs that were right | 69.5% (105 of 151) |
| True pairs found if review is checked by a person | **91.3%** |

## What this does not show

The data is generated, so it only has the kinds of mess the generator writes. Real lists have
others: abbreviations (`Choc`, `Org`), house-brand renames, sizes missing from one side,
multi-buy bundles. See [LIMITATIONS.md](LIMITATIONS.md).
