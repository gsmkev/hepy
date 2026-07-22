import math
import statistics


def is_outlier(history: list[float], new_price: float, threshold: float = 3.5) -> bool:
    """Flag new_price as an outlier relative to history using a robust
    z-score (MAD-based) on the log price. Returns False if there isn't
    enough history (< 3 points) to judge.
    """
    if len(history) < 3 or new_price <= 0:
        return False

    log_history = [math.log(p) for p in history if p > 0]
    if len(log_history) < 3:
        return False

    median = statistics.median(log_history)
    deviations = [abs(x - median) for x in log_history]
    mad = statistics.median(deviations)

    if mad == 0:
        # no variation in history at all — flag any change as an outlier
        return math.log(new_price) != median

    # 0.6745 makes MAD comparable to a standard deviation for normal data
    robust_z = abs((math.log(new_price) - median) * 0.6745 / mad)
    return robust_z > threshold
