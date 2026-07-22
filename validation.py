import datetime
import statistics


def _shift_date(date_str: str, days: int) -> str:
    d = datetime.date.fromisoformat(date_str) + datetime.timedelta(days=days)
    return d.isoformat()


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2 or len(ys) < 2:
        return None
    mean_x, mean_y = statistics.fmean(xs), statistics.fmean(ys)
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den_x = sum((x - mean_x) ** 2 for x in xs) ** 0.5
    den_y = sum((y - mean_y) ** 2 for y in ys) ** 0.5
    if den_x == 0 or den_y == 0:
        return None
    return num / (den_x * den_y)


def correlate_with_official(
    hepy_series: dict[str, float], ipc_series: dict[str, float], max_lag_days: int = 30
) -> dict:
    best_lag = 0
    best_corr: float | None = None

    for lag in range(-max_lag_days, max_lag_days + 1):
        xs, ys = [], []
        for date, hepy_value in hepy_series.items():
            shifted = _shift_date(date, lag)
            if shifted in ipc_series:
                xs.append(hepy_value)
                ys.append(ipc_series[shifted])
        corr = _pearson(xs, ys)
        if corr is not None and (best_corr is None or abs(corr) > abs(best_corr) or (abs(corr) == abs(best_corr) and abs(lag) < abs(best_lag))):
            best_corr = corr
            best_lag = lag

    return {"best_lag_days": best_lag, "correlation": best_corr}
