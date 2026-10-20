"""Verifica tiempo disponible, persistencia causal y preparación de anomalías."""

import numpy as np
import pandas as pd

from scripts.anomalias_serie2 import crear_detector, contexto_cerrado, simular_aviso, episodios_marcados


def test_regimen_no_se_utiliza_antes_de_cerrar_el_minuto():
    fechas = pd.Series(pd.date_range("2022-01-01", periods=25, freq="5s"))
    referencias = pd.DataFrame({"disponible_desde": pd.to_datetime(["2022-01-01 00:01", "2022-01-01 00:02"]),
                                "regimen": [1, 2]})
    contexto = contexto_cerrado(fechas, referencias)
    assert contexto.regimen_cerrado.tolist() == [0]*12+[1]*12+[2]
    assert contexto.disponible_desde.iloc[:12].isna().all()
    assert contexto.disponible_desde.iloc[12:].le(fechas.iloc[12:]).all()


def test_aviso_agrupa_y_no_cambia_el_pasado_al_alterar_el_futuro():
    candidatas = pd.Series([False]*5+[True]*3+[False]*12+[True]*20)
    resultado = simular_aviso(candidatas)
    assert resultado.inicio_aviso.iloc[7] and resultado.cierre_aviso.iloc[19]
    assert resultado.activo.iloc[7:19].all() and not resultado.activo.iloc[19]
    alteradas = candidatas.copy()
    alteradas.iloc[20:] = False
    pd.testing.assert_frame_equal(resultado.iloc[:20], simular_aviso(alteradas).iloc[:20])


def test_episodio_conserva_ultima_lectura_y_cobertura():
    fechas = pd.date_range("2022-01-01", periods=5, freq="5s")
    episodios = episodios_marcados(fechas, [False, True, True, False, True])
    assert episodios.lecturas.tolist() == [2, 1]
    assert episodios.cobertura_s.tolist() == [10, 5]
    assert episodios.fin.iloc[-1] == fechas[-1]+pd.Timedelta(seconds=5)


def test_imputacion_del_detector_no_aprende_de_las_lecturas_evaluadas():
    rng = np.random.default_rng(42)
    train = pd.DataFrame(rng.normal(size=(1100, 3)), columns=["A", "B", "C"])
    train.loc[0, "A"] = np.nan
    detector = crear_detector().fit(train)
    medianas = detector[0].statistics_.copy()
    detector.score_samples(pd.DataFrame({"A": [np.nan, 1e6], "B": [1e6, 0], "C": [-1e6, 0]}))
    np.testing.assert_allclose(medianas, train.median())
    np.testing.assert_array_equal(medianas, detector[0].statistics_)
