"""Comprueba disponibilidad temporal y aislamiento del preprocesamiento."""

import numpy as np
import pandas as pd
import pytest

from scripts.modelado_serie1 import (
    CATEGORICAS, ENTRADAS, NUMERICAS, agregar_historia, crear_modelos, referencia_reciente,
)


def test_historia_excluye_objetivos_del_mismo_anio_y_del_futuro():
    datos = pd.DataFrame({
        "CLONE": ["A"] * 5, "LOC": ["X"] * 5, "CROP": [0] * 5,
        "YEAR": [2020, 2018, 2019, 2019, 2021], "T_SPACRE": [900, 100, 200, 400, 9999],
    }, index=[8, 2, 7, 4, 11])
    original = datos.copy(deep=True)
    historia = agregar_historia(datos)
    assert historia.index.equals(datos.index)
    assert pd.isna(historia.loc[2, "HIST_CLONE"])
    assert historia.loc[[7, 4], "HIST_CLONE"].eq(100).all()
    assert historia.loc[8, "HIST_CLONE"] == pytest.approx(700 / 3)
    cambiados = datos.copy()
    cambiados.loc[cambiados.YEAR.ge(2020), "T_SPACRE"] = -999999
    columnas = ["HIST_CLONE", "HIST_LOC", "HIST_CLONE_CROP"]
    pd.testing.assert_frame_equal(historia.loc[datos.YEAR.le(2020), columnas], agregar_historia(cambiados).loc[datos.YEAR.le(2020), columnas])
    pd.testing.assert_frame_equal(datos, original)


def test_historia_respeta_clon_localidad_y_corte():
    datos = pd.DataFrame({
        "CLONE": ["A", "A", "B", "A", "NUEVO"], "LOC": ["X", "Y", "X", "X", "NUEVA"],
        "CROP": [0, 1, 0, 1, 0], "YEAR": [2018, 2018, 2018, 2019, 2019],
        "T_SPACRE": [100, 300, 900, 9999, 9999],
    })
    resultado = agregar_historia(datos)
    assert resultado.loc[3, "HIST_CLONE"] == 200
    assert resultado.loc[3, "HIST_LOC"] == 500
    assert resultado.loc[3, "HIST_CLONE_CROP"] == 300
    assert resultado.loc[4, ["HIST_CLONE", "HIST_LOC", "HIST_CLONE_CROP"]].isna().all()


def test_referencia_reciente_prioriza_historia_sin_usar_objetivo_evaluado():
    entrenamiento = pd.DataFrame({
        "CLONE": ["A", "A", "B", "C"], "LOC": ["X", "X", "Y", "Y"],
        "STAGE": ["5"] * 4, "CROP": [0, 0, 0, 1],
        "YEAR": [2018, 2019, 2018, 2019], "T_SPACRE": [100, 300, 500, 700],
    })
    evaluacion = pd.DataFrame({
        "CLONE": ["A", "B", "NUEVO", "NUEVO"], "LOC": ["X", "Y", "Z", "Z"],
        "STAGE": ["5", "5", "5", "4"], "CROP": [0, 0, 0, 2],
        "YEAR": [2020] * 4, "T_SPACRE": [-1e9] * 4,
    }, index=[8, 6, 4, 2])
    prediccion = referencia_reciente(entrenamiento, evaluacion)
    np.testing.assert_allclose(prediccion, [300, 500, 300, 400])
    assert prediccion.index.equals(evaluacion.index)


@pytest.mark.parametrize("nombre", ["Ridge interpretable", "Árbol de decisión", "Bosque aleatorio"])
def test_pipeline_ajusta_transformaciones_solo_con_entrenamiento(nombre):
    prohibidas = {"T_SPACRE", "TCA", "TRS_TON", "POPN", "MSTWT", "FIBER", "REP"}
    assert not set(ENTRADAS) & prohibidas
    entrenamiento = pd.DataFrame({
        "CLONE": ["A"] * 6, "LOC": ["X"] * 6, "STAGE": ["5"] * 6,
        "YEAR": [2017, 2017, 2018, 2018, 2019, 2019], "CROP": [0, 1, 0, 1, 0, 1],
        "HIST_CLONE": [np.nan, np.nan, 100, 100, 200, 200],
        "HIST_LOC": [np.nan, np.nan, 100, 100, 200, 200],
        "HIST_CLONE_CROP": [np.nan, np.nan, 100, 100, 200, 200],
    })
    objetivo = pd.Series([100, 150, 200, 250, 300, 350])
    modelo = crear_modelos()[nombre].fit(entrenamiento[ENTRADAS], objetivo)
    numeros = modelo.named_steps["preparar"].named_transformers_["numeros"]
    # Medianas manuales: año, corte y las tres historias.
    np.testing.assert_allclose(numeros.named_steps["imputar"].statistics_, [2018, 0.5, 150, 150, 150])
    centros = numeros.named_steps["escalar"].mean_.copy()
    evaluacion = entrenamiento.iloc[[0]].copy()
    evaluacion[NUMERICAS] = 1e6
    evaluacion[CATEGORICAS] = "SIN_HISTORIA"
    assert np.isfinite(modelo.predict(evaluacion[ENTRADAS])).all()
    np.testing.assert_array_equal(numeros.named_steps["escalar"].mean_, centros)
    assert "SIN_HISTORIA" not in modelo.named_steps["preparar"].named_transformers_["categorias"].categories_[0]
