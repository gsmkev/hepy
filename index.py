import math
import statistics

import db


def _prices_by_date(conn, supermarket: str, product_key: str) -> dict[str, float]:
    rows = db.read_prices(conn, product_key=product_key, supermarket=supermarket)
    return {r["date"]: r["price"] for r in rows if not r["is_outlier"]}


def compute_daily_index(conn, basket: list[dict], supermarket: str) -> dict[str, float]:
    per_product_prices = {
        item["product_key"]: _prices_by_date(conn, supermarket, item["product_key"])
        for item in basket
    }
    all_dates = sorted({d for prices in per_product_prices.values() for d in prices})
    if not all_dates:
        return {}

    result: dict[str, float] = {all_dates[0]: 100.0}
    for prev_date, date in zip(all_dates, all_dates[1:]):
        ratios_weights: list[tuple[float, float]] = []
        for item in basket:
            prices = per_product_prices[item["product_key"]]
            if prev_date in prices and date in prices and prices[prev_date] > 0:
                ratios_weights.append((prices[date] / prices[prev_date], item["weight"]))

        if not ratios_weights:
            change = 1.0
        else:
            total_weight = sum(w for _, w in ratios_weights)
            log_change = sum(w * math.log(r) for r, w in ratios_weights) / total_weight
            change = math.exp(log_change)

        result[date] = result[prev_date] * change

    return result


def compute_aggregate_index(conn, basket: list[dict], supermarkets: list[str]) -> dict[str, float]:
    per_market = {sm: compute_daily_index(conn, basket, sm) for sm in supermarkets}
    all_dates = sorted({d for series in per_market.values() for d in series})
    aggregate: dict[str, float] = {}
    for date in all_dates:
        values = [series[date] for series in per_market.values() if date in series]
        if values:
            aggregate[date] = statistics.fmean(values)

    for sm, series in per_market.items():
        for date, value in series.items():
            db.write_index_daily(conn, date, sm, value)
    for date, value in aggregate.items():
        db.write_index_daily(conn, date, "AGREGADO", value)

    return aggregate
