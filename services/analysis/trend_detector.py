import re

TREND_KEYWORDS = [
    "ai", "money", "success", "secret", "mistake",
    "viral", "growth", "hack", "truth", "shocking",
    "never", "everyone", "future", "billionaire"
]

def trend_score(text: str) -> float:
    text = text.lower()
    score = 0

    for word in TREND_KEYWORDS:
        if word in text:
            score += 1

    return score / len(TREND_KEYWORDS)