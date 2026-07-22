from validation import correlate_with_official


def test_perfect_correlation_at_zero_lag():
    hepy = {"2026-01-01": 100.0, "2026-01-02": 101.0, "2026-01-03": 102.0, "2026-01-04": 103.0}
    ipc = {"2026-01-01": 200.0, "2026-01-02": 202.0, "2026-01-03": 204.0, "2026-01-04": 206.0}

    result = correlate_with_official(hepy, ipc, max_lag_days=2)
    assert result["best_lag_days"] == 0
    assert result["correlation"] > 0.99


def test_no_overlapping_dates_returns_none_correlation():
    hepy = {"2020-01-01": 100.0}
    ipc = {"2030-01-01": 200.0}
    result = correlate_with_official(hepy, ipc, max_lag_days=1)
    assert result["correlation"] is None
