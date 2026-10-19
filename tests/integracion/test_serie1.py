"""Reconstruye resultados con el dataset local después de ejecutar los notebooks."""

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from sklearn.preprocessing import StandardScaler

from scripts.etl_serie1 import SHA256_ESPERADO
from scripts.modelado_serie1 import CATEGORICAS, ENTRADAS, agregar_historia, crear_modelos


RAIZ = Path(__file__).resolve().parents[2]
PROCESADOS = RAIZ / "data" / "processed"


def leer_resultado(nombre):
    ruta = PROCESADOS / nombre
    assert ruta.exists(), f"Falta {nombre}; ejecuta el ETL y los notebooks 01–05 indicados en README."
    return pd.read_csv(ruta, low_memory=False)


@pytest.fixture(scope="module")
def etl():
    return leer_resultado("serie1_etl_provisional.csv")


def test_etl_conserva_todas_las_filas_y_excluye_solo_copias_exactas(etl):
    ruta = RAIZ / "data" / "raw" / "louisiana_sugarcane_2010_2021.csv"
    assert hashlib.sha256(ruta.read_bytes()).hexdigest() == SHA256_ESPERADO
    fuente = pd.read_csv(ruta, dtype="string", keep_default_na=False)
    excluidas = leer_resultado("serie1_filas_excluidas.csv")
    copias = fuente.duplicated(keep="first")
    assert set(excluidas.FILA_CSV) == set(fuente.index[copias] + 2)
    assert set(etl.FILA_CSV) == set(fuente.index[~copias] + 2)
    assert set(etl.FILA_CSV).isdisjoint(excluidas.FILA_CSV)
    assert len(etl) + len(excluidas) == len(fuente)
    assert excluidas.MOTIVO_EXCLUSION.notna().all()
    assert not etl.FILA_CSV.duplicated().any()


@pytest.mark.parametrize("anio", [2019, 2020, 2021])
def test_predicciones_y_metricas_por_particion_temporal(etl, anio):
    if anio < 2021:
        predicciones = leer_resultado("serie1_predicciones_validacion.csv")
        resumen = leer_resultado("serie1_validacion_modelos.csv").query("ANIO_VALIDACION == @anio")
    else:
        predicciones = leer_resultado("serie1_predicciones_modelos_2021.csv")
        resumen = leer_resultado("serie1_evaluacion_2021.csv")
    predicciones = predicciones.loc[predicciones.ANIO_EVALUACION.eq(anio)]
    esperadas = etl.loc[etl.YEAR.eq(anio) & ~etl.REQUIERE_REVISION & etl.T_SPACRE.notna()].set_index("FILA_CSV")
    assert set(predicciones.MODELO) == set(crear_modelos()) | {"Referencia histórica", "Referencia clon-ambiente reciente"}
    assert not predicciones.duplicated(["MODELO", "FILA_CSV"]).any()
    assert predicciones.MAX_ANIO_ENTRENAMIENTO.eq(anio - 1).all()
    assert resumen.MAX_ANIO_ENTRENAMIENTO.eq(anio - 1).all()
    assert np.isfinite(predicciones[["OBSERVADO", "PREDICCION"]].to_numpy()).all()
    for nombre, filas in predicciones.groupby("MODELO"):
        assert set(filas.FILA_CSV) == set(esperadas.index)
        np.testing.assert_array_equal(filas.OBSERVADO, esperadas.loc[filas.FILA_CSV, "T_SPACRE"])
        observado = filas.OBSERVADO.to_numpy()
        error = filas.PREDICCION.to_numpy() - observado
        fila_resumen = resumen.set_index("MODELO").loc[nombre]
        # Se reconstruyen las métricas sin reutilizar las funciones de sklearn del notebook.
        assert fila_resumen.MAE == pytest.approx(np.mean(np.abs(error)), abs=1e-8)
        assert fila_resumen.RMSE == pytest.approx(np.sqrt(np.mean(error ** 2)), abs=1e-8)
        assert fila_resumen.R2 == pytest.approx(1 - np.sum(error ** 2) / np.sum((observado - observado.mean()) ** 2), abs=1e-10)
        if anio < 2021:
            assert fila_resumen.SESGO == pytest.approx(np.mean(error), abs=1e-8)
            assert fila_resumen.N == len(filas)


