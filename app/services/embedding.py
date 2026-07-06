import math
import re
from collections import Counter

TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|\d+")


class DeterministicEmbedding:
    def embed(self, text: str) -> dict[str, float]:
        tokens = []
        for token in TOKEN_RE.findall(text):
            tokens.extend(part for part in token.lower().split("_") if part)
        counts = Counter(tokens)
        norm = math.sqrt(sum(value * value for value in counts.values())) or 1.0
        return {token: value / norm for token, value in counts.items()}

    @staticmethod
    def similarity(left: dict[str, float], right: dict[str, float]) -> float:
        if len(left) > len(right):
            left, right = right, left
        return sum(value * right.get(token, 0.0) for token, value in left.items())
