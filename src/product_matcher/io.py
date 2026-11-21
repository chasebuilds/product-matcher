"""Read CSV or Excel product lists and write the result workbook."""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill

from product_matcher.match import Result, Row

GUESS = {
    "name": ["name", "product", "product name", "description", "item", "title"],
    "gtin": ["gtin", "upc", "ean", "barcode"],
    "sku": ["sku", "item code", "code"],
    "price": ["price", "unit price", "cost"],
}


def read_table(path: Path, sheet: str | None = None) -> list[dict[str, str]]:
    if path.suffix.lower() in (".xlsx", ".xlsm"):
        wb = load_workbook(path, read_only=True, data_only=True)
        ws = wb[sheet] if sheet else wb.worksheets[0]
        rows = [["" if v is None else str(v) for v in r] for r in ws.iter_rows(values_only=True)]
        wb.close()
        head, body = rows[0], rows[1:]
        return [dict(zip(head, r, strict=False)) for r in body if any(c.strip() for c in r)]
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def find_column(headers: list[str], role: str, given: str | None) -> str | None:
    if given:
        if given not in headers:
            raise KeyError(f"column {given!r} not found (have: {', '.join(headers)})")
        return given
    low = {h.strip().lower(): h for h in headers}
    return next((low[c] for c in GUESS[role] if c in low), None)


def parse_price(v: str) -> float | None:
    s = re.sub(r"[^0-9.,-]", "", v or "").replace(",", ".")
    try:
        return float(s) if s else None
    except ValueError:
        return None


def to_rows(table: list[dict[str, str]], cols: dict[str, str | None]) -> list[Row]:
    def get(t: dict[str, str], role: str) -> str:
        c = cols.get(role)
        return (t.get(c) or "").strip() if c else ""

    return [Row(get(t, "name"), get(t, "gtin"), get(t, "sku"), parse_price(get(t, "price")))
            for t in table]


HEAD = Font(bold=True)
GRAY = PatternFill("solid", fgColor="E7E6E6")


def _sheet(wb: Workbook, title: str, header: list[str], rows: list[list[Any]]) -> None:
    ws = wb.create_sheet(title)
    ws.append(header)
    for c in ws[1]:
        c.font = HEAD
    for r in rows:
        ws.append(r)
    ws.freeze_panes = "A2"
    for i, h in enumerate(header):
        width = max([len(str(h))] + [len(str(r[i])) for r in rows[:500]])
        ws.column_dimensions[ws.cell(1, i + 1).column_letter].width = min(width + 2, 60)


def write_workbook(out: Path, a: list[Row], b: list[Row], res: Result, labels: tuple[str, str]
                   ) -> None:
    la, lb = labels
    wb = Workbook()
    wb.remove(wb.active)
    pair_head = [f"{la} row", f"{la} name", f"{la} price", f"{lb} row", f"{lb} name",
                 f"{lb} price", "score", "reason", "price diff", "price diff %"]

    def pair_rows(pairs: list[Any]) -> list[list[Any]]:
        out_rows = []
        for p in sorted(pairs, key=lambda p: p.a):
            pa, pb = a[p.a].price, b[p.b].price
            diff = round(pb - pa, 2) if pa is not None and pb is not None else ""
            pct = round(100 * (pb - pa) / pa, 1) if pa and pb is not None else ""
            out_rows.append([p.a + 2, a[p.a].name, pa, p.b + 2, b[p.b].name, pb, p.score,
                             p.reason, diff, pct])
        return out_rows

    _sheet(wb, "Matched", pair_head, pair_rows(res.matched))
    _sheet(wb, "Review", pair_head, pair_rows(res.review))
    for c in wb["Review"]["G"][1:]:
        c.fill = GRAY
    _sheet(wb, f"Unmatched {la}"[:31], ["row", "name", "gtin", "sku", "price"],
           [[i + 2, a[i].name, a[i].gtin, a[i].sku, a[i].price] for i in res.unmatched_a])
    _sheet(wb, f"Unmatched {lb}"[:31], ["row", "name", "gtin", "sku", "price"],
           [[j + 2, b[j].name, b[j].gtin, b[j].sku, b[j].price] for j in res.unmatched_b])
    wb.save(out)
