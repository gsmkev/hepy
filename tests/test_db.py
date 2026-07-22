import sqlite3
import db


def test_insert_and_read_price(tmp_path):
    conn = db.connect(str(tmp_path / "test.db"))
    db.init_schema(conn)
    db.insert_price(conn, "2026-07-22", "stock", "arroz_1kg", "Arroz 1kg", 6500.0, "https://stock.com.py/p/1")
    rows = db.read_prices(conn, product_key="arroz_1kg")
    assert len(rows) == 1
    assert rows[0]["supermarket"] == "stock"
    assert rows[0]["price"] == 6500.0
    assert rows[0]["is_outlier"] == 0


def test_delete_price_removes_only_the_matching_row(tmp_path):
    conn = db.connect(str(tmp_path / "test.db"))
    db.init_schema(conn)
    db.insert_price(conn, "2026-07-22", "stock", "arroz_1kg", "Arroz 1kg", 6500.0, "https://stock.com.py/p/1")
    db.insert_price(conn, "2026-07-22", "stock", "banana_1kg", "Banana 1kg", 5000.0, "https://stock.com.py/p/2")

    db.delete_price(conn, "2026-07-22", "stock", "banana_1kg")

    remaining = db.read_prices(conn, supermarket="stock")
    assert [r["product_key"] for r in remaining] == ["arroz_1kg"]


def test_delete_price_is_a_no_op_when_no_row_exists(tmp_path):
    conn = db.connect(str(tmp_path / "test.db"))
    db.init_schema(conn)
    db.delete_price(conn, "2026-07-22", "stock", "banana_1kg")  # must not raise
    assert db.read_prices(conn) == []


def test_index_daily_roundtrip(tmp_path):
    conn = db.connect(str(tmp_path / "test.db"))
    db.init_schema(conn)
    db.write_index_daily(conn, "2026-07-22", "AGREGADO", 100.0)
    db.write_index_daily(conn, "2026-07-23", "AGREGADO", 101.2)
    rows = db.read_index_daily(conn, supermarket="AGREGADO")
    assert [r["value"] for r in rows] == [100.0, 101.2]
