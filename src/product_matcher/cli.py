"""Command line: pmatch a.csv b.xlsx -o matches.xlsx."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from product_matcher.io import find_column, read_table, to_rows, write_workbook
from product_matcher.match import match


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="pmatch", description=__doc__)
    ap.add_argument("a", type=Path, help="first list (CSV or Excel), e.g. supplier price list")
    ap.add_argument("b", type=Path, help="second list (CSV or Excel), e.g. store catalog")
    ap.add_argument("-o", "--out", type=Path, default=Path("matches.xlsx"))
    ap.add_argument("--auto", type=float, default=0.92, help="score to match without review")
    ap.add_argument("--review", type=float, default=0.75, help="lowest score sent to review")
    for role in ("name", "gtin", "sku", "price"):
        ap.add_argument(f"--{role}", help=f"{role} column in both files (default: guessed)")
    ap.add_argument("--sheet", help="sheet to read from Excel files (default: the first)")
    args = ap.parse_args(argv)
    if not 0 <= args.review <= args.auto <= 1:
        print("error: need 0 <= --review <= --auto <= 1", file=sys.stderr)
        return 2
    lists = []
    try:
        for path in (args.a, args.b):
            table = read_table(path, args.sheet)
            headers = list(table[0]) if table else []
            cols = {r: find_column(headers, r, getattr(args, r))
                    for r in ("name", "gtin", "sku", "price")}
            if not cols["name"]:
                raise KeyError(f"{path}: no name column found, pass --name")
            lists.append(to_rows(table, cols))
    except (OSError, KeyError, IndexError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    a, b = lists
    res = match(a, b, args.auto, args.review)
    write_workbook(args.out, a, b, res, (args.a.stem[:12], args.b.stem[:12]))
    print(f"{len(a)} rows in {args.a.name}, {len(b)} rows in {args.b.name}")
    print(f"{len(res.matched)} matched, {len(res.review)} to review, "
          f"{len(res.unmatched_a)} + {len(res.unmatched_b)} unmatched")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
