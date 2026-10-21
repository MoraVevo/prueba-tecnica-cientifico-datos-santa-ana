"""Casos pequeños con resultados conocidos para el ranking de Serie I."""

import numpy as np
import pandas as pd

from scripts.evaluar_ranking_serie1 import _politicas_desde_resumen, _resumen_replica


def test_aporte_anual_y_duracion_optima_conocidos():
    resumen = pd.DataFrame([
        {"CLONE": "A", "CROP": 0, "T_SPACRE": 10000.0, "TCA": 20.0, "anios": 2, "localidades": 2},
        {"CLONE": "A", "CROP": 1, "T_SPACRE": 9000.0, "TCA": 19.0, "anios": 2, "localidades": 2},
        {"CLONE": "A", "CROP": 2, "T_SPACRE": 8000.0, "TCA": 18.0, "anios": 2, "localidades": 2},
        {"CLONE": "B", "CROP": 0, "T_SPACRE": 5000.0, "TCA": 20.0, "anios": 2, "localidades": 2},
        {"CLONE": "B", "CROP": 1, "T_SPACRE": 4000.0, "TCA": 19.0, "anios": 1, "localidades": 2},
    ])
    mejor, estado = _politicas_desde_resumen(resumen, 0.20, ["A", "B", "C"])
    assert mejor.loc[mejor.CLONE.eq("A"), "ULTIMO_CROP"].item() == 2
    esperado = (0.20 * (10000 + 9000 + 8000) - 14 * (20 + 19 + 18) - 350 * 3 - 1100) / 3
    assert mejor.loc[mejor.CLONE.eq("A"), "APORTE_ANUAL_USD_ACRE"].item() == esperado
    assert not estado.loc[estado.CLONE.eq("B"), "ELEGIBLE"].item()
    assert estado.loc[estado.CLONE.eq("C"), "MOTIVO"].item().startswith("Ausente")


def test_repeticion_del_mismo_ano_pesa_dos_veces_pero_es_un_solo_ano_evidencial():
    celdas = pd.DataFrame([
        {"CLONE": "A", "CROP": 0, "YEAR": 2010, "LOC": "L1", "T_SPACRE": 100.0, "TCA": 10.0},
        {"CLONE": "A", "CROP": 0, "YEAR": 2011, "LOC": "L2", "T_SPACRE": 200.0, "TCA": 20.0},
        {"CLONE": "A", "CROP": 1, "YEAR": 2010, "LOC": "L1", "T_SPACRE": 50.0, "TCA": 5.0},
        {"CLONE": "A", "CROP": 1, "YEAR": 2011, "LOC": "L2", "T_SPACRE": 60.0, "TCA": 6.0},
    ])
    series, refs = ({("A", crop): {
        "a": np.array([a0, a1], dtype=float), "c": np.array([c0, c1], dtype=float),
        "n": np.array([1.0, 1.0]), "locs": {0: {"L1"}, 1: {"L2"}},
    } for crop, a0, a1, c0, c1 in [(0, 100, 200, 10, 20), (1, 50, 60, 5, 6)]}, {})
    # Dos copias del año 2010 dan la media 100, aunque solo haya un año distinto.
    resumen = _resumen_replica(series, refs, np.array([2.0, 0.0]), False, ["A"])
    fila = resumen.loc[resumen.CROP.eq(0)].iloc[0]
    assert fila.T_SPACRE == 100.0
    assert fila.anios == 1
    assert fila.localidades == 1

