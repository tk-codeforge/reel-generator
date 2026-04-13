"""
Hook classifier — fully local, no API key required.
Uses keyword and pattern matching to classify the opening of a transcript
into one of the 7 proven hook types.
"""
import re
from models.analysis_models import HookAnalysis
from utils.logger import get_logger

logger = get_logger(__name__)

HOOK_TYPES = [
    "Big Promise",
    "I Was Wrong",
    "Shock / Controversy",
    "Insider Secret",
    "Tension Setup",
    "Mini-Story Cold Open",
    "Counterintuitive / Weird",
]

_RULES = [
    {
        "hook_type": "I Was Wrong",
        "patterns": [
            r"\bi was wrong\b", r"\bi made a mistake\b", r"\bi failed\b",
            r"\bi learned the hard way\b", r"\bi used to (think|believe|do)\b",
            r"\bfor \d+ years? i (thought|believed|did)\b",
            r"\beverything (i knew|i thought) was wrong\b",
            r"\buntil (i|this|one day|everything) changed\b",
        ],
        "template": "I did everything wrong for X years until this…",
        "base_score": 0.85,
    },
    {
        "hook_type": "Tension Setup",
        "patterns": [
            r"\bwe were (running out|about to|almost|nearly)\b",
            r"\bwe (almost|nearly) (lost|failed|went bankrupt|shut down)\b",
            r"\bone (email|call|message|moment) changed everything\b",
            r"\bthen (everything changed|it all changed|one thing happened)\b",
            r"\b(crisis|disaster|problem|emergency) (hit|struck|happened)\b",
            r"\bwe had (no money|no choice|nothing left)\b",
            r"\band then (everything|it all)\b",
        ],
        "template": "We were running out of money… and then one email changed everything.",
        "base_score": 0.82,
    },
    {
        "hook_type": "Mini-Story Cold Open",
        "patterns": [
            r"\bhe (looked at|told|said|walked|called)\b",
            r"\bshe (looked at|told|said|walked|called)\b",
            r"\bthey (looked at|told|said|walked|called)\b",
            r"\bhe said[,\s]", r"\bshe said[,\s]",
            r"\bi (walked into|sat down|picked up the phone|got a call)\b",
            r"\bit was \d{4}\b",
            r"\bthat (morning|night|day|moment|year)\b.*\bi\b",
        ],
        "template": "He looked at me and said — fire half the team today.",
        "base_score": 0.80,
    },
    {
        "hook_type": "Insider Secret",
        "patterns": [
            r"\bnobody (tells|talks about|knows)\b",
            r"\bwhat (vcs?|investors?|ceos?|experts?) really\b",
            r"\bthe (real|actual|true) reason\b",
            r"\bbehind (the scenes|closed doors)\b",
            r"\bexclusive(ly)?\b",
            r"\binsider\b",
            r"\bthey (don't|never|won't) tell you\b",
            r"\bwhat (most people|everyone) (miss|gets wrong|doesn't know)\b",
        ],
        "template": "Here's what VCs really look for — and nobody tells founders this.",
        "base_score": 0.83,
    },
    {
        "hook_type": "Shock / Controversy",
        "patterns": [
            r"\byou should (never|not|stop)\b",
            r"\bstop (doing|trying|using|building)\b",
            r"\bdon'?t (ever|do|use|build|raise)\b",
            r"\bfounders? (shouldn'?t|should never|must not)\b",
            r"\b\d{1,3}%\b.*\b(fail|wrong|lose|don't|never)\b",
            r"\b(shocking|controversial|unpopular opinion|hot take)\b",
            r"\bmost (people|founders?|startups?) (are wrong|get this wrong|fail)\b",
        ],
        "template": "Founders shouldn't raise money until THIS moment…",
        "base_score": 0.81,
    },
    {
        "hook_type": "Counterintuitive / Weird",
        "patterns": [
            r"\bcounterIintuitive\b", r"\bcounter-intuitive\b",
            r"\bsurprisingly\b", r"\bparadox\b", r"\bironic(ally)?\b",
            r"\bthe (best|top|most successful) .{0,30} (are|is) (not|actually|really)\b",
            r"\bwhat (if|most people miss)\b",
            r"\bthe opposite (is true|of what)\b",
            r"\bbreaks? (the rules?|expectations?|conventional wisdom)\b",
            r"\bunexpectedly\b", r"\bagainst (the grain|conventional wisdom)\b",
        ],
        "template": "The best founders are not logical — they're emotional.",
        "base_score": 0.78,
    },
    {
        "hook_type": "Big Promise",
        "patterns": [
            r"\bhere'?s (the thing|what|how)\b",
            r"\bthe secret (to|of|behind)\b",
            r"\bhow (i|we|you can) .{0,40} (in \d|without|with just)\b",
            r"\bthe (truth|real truth) about\b",
            r"\bwhat (no one|nobody) tells you\b",
            r"\b(today|in this (video|episode|podcast))[,\s].{0,40}(learn|show|reveal|share)\b",
            r"\bi('?m going to| will) (show|tell|reveal|share|teach) you\b",
            r"\bby the end of (this|today)\b",
        ],
        "template": "Here's the thing nobody tells you about X…",
        "base_score": 0.75,
    },
]


