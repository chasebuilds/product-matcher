"""Turn a product name into comparable parts: words, size and pack count."""

from __future__ import annotations

import re
from dataclasses import dataclass

UNITS = {
    "ml": ("ml", 1.0), "cl": ("ml", 10.0), "l": ("ml", 1000.0), "ltr": ("ml", 1000.0),
    "litre": ("ml", 1000.0), "liter": ("ml", 1000.0), "floz": ("ml", 29.5735),
    "g": ("g", 1.0), "gr": ("g", 1.0), "kg": ("g", 1000.0), "oz": ("g", 28.3495),
    "lb": ("g", 453.592), "lbs": ("g", 453.592),
}
SIZE = re.compile(r"(\d+(?:\.\d+)?)\s*(fl\.?\s*oz|ml|cl|ltr|litre|liter|l|kg|gr|g|oz|lbs|lb)\b")
PACK_X = re.compile(r"\b(\d+)\s*x\b(?!\s*\d+(?:\.\d+)?\s*x)")
PACK_WORD = re.compile(
    r"\b(?:pack|pk|case|box)\s*(?:of\s*)?(\d+)\b|\b(\d+)\s*(?:pack|pk|ct|count|pcs)\b"
)
STOP = {"the", "and", "of", "with", "pack", "pk", "ct", "count", "case", "box", "pcs", "x"}


@dataclass(frozen=True)
class Key:
    words: tuple[str, ...]
    size: float | None
    unit: str | None
    pack: int

    @property
    def text(self) -> str:
        return " ".join(self.words)


def normalize_code(code: str) -> str:
    """Digits-only codes lose leading zeros (UPC-A vs EAN-13); other codes are upper-cased."""
    c = re.sub(r"[^0-9A-Za-z]", "", code).upper()
    return c.lstrip("0") if c.isdigit() else c


def normalize(name: str) -> Key:
    s = name.lower().replace(",", ".").replace("×", "x").replace("&", " and ")
    s = re.sub(r"(?<=\d)\s*x\s*(?=\d)", " x ", s)
    s = re.sub(r"[^\w.\s]", " ", s)
    s = re.sub(r"(?<!\d)\.|\.(?!\d)", " ", s)
    size = unit = None
    m = SIZE.search(s)
    if m:
        unit, factor = UNITS[re.sub(r"[.\s]", "", m.group(2))]
        size = round(float(m.group(1)) * factor, 1)
        s = s[: m.start()] + " " + s[m.end():]
    pack = 1
    p = PACK_X.search(s) or PACK_WORD.search(s)
    if p:
        pack = int(next(g for g in p.groups() if g))
        s = s[: p.start()] + " " + s[p.end():]
    words = tuple(sorted(w for w in s.split() if w not in STOP))
    return Key(words, size, unit, pack)
