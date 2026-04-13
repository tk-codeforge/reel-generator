HOOK_PATTERNS = [
    "you won't believe",
    "this changed my life",
    "nobody tells you",
    "big mistake",
    "the truth is",
    "what if i told you",
]

def hook_score(text: str) -> float:
    text = text.lower()
    score = 0

    for pattern in HOOK_PATTERNS:
        if pattern in text:
            score += 1

    return score / len(HOOK_PATTERNS)