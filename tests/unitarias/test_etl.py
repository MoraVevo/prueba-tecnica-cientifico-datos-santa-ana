"""Reglas de limpieza y trazabilidad con datos pequeños y resultados conocidos."""

import numpy as np
import pandas as pd
import pytest

from scripts.etl_serie1 import (
    convertir_mediciones,
    evaluar_relacion_dimensional,
    excluir_copias_duplicadas,
    marcar_duplicados,
    marcar_revision,
)


@pytest.fixture
def fila_fuente():
    return {
        "CLONE": "L01-299", "YEAR": "2020", "STAGE": "5", "LOC": "A",
        "CROP": "0", "REP": "1", "T_SPACRE": "10000", "TCA": "40",
        "TRS_TON": "250.000", "POPN": ".", "MSTWT": ".", "FIBER": ".",
    }


@pytest.mark.parametrize("texto,numero,prefijo", [
    ("79    227.620", 227.620, "79"),
    ("00    227.620", 227.620, "00"),
    ("250.000", 250.0, None),
    (".", None, None),
    ("", None, None),
])
def test_trs_separa_prefijo_y_preserva_original(fila_fuente, texto, numero, prefijo):
    fila_fuente["TRS_TON"] = texto
    fuente = pd.DataFrame([fila_fuente], dtype="string")
    datos, _ = convertir_mediciones(fuente)
    assert datos.loc[0, "TRS_TON_raw"] == texto
    assert not datos.loc[0, "ERROR_PARSE_TRS_TON"]
    if numero is None:
        assert pd.isna(datos.loc[0, "TRS_TON"])
    else:
        assert datos.loc[0, "TRS_TON"] == pytest.approx(numero)
    if prefijo is None:
        assert pd.isna(datos.loc[0, "TRS_TON_prefijo_sin_interpretar"])
    else:
        assert datos.loc[0, "TRS_TON_prefijo_sin_interpretar"] == prefijo


def test_deduplica_solo_copias_exactas_y_conserva_conflictos(fila_fuente):
    conflicto = {**fila_fuente, "T_SPACRE": "11000", "TCA": "44"}
    fuente = pd.DataFrame([fila_fuente, fila_fuente, conflicto], dtype="string")
    original = fuente.copy(deep=True)
    datos, errores = convertir_mediciones(fuente)
    assert marcar_duplicados(fuente, datos) == 1
    evaluar_relacion_dimensional(datos)
    analiticos, excluidos = excluir_copias_duplicadas(fuente, datos)
    marcar_revision(analiticos, errores)
    assert analiticos["FILA_CSV"].tolist() == [2, 4]
    assert excluidos["FILA_CSV"].tolist() == [3]
    assert excluidos["MOTIVO_EXCLUSION"].str.len().gt(0).all()
    assert analiticos["REQUIERE_REVISION"].all()
    assert set(analiticos.FILA_CSV).isdisjoint(excluidos.FILA_CSV)
    assert len(analiticos) + len(excluidos) == len(fuente)
    pd.testing.assert_frame_equal(fuente, original)


def test_ceros_se_conservan_y_alerta_dimensional_no_divide_entre_cero(fila_fuente):
    filas = [fila_fuente, {**fila_fuente, "T_SPACRE": "0", "TCA": "0"},
             {**fila_fuente, "T_SPACRE": "."}, {**fila_fuente, "T_SPACRE": "12000"}]
    datos, _ = convertir_mediciones(pd.DataFrame(filas, dtype="string"))
    evaluar_relacion_dimensional(datos)
    assert datos.loc[1, "T_SPACRE"] == 0
    assert pd.isna(datos.loc[2, "T_SPACRE"])
    assert datos.ESTADO_RELACION_DIMENSIONAL.tolist() == [
        "dentro_1_por_ciento", "sin_mediciones_completas",
        "sin_mediciones_completas", "fuera_1_por_ciento",
    ]
    assert np.isfinite(datos.RATIO_T_SPACRE_SOBRE_ESPERADO.dropna().to_numpy(dtype=float)).all()
