"""Pair rows of two product lists: codes first, then names."""

from __future__ import annotations

from dataclasses import dataclass, field

from rapidfuzz import fuzz, process

from product_matcher.normalize import Key, normalize, normalize_code


@dataclass
class Row:
    name: str
    gtin: str = ""
    sku: str = ""
    price: float | None = None


@dataclass
class Pair:
    a: int
    b: int
    score: float
    reason: str


@dataclass
class Result:
    matched: list[Pair] = field(default_factory=list)
    review: list[Pair] = field(default_factory=list)
    unmatched_a: list[int] = field(default_factory=list)
    unmatched_b: list[int] = field(default_factory=list)


def name_score(ka: Key, kb: Key, text_score: float) -> tuple[float, str]:
    score, notes = text_score / 100, [f"name {text_score:.0f}"]
    if ka.size is not None and kb.size is not None:
        if ka.unit != kb.unit or abs(ka.size - kb.size) > 0.02 * max(ka.size, kb.size):
            score *= 0.6
            notes.append("size differs")
        else:
            notes.append("size same")
    elif (ka.size is None) != (kb.size is None):
        score *= 0.9
        notes.append("size on one side only")
    if ka.pack != kb.pack:
        score *= 0.6
        notes.append("pack differs")
    return score, ", ".join(notes)


def match(a: list[Row], b: list[Row], auto: float = 0.92, review: float = 0.75) -> Result:
    res = Result()
    used_a: set[int] = set()
    used_b: set[int] = set()
    for attr in ("gtin", "sku"):
        index: dict[str, int] = {}
        for j, r in enumerate(b):
            code = normalize_code(getattr(r, attr))
            if code and j not in used_b:
                index.setdefault(code, j)
        for i, r in enumerate(a):
            code = normalize_code(getattr(r, attr))
            j = index.get(code, -1) if code and i not in used_a else -1
            if j >= 0 and j not in used_b:
                res.matched.append(Pair(i, j, 1.0, f"same {attr.upper()}"))
                used_a.add(i)
                used_b.add(j)
    ia = [i for i in range(len(a)) if i not in used_a]
    ib = [j for j in range(len(b)) if j not in used_b]
    ka = [normalize(a[i].name) for i in ia]
    kb = [normalize(b[j].name) for j in ib]
    cands: list[Pair] = []
    if ia and ib:
        grid = process.cdist([k.text for k in ka], [k.text for k in kb],
                             scorer=fuzz.token_sort_ratio, workers=-1)
        top = min(5, len(ib))
        for x, row in enumerate(grid):
            for y in row.argsort()[::-1][:top]:
                s, why = name_score(ka[x], kb[y], float(row[y]))
                if s >= review:
                    cands.append(Pair(ia[x], ib[int(y)], round(s, 3), why))
    cands.sort(key=lambda p: -p.score)
    for p in cands:
        if p.a in used_a or p.b in used_b:
            continue
        used_a.add(p.a)
        used_b.add(p.b)
        (res.matched if p.score >= auto else res.review).append(p)
    res.unmatched_a = [i for i in range(len(a)) if i not in used_a]
    res.unmatched_b = [j for j in range(len(b)) if j not in used_b]
    return res
