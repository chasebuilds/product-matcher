import pytest

from product_matcher.normalize import normalize, normalize_code


@pytest.mark.parametrize(
    ("a", "b"),
    [
        (
            "Brightvale Sparkling Water Lemon 12 x 500ml",
            "BRIGHTVALE LEMON SPARKLING WATER 0.5 L (12 PACK)",
        ),
        ("Norrow Oat Crackers 1,2kg", "norrow oat crackers 1200 g"),
        ("Kestrel Olive Oil 75cl", "Kestrel Olive Oil 750 ML"),
        ("Dunmere Tea Pack of 6 100g", "dunmere tea 6pk 100 G"),
    ],
)
def test_same_product_same_key(a: str, b: str) -> None:
    ka, kb = normalize(a), normalize(b)
    assert (ka.words, ka.size, ka.pack) == (kb.words, kb.size, kb.pack)


def test_units_and_pack() -> None:
    k = normalize("Brightvale Cola 24 x 330 ml")
    assert (k.size, k.unit, k.pack) == (330.0, "ml", 24)
    assert normalize("Oat Bars 6 pack 1 lb").size == 453.6
    assert normalize("Plain name").size is None


def test_codes() -> None:
    assert normalize_code("0012-3456-7890") == normalize_code("1234567890")
    assert normalize_code("ab-12") == "AB12"
