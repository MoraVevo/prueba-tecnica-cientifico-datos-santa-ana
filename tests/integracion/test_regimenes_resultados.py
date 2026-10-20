"""Reconstruye la vista temporal y las asignaciones sin usar el módulo de regímenes."""

import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from threadpoolctl import threadpool_limits


RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "outputs/regimenes"


def test_regimenes_conservan_fuente_y_reproducen_ajuste_solo_en_cuatro_dias():
    assert (SALIDA / "verificacion.json").exists(), "Ejecutar notebook 09 antes de esta integración."
    datos = pd.read_csv(RAIZ / "data/raw/serie2/data.csv", parse_dates=["date"])
    # Resample anclado: ruta independiente del groupby por cocientes usado en producción.
    vista = datos.set_index("date").resample("1min", origin=datos.date.iloc[0]).median()
    vista["presion_hogar_sintesis"] = vista[[f"PT_8313{letra}.AV_0#" for letra in "ABCDEF"]].median(axis=1)
    artefacto = joblib.load(SALIDA / "modelo_regimenes.joblib")
    x = vista[artefacto["columnas"]]
    guardadas = pd.read_csv(SALIDA / "entradas_minuto.csv", index_col="intervalo")
    np.testing.assert_allclose(x, guardadas, rtol=0, atol=1e-10)
    assert "ZZQBCHLL.AV_0#" not in x and "TE_8332A.AV_0#" not in x
    train = x.iloc[:5760]
    np.testing.assert_allclose(artefacto["escalador"].mean_, train.mean(), rtol=0, atol=1e-10)
    np.testing.assert_allclose(artefacto["escalador"].scale_, train.std(ddof=0), rtol=0, atol=1e-10)
    assert artefacto["escalador"].n_samples_seen_ == 5760
    z = (x.to_numpy()-train.mean().to_numpy())/train.std(ddof=0).to_numpy()*artefacto["pesos"]
    with threadpool_limits(limits=2):
        referencia = KMeans(n_clusters=2, n_init=20, random_state=42).fit(z[:5760])
    np.testing.assert_allclose(referencia.cluster_centers_, artefacto["modelo"].cluster_centers_, rtol=0, atol=1e-10)
    # Asignación geométrica manual: no usa predict del modelo guardado.
    distancia = ((z[:, None, :] - referencia.cluster_centers_[None, :, :])**2).sum(axis=2)
    etiquetas = np.array([artefacto["renumeracion"][int(i)] for i in distancia.argmin(axis=1)])
    asignaciones = pd.read_csv(SALIDA / "asignaciones_minuto.csv")
    np.testing.assert_array_equal(etiquetas, asignaciones.regimen)
    filas = pd.read_csv(SALIDA / "asignaciones_filas.csv", parse_dates=["date", "etiqueta_disponible_desde"])
    assert len(filas) == 86400 and filas.fila_fuente.is_unique
    np.testing.assert_array_equal(filas.fila_fuente, np.arange(len(datos)))
    np.testing.assert_array_equal(filas.regimen, np.repeat(etiquetas, 12))
    pd.testing.assert_series_equal(filas.date, datos.date)
    assert filas.date.lt(filas.etiqueta_disponible_desde).all()
    resumen = pd.read_csv(SALIDA / "resumen_regimenes.csv").set_index("regimen")
    assert resumen.minutos.sum() == 7200
    for regimen in [1, 2]:
        assert resumen.loc[regimen, "minutos"] == int((etiquetas == regimen).sum())
    episodios = pd.read_csv(SALIDA / "episodios.csv", parse_dates=["inicio", "fin"])
    assert episodios.minutos.sum() == 7200
    np.testing.assert_allclose(episodios.minutos, (episodios.fin-episodios.inicio).dt.total_seconds()/60)
    perfil = pd.read_csv(SALIDA / "perfiles_sensores_crudos.csv")
    crudo = datos.assign(regimen=filas.regimen.to_numpy())
    for _, fila in perfil.iterrows():
        s = crudo.loc[crudo.regimen.eq(fila.regimen), fila.sensor]
        np.testing.assert_allclose(fila.mediana, s.median(), rtol=0, atol=1e-10)
        assert fila.faltantes == s.isna().sum()
    verificacion = json.loads((SALIDA / "verificacion.json").read_text(encoding="utf-8"))
    assert all(hashlib.sha256((RAIZ/p).read_bytes()).hexdigest()==h for p,h in verificacion["huellas_protegidas"].items())
