"""Comprueba selección de señales actuales, aislamiento del ajuste y métricas."""

import numpy as np
import pandas as pd
import pytest

from scripts.modelado_serie2 import (
    calcular_metricas, crear_modelos, seleccionar_variables,
)


def test_seleccion_conserva_quince_y_es_invariante_a_cambio_de_unidades():
    generador = np.random.default_rng(42)
    entradas = pd.DataFrame(generador.normal(size=(500, 29)), columns=[f"S{i}" for i in range(29)])
    objetivo = 4 * entradas.S0 + 3 * entradas.S1 + 2 * entradas.S2
    original = entradas.copy(deep=True)
    columnas, posiciones = seleccionar_variables(entradas, objetivo)
    cambiadas = entradas.copy()
    cambiadas.S0 = cambiadas.S0 * 1000 + 500
    otras, _ = seleccionar_variables(cambiadas, objetivo)
    assert len(columnas) == 15 and posiciones.eq(1).sum() == 15
    assert {"S0", "S1", "S2"}.issubset(columnas)
    assert columnas == otras
    pd.testing.assert_frame_equal(entradas, original)


@pytest.mark.parametrize("nombre", ["Ridge", "Bosque aleatorio", "HistGradientBoosting"])
def test_imputacion_no_se_actualiza_con_la_evaluacion(nombre):
    entradas = pd.DataFrame({"A": [1, 2, 3, 4, 5, np.nan] * 30, "B": np.arange(180)})
    objetivo = pd.Series(np.arange(180) / 100 + 50)
    modelo = crear_modelos()[nombre].fit(entradas, objetivo)
    medianas = modelo[0].statistics_.copy()
    np.testing.assert_allclose(medianas, [3, 89.5])
    prediccion = modelo.predict(pd.DataFrame({"A": [np.nan, 1e6], "B": [-1e6, 1e6]}))
    assert np.isfinite(prediccion).all()
    np.testing.assert_array_equal(modelo[0].statistics_, medianas)


def test_no_elimina_automaticamente_pareja_correlacionada_con_aporte_conjunto():
    generador = np.random.default_rng(10)
    entradas = pd.DataFrame(generador.normal(size=(500, 29)), columns=[f"S{i}" for i in range(29)])
    entradas.S1 = entradas.S0 + generador.normal(scale=0.1, size=500)
    objetivo = 20 * (entradas.S0 - entradas.S1)
    assert entradas.S0.corr(entradas.S1) > 0.95
    columnas, _ = seleccionar_variables(entradas, objetivo)
    assert {"S0", "S1"}.issubset(columnas)


def test_metricas_signo_del_sesgo_escala_y_rechazo_de_infinitos():
    resultado = calcular_metricas([10, 20, 30], [12, 19, 33])
    assert resultado["MAE"] == 2
    assert resultado["RMSE"] == pytest.approx(np.sqrt(14 / 3))
    assert resultado["sesgo"] == pytest.approx(4 / 3)
    assert resultado["WAPE_pct"] == 10
    with pytest.raises(ValueError, match="finitas"):
        calcular_metricas([10, 20], [np.inf, np.nan])
