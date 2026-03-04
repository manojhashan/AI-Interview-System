"""
services/xai_explainer.py
--------------------------
Explainable AI (XAI) Feedback Engine
======================================
Uses SHAP (Shapley Additive Explanations) principles to explain
why each score was assigned, providing transparent, rule-based
feedback for every modality.

SHAP for a weighted linear model:
  phi_i = w_i * (x_i - baseline)

Where:
  w_i      = modality weight (Vocal 0.4, Facial 0.4, Semantic 0.2)
  x_i      = actual score for modality i
  baseline = expected/average score (set to 70 as interview baseline)
"""

# ── Constants ─────────────────────────────────────────────────────────────────
BASELINE_SCORE = 70.0   # Expected average interview score

WEIGHTS = {
    "vocal":    0.4,
    "facial":   0.4,
    "semantic": 0.2,
}

# ── SHAP Contribution Calculator ──────────────────────────────────────────────
# XAI Step 1: Calculate how much each modality pushed the score UP or DOWN
# relative to the expected baseline (70). This is the core SHAP formula:
#   φᵢ = wᵢ × (scoreᵢ − baseline)

def compute_shap_contributions(vocal: float, facial: float, semantic: float) -> dict:
    """
    XAI — SHAP Contribution Calculation
    Computes Shapley values for each modality.
    phi_i = w_i * (x_i - baseline)

    Positive phi → modality boosted the overall score above baseline.
    Negative phi → modality pulled the overall score below baseline.
    """
    contributions = {
        "vocal":    round(WEIGHTS["vocal"]    * (vocal    - BASELINE_SCORE), 2),
        "facial":   round(WEIGHTS["facial"]   * (facial   - BASELINE_SCORE), 2),
        "semantic": round(WEIGHTS["semantic"] * (semantic - BASELINE_SCORE), 2),
    }
    return contributions


# ── Per-Modality Rule-Based Explanations ─────────────────────────────────────
# XAI Step 2: Convert raw scores + SHAP values into human-readable explanations
# Each function generates a transparent sentence telling the candidate
# exactly how that modality contributed to their overall score.

def _explain_vocal(score: float, phi: float) -> str:
    # XAI — Vocal Transparency: shows quality level + SHAP contribution direction
    """Generate transparent vocal explanation based on score range + SHAP value."""
    direction = f"contributed {abs(phi):+.1f} pts to overall score"

    if score >= 85:
        quality = "Excellent vocal delivery — strong pitch control and confident speech rate."
    elif score >= 70:
        quality = "Good vocal projection — clear articulation with minor hesitations."
    elif score >= 55:
        quality = "Moderate vocal performance — noticeable speech rate inconsistency or pauses."
    else:
        quality = "Weak vocal delivery — frequent hesitations or low energy detected."

    impact = (
        f"[+XAI] Vocal score ({score:.0f}%) {direction}. "
        f"{'This positively impacted your overall result.' if phi >= 0 else 'This pulled your overall score below baseline.'} "
        f"{quality}"
    )
    return impact


def _explain_facial(score: float, phi: float, dominant_emotion: str = "Neutral") -> str:
    # XAI — Facial Transparency: includes dominant emotion detected during interview
    """Generate transparent facial explanation based on score, SHAP value, and emotion."""
    direction = f"contributed {abs(phi):+.1f} pts to overall score"

    if score >= 85:
        quality = "High confidence facial composure — positive expressions and stable eye contact."
    elif score >= 70:
        quality = "Good facial engagement — professional expression maintained."
    elif score >= 55:
        quality = "Moderate composure — some emotional fluctuation detected across frames."
    else:
        quality = "Low confidence signals — expressions showed significant anxiety or instability."

    emotion_note = {
        "Happy":    "Dominant emotion was Happy — builds great rapport with interviewers.",
        "Neutral":  "Dominant emotion was Neutral — professional and composed.",
        "Surprise": "Dominant emotion was Surprise — try to remain composed under pressure.",
        "Angry":    "Dominant emotion was Angry — relax facial muscles to appear approachable.",
        "Fear":     "Dominant emotion was Fear — deep breaths can reduce visible nervousness.",
        "Sad":      "Dominant emotion was Sad — maintain enthusiasm and upbeat expressions.",
        "Disgust":  "Dominant emotion was Disgust — be mindful of dismissive expressions.",
    }.get(dominant_emotion, "Maintain a confident, open expression throughout the interview.")

    impact = (
        f"[+XAI] Facial score ({score:.0f}%) {direction}. "
        f"{'Positively impacted overall result.' if phi >= 0 else 'Pulled overall score below baseline.'} "
        f"{quality} {emotion_note}"
    )
    return impact


