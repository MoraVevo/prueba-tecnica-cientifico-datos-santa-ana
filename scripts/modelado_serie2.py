"""Modelos y selección de señales actuales del sensor virtual de Serie II."""

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import RFE
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


OBJETIVO = "ZZQBCHLL.AV_0#"


def crear_modelos():
    """Hiperparámetros fijos; imputación y escalado se ajustan solo con fit."""
    return {
        "Ridge": make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=100)),
        "Bosque aleatorio": make_pipeline(
            SimpleImputer(strategy="median"),
            RandomForestRegressor(
                n_estimators=80, max_depth=14, min_samples_leaf=20,
                max_features=0.8, max_samples=0.65, n_jobs=2, random_state=42,
            ),
        ),
        "HistGradientBoosting": make_pipeline(
            SimpleImputer(strategy="median"),
            HistGradientBoostingRegressor(
                max_iter=150, max_leaf_nodes=15, min_samples_leaf=60,
                learning_rate=0.07, l2_regularization=1, early_stopping=False, random_state=42,
            ),
        ),
    }


def seleccionar_variables(entradas, objetivo):
    """Retira señales progresivamente con Ridge hasta conservar quince, solo en entrenamiento."""
    selector = make_pipeline(
        SimpleImputer(strategy="median"), StandardScaler(),
        RFE(Ridge(alpha=100), n_features_to_select=15, step=1),
    ).fit(entradas, objetivo)
    columnas = entradas.columns[selector[-1].support_].tolist()
    posiciones = pd.Series(selector[-1].ranking_, index=entradas.columns, name="posicion_RFE")
    return columnas, posiciones


def calcular_metricas(observado, estimado):
    """Errores en unidades originales; WAPE no se interpreta como MAE porcentual."""
    observado, estimado = np.asarray(observado), np.asarray(estimado)
    if not np.isfinite(observado).all() or not np.isfinite(estimado).all():
        raise ValueError("Observaciones y predicciones deben ser finitas.")
    return {
        "MAE": mean_absolute_error(observado, estimado),
        "RMSE": np.sqrt(mean_squared_error(observado, estimado)),
        "R2": r2_score(observado, estimado),
        "sesgo": np.mean(estimado - observado),
        "WAPE_pct": 100 * np.abs(estimado - observado).sum() / np.abs(observado).sum(),
        "error_abs_p95": np.quantile(np.abs(estimado - observado), 0.95),
    }
