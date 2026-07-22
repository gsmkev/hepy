import db
import index

TOY_BASKET = [
    {"product_key": "arroz", "bcp_category": "cereales", "weight": 0.6},
    {"product_key": "aceite", "bcp_category": "aceites", "weight": 0.4},
]


def _seed(conn):
    # Day 1: base prices. Day 2: arroz +10%, aceite unchanged.
    db.insert_price(conn, "2026-07-01", "stock", "arroz", "Arroz", 100.0, "u")
    db.insert_price(conn, "2026-07-01", "stock", "aceite", "Aceite", 200.0, "u")
    db.insert_price(conn, "2026-07-02", "stock", "arroz", "Arroz", 110.0, "u")
    db.insert_price(conn, "2026-07-02", "stock", "aceite", "Aceite", 200.0, "u")


def test_compute_daily_index_single_supermarket(tmp_path):
    conn = db.connect(str(tmp_path / "t.db"))
    db.init_schema(conn)
    _seed(conn)

    result = index.compute_daily_index(conn, TOY_BASKET, "stock")

    assert result["2026-07-01"] == 100.0
    # weighted geometric mean of (1.10 for arroz, 1.00 for aceite) with weights 0.6/0.4
    expected_change = 1.10 ** 0.6 * 1.00 ** 0.4
    assert abs(result["2026-07-02"] - 100.0 * expected_change) < 1e-6


def test_compute_daily_index_excludes_outliers(tmp_path):
    conn = db.connect(str(tmp_path / "t.db"))
    db.init_schema(conn)
    _seed(conn)
    # Day 2 arroz price flagged as an outlier — should be excluded from the change
    db.insert_price(conn, "2026-07-02", "stock", "arroz", "Arroz", 110.0, "u", is_outlier=True)

    result = index.compute_daily_index(conn, TOY_BASKET, "stock")
    # only aceite (unchanged) contributes -> index stays at 100
    assert abs(result["2026-07-02"] - 100.0) < 1e-6


def test_compute_aggregate_index_averages_supermarkets(tmp_path):
    conn = db.connect(str(tmp_path / "t.db"))
    db.init_schema(conn)
    _seed(conn)
    db.insert_price(conn, "2026-07-01", "salemma", "arroz", "Arroz", 100.0, "u")
    db.insert_price(conn, "2026-07-01", "salemma", "aceite", "Aceite", 200.0, "u")
    db.insert_price(conn, "2026-07-02", "salemma", "arroz", "Arroz", 100.0, "u")  # no change at salemma
    db.insert_price(conn, "2026-07-02", "salemma", "aceite", "Aceite", 200.0, "u")

    result = index.compute_aggregate_index(conn, TOY_BASKET, ["stock", "salemma"])
    assert result["2026-07-01"] == 100.0
    stock_day2 = 100.0 * (1.10 ** 0.6 * 1.00 ** 0.4)
    salemma_day2 = 100.0
    assert abs(result["2026-07-02"] - (stock_day2 + salemma_day2) / 2) < 1e-6
