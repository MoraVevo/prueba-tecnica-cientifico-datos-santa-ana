"""Comprueba conservación, disponibilidad temporal e independencia del caudal."""

import numpy as np
import pandas as pd

from scripts.regimenes_serie2 import ENTRADAS, FAMILIAS, PESOS, PRESIONES_HOGAR, construir_vista, resumir_episodios


def test_vista_conserva_filas_y_no_consulta_caudal_para_entradas():
    columnas = [c for c in ENTRADAS if c != "presion_hogar_sintesis"] + PRESIONES_HOGAR
    datos = pd.DataFrame({c: np.arange(24, dtype=float) + i for i,c in enumerate(columnas)})
    datos.insert(0, "date", pd.date_range("2022-03-27 14:28:54", periods=24, freq="5s"))
    datos["ZZQBCHLL.AV_0#"] = np.arange(24) * 10
    original = datos.copy()
    vista, entradas, correspondencia = construir_vista(datos)
    alterados = datos.copy()
    alterados["ZZQBCHLL.AV_0#"] = -1e12
    _, otras, _ = construir_vista(alterados)
    pd.testing.assert_frame_equal(entradas, otras)
    pd.testing.assert_frame_equal(datos, original)
    assert len(vista) == 2 and vista.filas_fuente.eq(12).all()
    np.testing.assert_array_equal(correspondencia.fila_fuente, np.arange(24))
    assert correspondencia.intervalo.tolist() == [0]*12 + [1]*12
    assert entradas.iloc[0, 0] == datos.iloc[:12][ENTRADAS[0]].median()
    assert correspondencia.date.lt(correspondencia.intervalo.map(vista.disponible_desde)).all()


def test_familias_tienen_igual_peso_total_y_episodios_incluyen_intervalo_final():
    for columnas in FAMILIAS.values():
        np.testing.assert_allclose((PESOS[columnas]**2).sum(), 1)
    inicio = pd.date_range("2022-01-01", periods=5, freq="1min")
    vista = pd.DataFrame({"inicio": inicio, "disponible_desde": inicio+pd.Timedelta(minutes=1)})
    episodios = resumir_episodios(vista, [1, 1, 2, 2, 1])
    assert episodios.regimen.tolist() == [1, 2, 1]
    assert episodios.minutos.tolist() == [2, 2, 1]
