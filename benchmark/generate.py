"""Write two seeded product lists of invented products with known true pairs."""

from __future__ import annotations

import argparse
import csv
import random
from dataclasses import dataclass
from pathlib import Path

from openpyxl import Workbook

BRANDS = ["Brightvale", "Norrow", "Kestrel Farms", "Dunmere", "Ollby", "Tarnwick", "Pellow",
          "Quillon", "Marrowby", "Fennick", "Glasswell", "Hobbin", "Ivelle", "Jorvane", "Lunt"]
TYPES = [("Sparkling Water", "ml", [330, 500, 1000, 1500]), ("Olive Oil", "ml", [250, 500, 750]),
         ("Oat Crackers", "g", [150, 200, 400]), ("Green Tea", "g", [40, 80, 100]),
         ("Apple Juice", "ml", [200, 1000]), ("Peanut Butter", "g", [340, 500, 1000]),
         ("Dish Soap", "ml", [450, 750]), ("Rice Cakes", "g", [100, 130]),
         ("Tomato Sauce", "g", [400, 680]), ("Cold Brew Coffee", "ml", [250, 1000]),
         ("Granola", "g", [350, 500, 750]), ("Hand Soap", "ml", [250, 500])]
VARIANTS = ["Original", "Lemon", "Lime", "Mint", "Berry", "Honey", "Unsalted", "Classic",
            "Extra Virgin", "Chili", "Vanilla", "Sea Salt"]
PACKS = [1, 1, 1, 4, 6, 12]


@dataclass(frozen=True)
class Product:
    pid: int
    brand: str
    kind: str
    variant: str
    size: int
    unit: str
    pack: int
    gtin: str
    price: float


def products(rng: random.Random, n: int) -> list[Product]:
    seen: set[tuple[str, str, str, int, int]] = set()
    out: list[Product] = []
    while len(out) < n:
        kind, unit, sizes = rng.choice(TYPES)
        key = (rng.choice(BRANDS), kind, rng.choice(VARIANTS), rng.choice(sizes), rng.choice(PACKS))
        if key in seen:
            continue
        seen.add(key)
        gtin = "".join(rng.choice("0123456789") for _ in range(12))
        price = round(rng.uniform(0.8, 9.0) * key[4] * (key[3] / 500) ** 0.5, 2)
        out.append(Product(len(out) + 1, key[0], kind, key[2], key[3], unit, key[4],
                           "0" + gtin, price))
    return out


def size_text(rng: random.Random, p: Product, store: bool) -> str:
    if not store:
        return f"{p.size}{p.unit.upper()}"
    if p.unit == "ml" and p.size >= 500 and rng.random() < 0.6:
        return f"{p.size / 1000:g} L"
    if p.unit == "ml" and p.size < 1000 and rng.random() < 0.3:
        return f"{p.size / 10:g}cl"
    if p.unit == "g" and p.size >= 1000:
        return f"{p.size / 1000:g} kg"
    return f"{p.size} {p.unit}"


def typo(rng: random.Random, word: str) -> str:
    if len(word) < 5:
        return word
    i = rng.randrange(1, len(word) - 2)
    return word[:i] + word[i + 1] + word[i] + word[i + 2:]


def supplier_name(p: Product) -> str:
    pack = f"{p.pack}X" if p.pack > 1 else ""
    return f"{p.brand} {p.kind} {p.variant} {pack}{p.size}{p.unit}".upper()


def store_name(rng: random.Random, p: Product) -> str:
    words = [p.brand, p.variant, p.kind] if rng.random() < 0.6 else [p.brand, p.kind, p.variant]
    if rng.random() < 0.15:
        words = [w for w in words if w != p.brand]
    name = " ".join(words)
    if rng.random() < 0.15:
        parts = name.split()
        k = rng.randrange(len(parts))
        parts[k] = typo(rng, parts[k])
        name = " ".join(parts)
    size = size_text(rng, p, True)
    if p.pack > 1:
        size = rng.choice([f"{size} ({p.pack} pack)", f"{p.pack} x {size}", f"{size}, {p.pack}pk"])
    return f"{name} {size}"


def generate(seed: int, n: int) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    rng = random.Random(seed)
    items = products(rng, n)
    a: list[dict[str, str]] = []
    b: list[dict[str, str]] = []
    for p in items:
        r = rng.random()
        in_a, in_b = r < 0.92, r > 0.08
        if in_a:
            gtin = p.gtin if rng.random() < 0.5 else ""
            a.append({"sku": f"SUP-{p.pid:05d}", "gtin": gtin, "product name": supplier_name(p),
                      "unit price": f"{p.price:.2f}", "true_id": str(p.pid)})
        if in_b:
            gtin = p.gtin.lstrip("0") if rng.random() < 0.4 else ""
            price = round(p.price * rng.uniform(1.1, 1.6), 2)
            b.append({"sku": f"ST{rng.randrange(10**6):06d}", "upc": gtin,
                      "title": store_name(rng, p), "price": f"{price:.2f}",
                      "true_id": str(p.pid)})
    rng.shuffle(b)
    return a, b


def write(a: list[dict[str, str]], b: list[dict[str, str]], out_a: Path, out_b: Path) -> None:
    with out_a.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(a[0]))
        w.writeheader()
        w.writerows(a)
    wb = Workbook()
    ws = wb.active
    ws.title = "catalog"
    ws.append(list(b[0]))
    for r in b:
        ws.append(list(r.values()))
    wb.save(out_b)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--products", type=int, default=40)
    ap.add_argument("--out", type=Path, default=Path("samples"))
    args = ap.parse_args()
    a, b = generate(args.seed, args.products)
    write(a, b, args.out / "supplier.csv", args.out / "store.xlsx")


if __name__ == "__main__":
    main()
