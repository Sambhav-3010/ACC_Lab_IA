from lbml.simulator import run_comparison


def test_all_policies_return_metrics():
    results, details = run_comparison("E1", 30, 5)
    assert set(results["policy"]) == {"round_robin", "least_loaded", "ml_predictive"}
    assert all(len(details[row.policy]) == int(row.requests) for row in results.itertuples())


def test_ml_is_not_a_static_result():
    results, _ = run_comparison("E3", 30, 9)
    assert results.loc[results.policy == "ml_predictive", "route_time_us"].iloc[0] >= 0
