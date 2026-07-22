import db


def build_feature_table(conn, supermarket: str = "AGREGADO", lags: list[int] | None = None) -> list[dict]:
    lags = lags or [1, 7, 30]
    series = db.read_index_daily(conn, supermarket=supermarket)
    dates = [r["date"] for r in series]
    values = {r["date"]: r["value"] for r in series}

    rows: list[dict] = []
    for i, date in enumerate(dates):
        row = {"date": date, "index_value": values[date]}
        for lag in lags:
            row[f"lag_{lag}"] = values[dates[i - lag]] if i - lag >= 0 else None
        rows.append(row)
    return rows
