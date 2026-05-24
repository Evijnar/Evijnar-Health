from app.services import demo_catalog
from app.services import ranking as ranking_service


def test_demo_search_and_ranking():
    results = demo_catalog.search_hospitals("27447")
    assert results, "Demo catalog should return hospitals for known CPT"

    ranked = ranking_service.compute_success_adjusted_scores(results)
    assert ranked
    assert all("value_score" in r for r in ranked)
    # Ensure sorted
    values = [r["value_score"] for r in ranked]
    assert values == sorted(values, reverse=True)