def test_eleccion_sin_test_y_reproduccion_del_modelo_supervisado(etl):
    validacion = leer_resultado("serie1_validacion_modelos.csv")
    candidatos = validacion.loc[validacion.MODELO.isin(crear_modelos())]
    elegido = candidatos.groupby("MODELO").MAE.mean().idxmin()
    guardadas = leer_resultado("serie1_predicciones_2021.csv")
    assert guardadas.MODELO_ELEGIDO.eq(elegido).all()
    base = etl.loc[~etl.REQUIERE_REVISION & etl.T_SPACRE.notna()]
    modelado = agregar_historia(base)
    entrenamiento = modelado.loc[modelado.YEAR.lt(2021)].copy()
    prueba = modelado.loc[modelado.YEAR.eq(2021)].copy()
    # Las tres historias de 2021 se reconstruyen con cruces sobre el pasado.
    for claves, nombre in [(["CLONE"], "HIST_CLONE"), (["LOC"], "HIST_LOC"), (["CLONE", "CROP"], "HIST_CLONE_CROP")]:
        media = entrenamiento.groupby(claves).T_SPACRE.mean().rename("ESPERADA")
        referencia = prueba[claves].join(media, on=claves).ESPERADA
        np.testing.assert_allclose(prueba[nombre], referencia, equal_nan=True)
    entrenamiento[CATEGORICAS] = entrenamiento[CATEGORICAS].astype(str)
    prueba[CATEGORICAS] = prueba[CATEGORICAS].astype(str)
    modelo = crear_modelos()[elegido].fit(entrenamiento[ENTRADAS], entrenamiento.T_SPACRE)
    prediccion = pd.Series(modelo.predict(prueba[ENTRADAS]), index=prueba.FILA_CSV)
    np.testing.assert_allclose(guardadas.PREDICCION, prediccion.loc[guardadas.FILA_CSV], rtol=1e-10, atol=1e-7)
    numerico = modelo.named_steps["preparar"].named_transformers_["numeros"]
    assert numerico.named_steps["escalar"].n_samples_seen_ == len(entrenamiento)
    assert entrenamiento.YEAR.max() < prueba.YEAR.min()


def test_politicas_economicas_reproducen_formula_y_cobertura(etl):
    base = etl.loc[etl.STAGE.eq(5) & ~etl.REQUIERE_REVISION].dropna(subset=["T_SPACRE", "TCA"])
    medidas = ["T_SPACRE", "TCA"]
    celdas = base.groupby(["CLONE", "CROP", "YEAR", "LOC"], as_index=False)[medidas].mean()
    control = celdas.loc[celdas.CLONE.eq("L01-299")]
    comunes = celdas.merge(control.drop(columns="CLONE"), on=["CROP", "YEAR", "LOC"], suffixes=("", "_CONTROL"), validate="many_to_one")
    ajustadas = pd.DataFrame(index=comunes.groupby(["CLONE", "CROP"]).size().index)
    for medida in medidas:
        diferencia = comunes[medida] - comunes[medida + "_CONTROL"]
        ajustadas[medida] = diferencia.groupby([comunes.CLONE, comunes.CROP]).mean()
        ajustadas[medida] += ajustadas.index.get_level_values("CROP").map(control.groupby("CROP")[medida].mean())
    cobertura = comunes.groupby(["CLONE", "CROP"]).agg(anios=("YEAR", "nunique"), localidades=("LOC", "nunique"))
    politicas = leer_resultado("serie1_politicas_renovacion.csv")
    assert np.isfinite(politicas.select_dtypes("number").to_numpy()).all()
    for fila in politicas.itertuples():
        cortes = range(fila.ULTIMO_CROP + 1)
        tramo = ajustadas.loc[[(fila.CLONE, c) for c in cortes]]
        respaldo = cobertura.loc[tramo.index]
        assert fila.COSECHAS_TOTALES == len(tramo)
        assert respaldo.ge(2).all().all()
        ingresos_menos_costos = fila.PRECIO_USD_LB * tramo.T_SPACRE - 14 * tramo.TCA - 350
        esperado = (ingresos_menos_costos.sum() - 1100) / len(tramo)
        assert fila.APORTE_ANUAL_USD_ACRE == pytest.approx(esperado, abs=1e-8)
    mejores = politicas.loc[politicas.PRECIO_USD_LB.eq(0.20)].sort_values("APORTE_ANUAL_USD_ACRE", ascending=False).drop_duplicates("CLONE").head(3)
    assert list(zip(mejores.CLONE, mejores.COSECHAS_TOTALES)) == [("HOCP14-885", 3), ("L01-299", 4), ("HO12-615", 4)]


