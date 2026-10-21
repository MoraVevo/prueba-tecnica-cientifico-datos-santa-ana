"""Comprobaciones de dirección temporal y aislamiento de los rezagos."""

import numpy as np
import pandas as pd
import pytest

from experimentos.rezagos_serie2 import construir_rezagos, explorar_correlaciones, seleccionar_rezagos


def test_rezago_usa_solo_pasado_y_exige_rejilla():
    fechas = pd.date_range("2022-01-01", periods=200, freq="10s")
    x = pd.DataFrame({"sensor": np.arange(200.0)}, index=fechas)
    pasado = construir_rezagos(x, 30)
    assert pasado.iloc[:3].isna().all().all()
    np.testing.assert_array_equal(pasado.iloc[3:, 0], np.arange(197.0))
    with pytest.raises(AssertionError):
        construir_rezagos(x.drop(fechas[20]), 30)


def test_eleccion_rezago_aislada_de_cualquier_valor_futuro():
    rng = np.random.default_rng(21)
    fechas = pd.date_range("2022-01-01", periods=600, freq="10s")
    x = pd.DataFrame({"sensor": rng.normal(size=600)}, index=fechas)
    y = x.sensor.shift(3)
    mascara = (np.arange(600) >= 66) & (np.arange(600) < 400)
    esperado = explorar_correlaciones(x, y, mascara)
    assert seleccionar_rezagos(esperado).rezago_s.iloc[0] == 30
    x.loc[fechas[400]:] = rng.normal(1e6, 1e4, (200, 1))
    y.loc[fechas[400]:] = -1e8
    pd.testing.assert_frame_equal(explorar_correlaciones(x, y, mascara), esperado)
