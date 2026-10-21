"""Contrasta el JSON de la API con el pipeline original de Serie II."""

import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest

from api.modelo import ModeloSensorVirtual
from experimentos.rezagos_serie2 import PRESIONES
from scripts.exportar_modelo_serie2 import construir_especificacion
from scripts.modelado_serie2 import OBJETIVO


RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "outputs/campeona_serie2"
RUTA_JSON = RAIZ / "models/serie2_sensor_virtual.json"


def _reconstruir_ajuste():
    crudo = pd.read_csv(RAIZ / "data/raw/serie2/data.csv", parse_dates=["date"])
    datos = crudo.iloc[::2].set_index("date")
    inicio = crudo.date.iloc[0]
    mascara = (
        (datos.index >= inicio + pd.Timedelta(seconds=660))
        & (datos.index < inicio + pd.Timedelta(days=4) - pd.Timedelta(minutes=5))
    )
    guardado = joblib.load(SALIDA / "sensor_virtual.joblib")
    decision = json.loads((SALIDA / "decision.json").read_text(encoding="utf-8"))
    actuales = [c for c in guardado["columnas"] if not c.endswith("__pasado_30s")]
    x = datos.loc[mascara, actuales].copy()
    for columna in PRESIONES:
        x[f"{columna}__pasado_30s"] = datos[columna].reindex(
            x.index - pd.Timedelta(seconds=30)
        ).to_numpy()
    x = x[guardado["columnas"]]
    y = datos.loc[mascara, OBJETIVO]
    return crudo, x, y, guardado, decision


@pytest.fixture(scope="module")
def reconstruccion():
    return _reconstruir_ajuste()


@pytest.fixture(scope="module")
def especificacion():
    return json.loads(RUTA_JSON.read_text(encoding="utf-8"))


def test_json_conserva_parametros_procedencia_y_limites(reconstruccion, especificacion):
    crudo, x, y, guardado, decision = reconstruccion
    pipeline = guardado["modelo"]
    assert especificacion["objetivo"] == OBJETIVO
    assert [entrada["nombre"] for entrada in especificacion["entradas"]] == guardado["columnas"]
    assert len(especificacion["entradas"]) == 17
    assert len(x) == decision["n_ajuste"] == 34464
    assert len(y) == len(x)
    assert int(x.isna().sum().sum()) == 15
    assert int(x["YJJWSLL.AV_0#"].isna().sum()) == 15

    entrenamiento = especificacion["entrenamiento"]
    assert entrenamiento["n_ajuste"] == decision["n_ajuste"]
    assert entrenamiento["n_faltantes_imputados"] == int(x.isna().sum().sum())
    assert entrenamiento["inicio"] == decision["inicio_ajuste"]
    assert entrenamiento["fin"] == decision["fin_ajuste"]
    assert entrenamiento["validacion_independiente"] is False
    assert entrenamiento["dia5_evaluado"] is False
    assert entrenamiento["mae_validacion"] == pytest.approx(decision["MAE_validacion"])
    assert entrenamiento["wape_validacion_pct"] == pytest.approx(decision["WAPE_validacion_pct"])
    assert entrenamiento["peor_mae_validacion"] == pytest.approx(decision["peor_MAE_validacion"])
    assert especificacion["alpha"] == pytest.approx(pipeline.named_steps["ridge"].alpha)
    assert especificacion["intercepto"] == pytest.approx(pipeline.named_steps["ridge"].intercept_)
    assert especificacion["huella_joblib_sha256"] == hashlib.sha256(
        (SALIDA / "sensor_virtual.joblib").read_bytes()
    ).hexdigest()

    imputador = pipeline.named_steps["simpleimputer"]
    escalador = pipeline.named_steps["standardscaler"]
    ridge = pipeline.named_steps["ridge"]
    for i, entrada in enumerate(especificacion["entradas"]):
        columna = entrada["nombre"]
        assert entrada["mediana_imputacion"] == pytest.approx(imputador.statistics_[i])
        assert entrada["media_escalado"] == pytest.approx(escalador.mean_[i])
        assert entrada["escala"] == pytest.approx(escalador.scale_[i])
        assert entrada["coeficiente_estandarizado"] == pytest.approx(ridge.coef_[i])
        assert entrada["minimo_entrenamiento"] == pytest.approx(x[columna].min())
        assert entrada["maximo_entrenamiento"] == pytest.approx(x[columna].max())
        assert entrada["p01_entrenamiento"] == pytest.approx(x[columna].quantile(0.01))
        assert entrada["p99_entrenamiento"] == pytest.approx(x[columna].quantile(0.99))
        assert entrada["n_faltantes_entrenamiento"] == int(x[columna].isna().sum())
        assert entrada["minimo_entrenamiento"] <= entrada["p01_entrenamiento"]
        assert entrada["p01_entrenamiento"] <= entrada["p99_entrenamiento"]
        assert entrada["p99_entrenamiento"] <= entrada["maximo_entrenamiento"]

    texto = RUTA_JSON.read_text(encoding="utf-8").lower()
    assert "usuario" not in texto
    assert "solicitada" not in texto


def test_predicciones_del_json_coinciden_con_el_pipeline(reconstruccion):
    _, x, _, guardado, _ = reconstruccion
    modelo = ModeloSensorVirtual.cargar(RUTA_JSON)
    pipeline = guardado["modelo"]
    completas = x.dropna()
    assert len(completas) == 34449
    indices = np.linspace(0, len(completas) - 1, 500, dtype=int)
    muestra = completas.iloc[indices]
    observado = pipeline.predict(muestra)
    reconstruido = np.array(
        [modelo.predecir(fila.to_dict()) for _, fila in muestra.iterrows()], dtype=float
    )
    np.testing.assert_allclose(reconstruido, observado, rtol=0, atol=1e-9)

    medianas = {entrada.nombre: entrada.mediana_imputacion for entrada in modelo.entradas}
    fila_mediana = pd.DataFrame([medianas], columns=x.columns)
    assert modelo.predecir(medianas) == pytest.approx(float(pipeline.predict(fila_mediana)[0]))


def test_los_faltantes_imputados_tambien_reproducen_el_pipeline(reconstruccion):
    _, x, _, guardado, _ = reconstruccion
    modelo = ModeloSensorVirtual.cargar(RUTA_JSON)
    faltantes = x[x.isna().any(axis=1)]
    assert len(faltantes) == 15
    medianas = {entrada.nombre: entrada.mediana_imputacion for entrada in modelo.entradas}
    for _, fila in faltantes.iterrows():
        valores = {
            nombre: (medianas[nombre] if pd.isna(valor) else float(valor))
            for nombre, valor in fila.items()
        }
        assert modelo.predecir(valores) == pytest.approx(
            float(guardado["modelo"].predict(fila.to_frame().T)[0])
        )


def test_el_exportador_reproduce_el_archivo_versionado():
    assert construir_especificacion(RAIZ) == json.loads(RUTA_JSON.read_text(encoding="utf-8"))