def test_errores_por_ambiente_conservan_filas_y_metricas_globales():
    predicciones = leer_resultado("serie1_predicciones_2021.csv")
    ambientes = leer_resultado("serie1_errores_ambiente_2021.csv")
    assert ambientes.n.sum() == len(predicciones)
    assert np.isfinite(ambientes[["n", "mae", "sesgo"]].to_numpy()).all()
    assert np.average(ambientes.mae, weights=ambientes.n) == pytest.approx(predicciones.ERROR_ABSOLUTO.mean())
    for fila in ambientes.itertuples():
        parte = predicciones.loc[predicciones.LOC.eq(fila.LOC) & predicciones.STAGE.eq(fila.STAGE)]
        error = parte.PREDICCION - parte.T_SPACRE
        assert fila.n == len(parte)
        assert fila.mae == pytest.approx(error.abs().mean())
        assert fila.sesgo == pytest.approx(error.mean())


def test_segmentacion_reproduce_dimensiones_y_conservacion_comparable(etl):
    perfil = leer_resultado("serie1_segmentos_variedades.csv").set_index("CLONE")
    base = etl.loc[etl.STAGE.eq(5) & ~etl.REQUIERE_REVISION].dropna(subset=["T_SPACRE", "TRS_TON"])
    celdas = base.groupby(["CLONE", "CROP", "YEAR", "LOC"], as_index=False)[["T_SPACRE", "TRS_TON"]].mean()
    cobertura = celdas.groupby(["CLONE", "CROP"]).agg(anios=("YEAR", "nunique"), localidades=("LOC", "nunique"))
    elegibles = [clon for clon, grupo in cobertura.groupby(level=0)
                 if all((clon, c) in grupo.index and grupo.loc[(clon, c)].ge(2).all() for c in [0, 1, 2])]
    assert set(perfil.index) == set(elegibles)
    celdas = celdas.loc[celdas.CLONE.isin(elegibles) & celdas.CROP.le(2)]
    reconstruido = pd.DataFrame(index=perfil.index)
    for medida, nombre in [("T_SPACRE", "PRODUCTIVIDAD_LB_ACRE"), ("TRS_TON", "CALIDAD_LB_TON")]:
        reconstruido[nombre] = celdas.groupby(["CLONE", "CROP"])[medida].mean().groupby("CLONE").sum() / 3
    claves = ["CLONE", "YEAR", "LOC"]
    comunes = celdas.loc[celdas.CROP.eq(0), claves + ["T_SPACRE"]].merge(
        celdas.loc[celdas.CROP.eq(2), claves + ["T_SPACRE"]], on=claves,
        suffixes=("_PLANTIA", "_SOCA"), validate="one_to_one",
    )
    sumas = comunes.groupby("CLONE")[["T_SPACRE_PLANTIA", "T_SPACRE_SOCA"]].sum()
    reconstruido["CONSERVACION_SEGUNDA_SOCA"] = sumas.T_SPACRE_SOCA / sumas.T_SPACRE_PLANTIA
    soporte = comunes.groupby("CLONE").agg(AMBIENTES_COMPARABLES=("LOC", "size"), ANIOS_COMPARABLES=("YEAR", "nunique"), LOCALIDADES_COMPARABLES=("LOC", "nunique"))
    np.testing.assert_array_equal(perfil[soporte.columns], soporte.loc[perfil.index])
    assert soporte[["ANIOS_COMPARABLES", "LOCALIDADES_COMPARABLES"]].ge(2).all().all()
    referencia = celdas.groupby(["CROP", "YEAR", "LOC"]).T_SPACRE.median().rename("MEDIANA")
    relativas = celdas.join(referencia, on=["CROP", "YEAR", "LOC"])
    relativas["INDICE"] = relativas.T_SPACRE / relativas.MEDIANA
    relativas["RESIDUO"] = relativas.INDICE - relativas.groupby(["CLONE", "CROP"]).INDICE.transform("mean")
    relativas["CUADRADO"] = relativas.RESIDUO ** 2
    varianza = relativas.groupby("CLONE").agg(suma=("CUADRADO", "sum"), n=("CUADRADO", "size"))
    reconstruido["INESTABILIDAD_RELATIVA"] = np.sqrt(varianza.suma / (varianza.n - 1))
    variables = reconstruido.columns.tolist()
    assert np.isfinite(perfil[variables].to_numpy()).all()
    np.testing.assert_allclose(perfil[variables], reconstruido[variables], rtol=1e-12, atol=1e-12)
    etiquetas = KMeans(n_clusters=2, n_init=30, random_state=42).fit_predict(StandardScaler().fit_transform(reconstruido))
    assert adjusted_rand_score(etiquetas, perfil.GRUPO) == 1
    assert len(perfil) == 17 and perfil.SEGMENTO.nunique() == 2
