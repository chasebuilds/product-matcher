# Limitations

What product-matcher does not do, or does poorly. Read this before trusting a matched file.

## Codes

- **GTINs are compared as digits with leading zeros dropped.** The check digit is not verified, so
  a mistyped GTIN that happens to equal another product's code would match it.
- **SKUs only help when both lists use the same SKUs.** A supplier code and a store code for the
  same product never match each other.
- The first row with a given code wins. Duplicate codes inside one list are not reported.

## Names

- **It compares text, not meaning.** Abbreviations (`Choc`, `Org`, `Pnt Btr`), synonyms (`soda`
  and `pop`) and house-brand renames lower the score. There is no dictionary of them.
- **A missing brand lowers the score** enough that most such pairs land in review, not matched.
- **Word order is ignored**, so `Lemon Mint Tea` and `Mint Lemon Tea` look the same, even when
  they are different products.
- Only the first size and the first pack count in a name are read. `6 x 4 x 100g` (a case of
  multipacks) keeps only the first pack count.

## Sizes and packs

- **Units are converted only inside one kind**: volume (`ml`, `cl`, `l`, `fl oz`) or weight (`g`,
  `kg`, `oz`, `lb`). `oz` is read as weight, never as fluid ounces unless written `fl oz`.
- **A different size or pack count cuts the score** (times 0.6), so the same drink in `500 ml` and
  `1 L` is not matched. That is on purpose, but a list that writes the case size and a list that
  writes the unit size will not match by name.
- Sizes within 2% count as the same, to absorb rounding such as `16 oz` and `454 g`.

## Pairing

- Each row is used once. Pairs are picked highest score first, which is greedy, not a global best
  assignment.
- Only the 5 best name candidates per row are scored for size and pack.

## Benchmark

- The benchmark data is generated, so it only holds the kinds of mess the generator writes. The
  numbers in [BENCHMARK.md](BENCHMARK.md) are an upper bound for messy real lists.
