"""Hospital ranking utilities: Success-Adjusted Value ranking.

This module provides functions to compute a normalized, success-adjusted
value score for a list of candidate hospitals/procedures. The functions
accept simple candidate dicts (as returned from repositories or demo data)
and return the same list annotated with `value_score` and other helper
fields. Scores are normalized to be comparable and higher-is-better.
"""

from typing import List, Dict
import math


def _safe_float(v, default=0.0):
    try:
        return float(v) if v is not None else default
    except Exception:
        return default


def compute_success_adjusted_scores(candidates: List[Dict]) -> List[Dict]:
    """Compute Success-Adjusted Value scores for candidate hospitals.

    Algorithm (high level):
    - Normalize numeric components (price, success_rate, complication_rate)
      into 0-1 range across the candidate set.
    - Compute accreditation weight (JCI > NABH > none) mapped into 0.7-1.0.
    - Combine components into final score:
        score = price_component * success_component * (1 - complication_component) * accreditation_weight

    Returns candidates annotated with `value_score` (float) and
    `normalized_price`, `price_component`, `success_norm`, `complication_norm`.
    """

    if not candidates:
        return candidates

    # Extract total prices (estimated_total_usd if present else base_price+others)
    prices = []
    for c in candidates:
        if c.get("estimated_total_usd"):
            prices.append(_safe_float(c.get("estimated_total_usd")))
        else:
            total = _safe_float(c.get("price") or c.get("base_price"))
            total += _safe_float(c.get("facility_fee"))
            total += _safe_float(c.get("anesthesia_fee"))
            total += _safe_float(c.get("surgeon_fee"))
            prices.append(total)

    min_price = min(prices)
    max_price = max(prices)
    price_span = max_price - min_price if max_price > min_price else 1.0

    # Normalize success and complication rates as percentages -> 0-1
    successes = [_safe_float(c.get("success_rate")) / 100.0 for c in candidates]
    comps = [_safe_float(c.get("complication_rate")) / 100.0 for c in candidates]

    # Clamping helpers
    def clamp01(x: float) -> float:
        return max(0.0, min(1.0, x))

    results = []
    for i, c in enumerate(candidates):
        price = prices[i]
        normalized_price = (price - min_price) / price_span
        # price_component: cheaper hospitals score higher -> invert normalized price
        price_component = clamp01(1.0 - normalized_price)

        success_norm = clamp01(successes[i]) if successes[i] is not None else 0.7
        complication_norm = clamp01(comps[i]) if comps[i] is not None else 0.05

        # Accreditation weighting: prefer JCI then NABH then none
        accreditation_weight = 0.7
        if c.get("jci_accredited"):
            accreditation_weight = 1.0
        elif c.get("nabh_accredited"):
            accreditation_weight = 0.9

        # Final score combination
        score = price_component * success_norm * (1.0 - complication_norm) * accreditation_weight

        enriched = dict(c)
        enriched.update(
            {
                "normalized_price": normalized_price,
                "price_component": price_component,
                "success_norm": success_norm,
                "complication_norm": complication_norm,
                "accreditation_weight": accreditation_weight,
                "value_score": round(score * 100.0, 4),
            }
        )
        results.append(enriched)

    # Sort descending by score
    results.sort(key=lambda x: x.get("value_score", 0), reverse=True)

    # Return top 20 by default caller can slice further
    return results
