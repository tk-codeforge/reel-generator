import os
import joblib

from services.analysis.trend_detector import trend_score
from services.analysis.hook_scorer import hook_score

MODEL_PATH = "models/viral_model.pkl"

# Load model once
model = None
if os.path.exists(MODEL_PATH):
    try:
        model = joblib.load(MODEL_PATH)
        print("✅ ML model loaded")
    except Exception as e:
        print("❌ Failed to load model:", e)


def score_segment(text: str, position: float) -> float:
    """
    position: 0 → start, 1 → end
    """

    # ── Rule-based scoring ─────────────────────────────
    trend = trend_score(text)
    hook = hook_score(text)
    position_weight = 1 - position

    rule_score = (
        0.5 * trend +
        0.3 * hook +
        0.2 * position_weight
    )

    # ── ML scoring ────────────────────────────────────
    ml_score = 0.0

    if model:
        try:
            length = len(text)
            engagement = 0.05  # fallback

            features = [[position, length, engagement]]
            ml_score = model.predict_proba(features)[0][1]

        except Exception as e:
            print("ML scoring failed:", e)

    # ── Combine ───────────────────────────────────────
    final_score = (0.6 * ml_score) + (0.4 * rule_score)

    # Optional filtering
    if final_score < 0.3:
        return 0

    return final_score