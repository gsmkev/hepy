import db
import forecasting.features as features


def test_build_feature_table_computes_lags(tmp_path):
    conn = db.connect(str(tmp_path / "t.db"))
    db.init_schema(conn)
    for i, value in enumerate([100.0, 101.0, 102.0, 103.0], start=1):
        db.write_index_daily(conn, f"2026-01-0{i}", "AGREGADO", value)

    rows = features.build_feature_table(conn, supermarket="AGREGADO", lags=[1])
    by_date = {r["date"]: r for r in rows}

    assert by_date["2026-01-01"]["lag_1"] is None
    assert by_date["2026-01-02"]["lag_1"] == 100.0
    assert by_date["2026-01-04"]["lag_1"] == 102.0
