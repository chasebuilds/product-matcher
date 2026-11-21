from benchmark.generate import generate
from benchmark.run_benchmark import score


def test_generator_is_seeded() -> None:
    assert generate(1, 50) == generate(1, 50)
    assert generate(1, 50) != generate(2, 50)


def test_small_benchmark_run() -> None:
    s = score(3, 300)
    assert s.matched_right / s.matched > 0.97
    assert s.matched_right / s.true_pairs > 0.7