def _explain_semantic(score: float, phi: float) -> str:
    # XAI — Semantic Transparency: shows how relevant the answer was to the question
    """Generate transparent semantic explanation based on cosine similarity score + SHAP value."""
    direction = f"contributed {abs(phi):+.1f} pts to overall score"

    if score >= 80:
        quality = "Answer was highly relevant — strong alignment with the question context."
    elif score >= 60:
        quality = "Good relevance — core question addressed with adequate depth."
    elif score >= 40:
        quality = "Moderate relevance — answer touched the topic but lacked specificity."
    elif score >= 20:
        quality = "Low relevance — answer drifted from the specific question asked."
    else:
        quality = "Answer did not address the question — focus on the key concepts asked."

    impact = (
        f"[+XAI] Semantic score ({score:.0f}%) {direction}. "
        f"{'Positively impacted overall result.' if phi >= 0 else 'Pulled overall score below baseline.'} "
        f"{quality}"
    )
    return impact


# ── Main XAI Entry Point ───────────────────────────────────────────────────────
# XAI Step 3: Aggregate all modality explanations + identify strongest/weakest
# modality and generate a transparent overall summary for the candidate.

def generate_xai_feedback(
    vocal_score: float,
    facial_score: float,
    semantic_score: float,
    overall_score: float,
    dominant_emotion: str = "Neutral"
) -> dict:
    """
    Generate Explainable AI feedback for one interview answer.

    Returns
    -------
    dict with keys:
        - contributions  : SHAP phi values per modality
        - strongest      : modality that helped the most
        - weakest        : modality that hurt the most
        - vocal_xai      : explainable vocal feedback string
        - facial_xai     : explainable facial feedback string
        - semantic_xai   : explainable semantic feedback string
        - summary_xai    : overall transparent explanation
    """
    # XAI Step 1 — Compute SHAP φ for each modality
    phi = compute_shap_contributions(vocal_score, facial_score, semantic_score)

    # XAI Step 2 — Generate per-modality transparent explanations
    vocal_xai    = _explain_vocal(vocal_score, phi["vocal"])
    facial_xai   = _explain_facial(facial_score, phi["facial"], dominant_emotion)
    semantic_xai = _explain_semantic(semantic_score, phi["semantic"])

    # XAI Step 3 — Identify which modality helped most and which hurt most
    strongest = max(phi, key=phi.get)
    weakest   = min(phi, key=phi.get)

    # Build transparent overall summary
    gap_from_baseline = round(overall_score - BASELINE_SCORE, 1)
    if gap_from_baseline >= 10:
        verdict = "Well above average — strong multimodal performance."
    elif gap_from_baseline >= 0:
        verdict = "Above baseline — overall performance is satisfactory."
    elif gap_from_baseline >= -10:
        verdict = "Slightly below baseline — improvement needed in weaker areas."
    else:
        verdict = "Below baseline — significant improvement required across modalities."

    summary_xai = (
        f"[XAI Summary] Overall score {overall_score:.0f}% is {abs(gap_from_baseline):.1f} pts "
        f"{'above' if gap_from_baseline >= 0 else 'below'} the baseline of {BASELINE_SCORE:.0f}%. "
        f"Strongest modality: {strongest.capitalize()} (SHAP: {phi[strongest]:+.1f}). "
        f"Weakest modality: {weakest.capitalize()} (SHAP: {phi[weakest]:+.1f}). "
        f"{verdict}"
    )

    return {
        "contributions": phi,
        "strongest":     strongest,
        "weakest":       weakest,
        "vocal_xai":     vocal_xai,
        "facial_xai":    facial_xai,
        "semantic_xai":  semantic_xai,
        "summary_xai":   summary_xai,
    }
