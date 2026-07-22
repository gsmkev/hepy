from outliers import is_outlier

def test_no_outlier_with_stable_prices():
    history = [6500.0, 6520.0, 6480.0, 6510.0, 6495.0]
    assert is_outlier(history, 6505.0) is False

def test_flags_a_price_spike():
    history = [6500.0, 6520.0, 6480.0, 6510.0, 6495.0]
    assert is_outlier(history, 65000.0) is True  # 10x jump

def test_flags_a_price_crash():
    history = [6500.0, 6520.0, 6480.0, 6510.0, 6495.0]
    assert is_outlier(history, 650.0) is True  # 10x drop

def test_insufficient_history_never_flags():
    assert is_outlier([6500.0], 65000.0) is False
    assert is_outlier([], 65000.0) is False

def test_zero_or_negative_price_always_flagged():
    history = [6500.0, 6520.0, 6480.0, 6510.0, 6495.0]
    assert is_outlier(history, 0.0) is True
    assert is_outlier(history, -10.0) is True
    assert is_outlier([], -10.0) is True  # even with no history at all