def _score_hook(hook_text: str) -> tuple[str, str, float, int]:
    text = hook_text.lower()
    best_type     = "Big Promise"
    best_template = _RULES[-1]["template"]
    best_score    = _RULES[-1]["base_score"]
    best_matches  = 0

    for rule in _RULES:
        matches = sum(
            1 for pattern in rule["patterns"]
            if re.search(pattern, text, re.IGNORECASE)
        )
        if matches > best_matches:
            best_matches  = matches
            best_type     = rule["hook_type"]
            best_template = rule["template"]
            best_score    = rule["base_score"]

    return best_type, best_template, best_score, best_matches


def _build_explanation(hook_type: str, hook_text: str, match_count: int) -> str:
    first_sentence = re.split(r'[.!?]', hook_text.strip())[0][:120].strip()
    confidence = "strongly" if match_count >= 2 else "likely"

    explanations = {
        "Big Promise": (
            f"The opening {confidence} sets up a bold promise or revelation. "
            f'Starting with: "{first_sentence}…" — this creates anticipation '
            "and tells the listener they will gain something valuable."
        ),
        "I Was Wrong": (
            f"The hook {confidence} uses vulnerability and belief reversal. "
            f'Opening: "{first_sentence}…" — sharing past failure builds trust '
            "and makes the turnaround highly relatable."
        ),
        "Shock / Controversy": (
            f"The opening {confidence} uses a polarising or controversial statement. "
            f'"{first_sentence}…" — this forces the listener to pay attention '
            "to either agree or disagree."
        ),
        "Insider Secret": (
            f"The hook {confidence} frames content as exclusive insider knowledge. "
            f'"{first_sentence}…" — implying the listener is gaining rare access '
            "triggers curiosity and a sense of privilege."
        ),
        "Tension Setup": (
            f"The opening {confidence} introduces conflict or tension that needs resolution. "
            f'"{first_sentence}…" — the unresolved problem keeps listeners engaged '
            "waiting for how it was solved."
        ),
        "Mini-Story Cold Open": (
            f"The hook {confidence} drops the listener into the middle of a live moment. "
            f'"{first_sentence}…" — starting mid-scene creates immediate emotional investment.'
        ),
        "Counterintuitive / Weird": (
            f"The opening {confidence} breaks expectations with a surprising insight. "
            f'"{first_sentence}…" — challenging conventional wisdom forces the listener '
            "to reconsider what they thought they knew."
        ),
    }
    return explanations.get(hook_type, f"Classified as {hook_type} based on opening language patterns.")


async def classify_hook(transcript: str) -> HookAnalysis:
    """
    Classify a transcript's opening as one of the 7 proven hook patterns.
    Fully local — no API key required.
    """
    hook_text = transcript[:600]

    hook_type, template, base_score, match_count = _score_hook(hook_text)

    if match_count == 0:
        strength = 0.55
    elif match_count == 1:
        strength = base_score
    else:
        strength = min(0.97, base_score + (match_count - 1) * 0.04)

    explanation = _build_explanation(hook_type, hook_text, match_count)

    logger.info(f"Hook classified as '{hook_type}' ({match_count} pattern matches, score={strength:.2f})")

    return HookAnalysis(
        hook_type=hook_type,
        template_match=template,
        strength_score=round(strength, 2),
        explanation=explanation,
    )