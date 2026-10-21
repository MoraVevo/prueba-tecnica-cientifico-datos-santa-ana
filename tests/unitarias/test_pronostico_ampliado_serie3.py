"""Disponibilidad temporal y selección de la comparación ampliada."""

import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from scripts.ampliar_pronostico_serie3 import (
    CANDIDATOS, COMPLETOS, construir_rasgos, predecir, elegir,
)


def fuente_sintetica():
    fechas = pd.bdate_range("2014-01-01", "2024-06-24")
    i = np.arange(len(fechas))
    precio = 20+2*np.sin(i/30)+i/500
    return pd.DataFrame({"date": fechas.astype(str), "open": precio*1.001,
        "high": precio*1.01, "low": precio*.99, "close": precio,
        "volume": 100+i % 70})


def test_rasgos_y_todas_las_familias_son_invariantes_a_datos_futuros():
    crudo = fuente_sintetica()
    m, diario, fuera = construir_rasgos(crudo)
    modificada = crudo.copy()
    fecha = m.index[80].end_time
    mascara = pd.to_datetime(modificada.date) > fecha
    modificada.loc[mascara, ["open", "high", "low", "close"]] *= 30
    modificada.loc[mascara, "volume"] *= 7
    futuro, _, _ = construir_rasgos(modificada)
    pd.testing.assert_frame_equal(m.iloc[:81], futuro.iloc[:81])
    # Truncar después del cierre de febrero también debe conservar la marca
    # de frontera, sin necesitar filas observadas del mes siguiente.
    t = m.index.get_loc(pd.Period("2019-02", "M"))
    prefijo = crudo[pd.to_datetime(crudo.date) <= m.index[t].end_time].copy()
    truncado, _, _ = construir_rasgos(prefijo)
    pd.testing.assert_frame_equal(m.iloc[:t+1], truncado)
    with threadpool_limits(limits=1):
        for h in [1, 3]:
            for c in CANDIDATOS:
                a, detalle, _ = predecir(m, 80, h, c)
                b, otro, _ = predecir(futuro, 80, h, c)
                assert a == b and detalle == otro
                assert detalle["ultimo_objetivo_ajuste"] == str(m.index[80])
                if "primer_origen_ajuste" in detalle:
                    assert detalle["n_ajuste"] == 80-h-11
                    assert detalle["ultimo_origen_ajuste"] == str(m.index[80-h])
    assert len(diario) == len(crudo) and len(fuera) == 16


def test_marcas_por_senal_conservan_observaciones_y_no_inventan_rangos():
    crudo = fuente_sintetica()
    crudo.loc[5, "high"] = crudo.loc[5, "low"]-1
    crudo.loc[7, "volume"] = 0
    copia = crudo.copy(deep=True)
    m, diario, fuera = construir_rasgos(crudo)
    pd.testing.assert_frame_equal(crudo, copia)
    assert not diario.loc[5, "uso_ohlc"] and pd.isna(diario.loc[5, "rango_rasgo"])
    assert diario.loc[5, "motivo_ohlc"] == "OHLC_incoherente"
    assert not diario.loc[7, "uso_volumen"] and diario.loc[7, "volume"] == 0
    assert diario.loc[7, "motivo_volumen"] != ""
    assert len(diario) == len(crudo) and m.n_dias.sum()+len(fuera) == len(crudo)
    assert m[COMPLETOS].iloc[12:].notna().all().all()


def test_eleccion_no_consulta_calibracion_ni_evaluacion():
    filas = []
    for h in [1, 3]:
        for fase in ["seleccion", "calibracion", "evaluacion"]:
            for i, c in enumerate(CANDIDATOS):
                filas.append({"horizonte": h, "fase": fase, "metodo": c["metodo"],
                              "observado": 20., "prediccion": 21.+i/10})
    p = pd.DataFrame(filas)
    a, _ = elegir(p)
    assert a == {"1": "ingenuo_cierre", "3": "ingenuo_cierre"}
    p.loc[~p.fase.eq("seleccion"), "prediccion"] = np.nan
    assert elegir(p)[0] == a
    p.loc[p.metodo.eq("svr_0.1") & p.fase.eq("seleccion"), "prediccion"] = 20.5
    assert elegir(p)[0] == {"1": "svr_0.1", "3": "svr_0.1"}
