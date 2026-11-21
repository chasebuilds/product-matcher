from product_matcher.match import Row, match


def test_code_then_name() -> None:
    a = [Row("Brightvale Cola 330ml", gtin="0001234567"), Row("Norrow Oat Crackers 200g"),
         Row("Kestrel Olive Oil 1L"), Row("Only In A Thing")]
    b = [Row("Norrow Crackers Oat 200 g"), Row("Cola Brightvale 0.33 L", gtin="1234567"),
         Row("Kestrel Olive Oil 500 ml"), Row("Something Else Entirely")]
    r = match(a, b)
    pairs = {(p.a, p.b): p.reason for p in r.matched}
    assert pairs[(0, 1)] == "same GTIN"
    assert (1, 0) in pairs
    assert 2 not in {p.a for p in r.matched}
    assert 3 in r.unmatched_a and 3 in r.unmatched_b


def test_review_band() -> None:
    a = [Row("Brightvale Lemon Water 500ml")]
    b = [Row("Brightvale Lemon Water Zero 500ml")]
    r = match(a, b, auto=0.99, review=0.5)
    assert len(r.review) == 1 and not r.matched


def test_one_to_one_and_empty() -> None:
    r = match([Row("Tea 100g"), Row("Tea 100g")], [Row("Tea 100g")])
    assert len(r.matched) == 1 and len(r.unmatched_a) == 1
    assert match([], [Row("x")]).unmatched_b == [0]
