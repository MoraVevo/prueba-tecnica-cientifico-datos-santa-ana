"""Contrasta resultados guardados del sensor virtual con sus predicciones originales."""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest

from scripts.modelado_serie2 import OBJETIVO

SALIDA = Path(__file__).resolve().parents[2] / "outputs"


def test_comprobacion_reproduce_metricas_y_respeta_particiones():
    archivos = ["serie2_predicciones_test.csv", "serie2_metricas_test.csv", "serie2_particiones.csv", "serie2_entradas_campeon.csv"]
    assert all((SALIDA / nombre).exists() for nombre in archivos), "Ejecutar notebook 07 antes de las pruebas de integración."
    predicciones = pd.read_csv(SALIDA / archivos[0], parse_dates=["date"])
    metricas = pd.read_csv(SALIDA / archivos[1]).iloc[0]
    particiones = pd.read_csv(SALIDA / archivos[2])
    entradas = pd.read_csv(SALIDA / archivos[3]).entrada
    assert len(predicciones) == 8640 and predicciones.date.is_unique
    assert not entradas.str.contains("ZZQBCHLL", regex=False).any()
    assert not entradas.str.contains("__", regex=False).any()
    assert len(entradas) in [15, 29]
    assert predicciones.date.diff().dropna().eq(pd.Timedelta(seconds=10)).all()
    for _, fila in particiones.iterrows():
        assert pd.Timestamp(fila.fin_entrenamiento) < pd.Timestamp(fila.inicio_evaluacion) - pd.Timedelta(minutes=5)
    error = predicciones.estimado - predicciones.observado
    assert np.isfinite(predicciones[["observado", "estimado", "referencia", "error"]]).all().all()
    assert metricas.MAE == pytest.approx(error.abs().mean())
    assert metricas.RMSE == pytest.approx(np.sqrt((error ** 2).mean()))
    assert metricas.R2 == pytest.approx(1 - (error ** 2).sum() / ((predicciones.observado - predicciones.observado.mean()) ** 2).sum())
    assert metricas.sesgo == pytest.approx(error.mean())
    assert metricas.WAPE_pct == pytest.approx(100 * error.abs().sum() / predicciones.observado.abs().sum())
    # Verificar alineación con fuente y reproducción del artefacto, sin volver a entrenar.
    fuente = pd.read_csv(SALIDA.parent / "data/raw/serie2/data.csv", parse_dates=["date"])
    observado_original = fuente.set_index("date").loc[predicciones.date, OBJETIVO]
    np.testing.assert_allclose(predicciones.observado, observado_original, rtol=0, atol=1e-12)
    artefacto = joblib.load(SALIDA / "serie2_sensor_virtual.joblib")
    entradas_originales = fuente.drop(columns=["date", OBJETIVO]).set_axis(fuente.date)
    reproducidas = artefacto["modelo"].predict(entradas_originales.loc[predicciones.date, artefacto["columnas"]])
    np.testing.assert_allclose(predicciones.estimado, reproducidas, rtol=0, atol=1e-10)


def test_decision_corresponde_a_validacion_y_declara_reutilizacion():
    decision = json.loads((SALIDA / "serie2_decision_antes_test.json").read_text(encoding="utf-8"))
    validacion = pd.read_csv(SALIDA / "serie2_validacion.csv")
    assert decision["evaluacion_final_independiente"] is False
    assert len(validacion) == 21
    assert set(validacion.particion) == {"Validación 1", "Validación 2", "Validación 3"}
    candidato = validacion.loc[validacion.modelo.eq(decision["modelo"]) & validacion.variante.eq(decision["variante"])]
    assert len(candidato) == 3
    assert decision["MAE_validacion"] == pytest.approx(candidato.MAE.mean())
    reducidas = validacion.loc[validacion.variante.eq("Reducida 15")]
    assert len(reducidas) == 9 and reducidas.n_entradas.eq(15).all()
    numericas = validacion.select_dtypes(include="number")
    assert np.isfinite(numericas.to_numpy()).all()
