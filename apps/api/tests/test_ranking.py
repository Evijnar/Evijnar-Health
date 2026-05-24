import pytest

from app.services.ranking import compute_success_adjusted_scores


def test_compute_scores_basic_ordering():
    candidates = [
        {"hospital_id": "a", "price": 50000, "success_rate": 0.95, "complication_rate": 0.02, "jci_accredited": True},
        {"hospital_id": "b", "price": 10000, "success_rate": 0.90, "complication_rate": 0.05, "jci_accredited": False},
        {"hospital_id": "c", "price": 20000, "success_rate": 0.98, "complication_rate": 0.015, "jci_accredited": True},
    ]

    scored = compute_success_adjusted_scores(candidates)

    # Should annotate value_score and be sorted desc
    assert len(scored) == 3
    assert all("value_score" in s for s in scored)

    scores = [s["value_score"] for s in scored]
    # descending
    assert scores[0] >= scores[1] >= scores[2]

