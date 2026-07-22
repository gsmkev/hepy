"""Fase 2 — nowcasting del IPC-BCP oficial. No implementar hasta acumular
6-12 meses de historia en prices.db / index_daily (ver design doc
2026-07-22-hepy-indice-precios-design, sección "Fase 2").
"""


def ridge_baseline(feature_table: list[dict], target: list[float]):
    """Planned: sklearn.linear_model.RidgeCV sobre feature_table (ver
    forecasting.features.build_feature_table) contra la variación
    intermensual del IPC-BCP oficial. Punto de partida interpretable.
    """
    raise NotImplementedError("Fase 2 — esperar 6-12 meses de historia acumulada")


def gbm_baseline(feature_table: list[dict], target: list[float]):
    """Planned: XGBoost o LightGBM sobre las mismas features que ridge_baseline.
    Es el modelo que domina la literatura reciente de nowcasting de inflación
    en economías en desarrollo (ver Bolivar 2025 en el design doc)."""
    raise NotImplementedError("Fase 2 — esperar 6-12 meses de historia acumulada")


def sarimax_baseline(index_series: list[float]):
    """Planned: statsmodels SARIMAX como benchmark econométrico clásico,
    obligatorio para poder decir "el modelo de ML mejora sobre X%"."""
    raise NotImplementedError("Fase 2 — esperar 6-12 meses de historia acumulada")
