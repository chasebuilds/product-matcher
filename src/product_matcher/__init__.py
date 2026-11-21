"""Match product rows between two lists."""

from product_matcher.match import Pair, Result, match
from product_matcher.normalize import Key, normalize

__all__ = ["Key", "Pair", "Result", "match", "normalize"]
