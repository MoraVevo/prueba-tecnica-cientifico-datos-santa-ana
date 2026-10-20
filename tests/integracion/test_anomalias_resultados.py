"""Reconstrucción independiente de contexto, ajuste, reglas y conservación."""

import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "outputs/anomalias"


def test_anomalias_reproducen_pasado_reglas_y_todas_las_filas():
    assert (SALIDA / "verificacion.json").exists(), "Ejecutar notebook 10 antes de esta integración."
    v = json.loads((SALIDA / "verificacion.json").read_text(encoding="utf-8"))
    datos = pd.read_csv(RAIZ / "data/raw/serie2/data.csv", parse_dates=["date"])
    f = pd.read_csv(SALIDA / "evaluacion_filas.csv", parse_dates=["date", "contexto_disponible_desde"],
                    dtype={"tags_faltantes": "string"})
    assert len(f) == len(datos) == 86400
    np.testing.assert_array_equal(f.fila_fuente, np.arange(len(datos)))
    pd.testing.assert_series_equal(f.date, datos.date)
    x = datos.drop(columns="date")
    assert f.faltantes.sum() == x.isna().sum().sum() == 30
    np.testing.assert_array_equal(f.aviso_calidad, x.isna().any(axis=1))
    # Búsqueda binaria, independiente de merge_asof: nunca usa un minuto no cerrado.
    r = pd.read_csv(RAIZ / "outputs/regimenes/asignaciones_minuto.csv", parse_dates=["disponible_desde"])
    pos = np.searchsorted(r.disponible_desde.to_numpy(), datos.date.to_numpy(), side="right") - 1
    perfil = np.zeros(len(f), dtype=int)
    perfil[pos >= 0] = r.regimen.to_numpy()[pos[pos >= 0]]
    np.testing.assert_array_equal(perfil, f.regimen_cerrado)
    assert (f.contexto_disponible_desde.dropna() <= f.date[f.contexto_disponible_desde.notna()]).all()
    corte = datos.date.iloc[0] + pd.Timedelta(days=4)
    train = datos.date.lt(corte).to_numpy()
    assert train.sum() == 69120 == v["filas_ajuste"]
    medianas = x.loc[train].median()
    artefacto = joblib.load(SALIDA / "detector_anomalias.joblib")
    assert artefacto["columnas"] == list(x.columns)
    np.testing.assert_allclose(artefacto["detector"][0].statistics_, medianas)
    # Reajuste directo sobre matriz imputada manualmente, sin helpers del notebook.
    matriz = x.fillna(medianas).to_numpy()
    ref = IsolationForest(n_estimators=200, max_samples=1024, contamination="auto", random_state=42, n_jobs=2)
    ref.fit(matriz[train])
    score = -ref.score_samples(matriz)
    np.testing.assert_allclose(score, f.score, rtol=0, atol=1e-14)
    umbral = np.full(len(f), np.quantile(score[train], .99))
    for g in [1, 2]:
        umbral[perfil == g] = np.quantile(score[train & (perfil == g)], .99)
    np.testing.assert_allclose(umbral, f.umbral, rtol=0, atol=1e-14)
    candidatas = score > umbral
    np.testing.assert_array_equal(candidatas, f.candidata)
    temp = datos["TE_8332A.AV_0#"].to_numpy()
    fuera = (temp < 530) | (temp > 545)
    np.testing.assert_array_equal(fuera, f.fuera_banda_temperatura)
    # Máquina de estados independiente, incluida espera de recuperación.
    for senal, requeridas, ventana, columna in [(candidatas, 3, 6, "aviso_multivariable"),
                                                (fuera, 12, 12, "aviso_temperatura")]:
        esperada = np.zeros(len(f), dtype=bool)
        encendido = False
        for i in range(len(f)):
            if encendido:
                if i >= 11 and not senal[i-11:i+1].any():
                    encendido = False
            elif i >= ventana-1 and senal[i] and senal[i-ventana+1:i+1].sum() >= requeridas:
                encendido = True
            esperada[i] = encendido
        np.testing.assert_array_equal(esperada, f[columna])
    e = pd.read_csv(SALIDA / "episodios.csv", parse_dates=["inicio", "fin", "fin_lectura"])
    for tipo, columna in [("candidata", "candidata"), ("multivariable", "aviso_multivariable"),
                          ("temperatura", "aviso_temperatura"), ("calidad", "aviso_calidad")]:
        b = f[columna].to_numpy()
        inicios = np.flatnonzero(b & ~np.r_[False, b[:-1]])
        finales = np.flatnonzero(b & ~np.r_[b[1:], False])
        guardado = e[e.tipo.eq(tipo)]
        np.testing.assert_array_equal(guardado.inicio.to_numpy(), datos.date.iloc[inicios].to_numpy())
        np.testing.assert_array_equal(guardado.fin_lectura.to_numpy(), datos.date.iloc[finales].to_numpy())
        np.testing.assert_array_equal(guardado.cobertura_s, (finales-inicios+1)*5)
        assert (guardado.fin-guardado.fin_lectura).eq(pd.Timedelta(seconds=5)).all()
    for ruta, huella in v["huellas_protegidas"].items():
        assert hashlib.sha256((RAIZ/ruta).read_bytes()).hexdigest() == huella


def test_extremos_individuales_reconstruyen_referencias_y_no_pierden_picos():
    """NumPy reproduce medianas/MAD y se contrastan marcas, estados y episodios."""
    datos = pd.read_csv(RAIZ / "data/raw/serie2/data.csv", parse_dates=["date"])
    f = pd.read_csv(SALIDA / "extremos_individuales.csv", parse_dates=["date"])
    referencias = pd.read_csv(SALIDA / "referencias_robustas.csv")
    episodios = pd.read_csv(SALIDA / "episodios_extremos.csv", parse_dates=["inicio", "fin_lectura"])
    sensibilidad = pd.read_csv(SALIDA / "sensibilidad_extremos.csv")
    assert len(f) == len(datos) == 86400
    pd.testing.assert_series_equal(f.date, datos.date)
    np.testing.assert_array_equal(f.fila_fuente, np.arange(len(datos)))
    perfil = f.regimen_cerrado.to_numpy()
    train = np.arange(len(datos)) < 69120
    tags = ["YFJ3_AI.AV_0#", "FT_8306A.AV_0#", "FT_8306B.AV_0#"]
    for tag in tags:
        valores = datos[tag].to_numpy()
        z = np.empty(len(datos))
        for contexto in [0, 1, 2]:
            muestra = valores[train if contexto == 0 else train & (perfil == contexto)]
            mediana = np.nanmedian(muestra)
            mad = np.nanmedian(np.abs(muestra-mediana))
            r = referencias[referencias.tag.eq(tag) & referencias.regimen_cerrado.eq(contexto)].iloc[0]
            assert np.isclose(r.mediana, mediana) and np.isclose(r.mad, mad)
            assert r.lecturas_referencia == np.isfinite(muestra).sum()
            z[perfil == contexto] = (valores[perfil == contexto]-mediana)/(1.4826*mad)
        np.testing.assert_allclose(f[f"z::{tag}"], z, rtol=0, atol=1e-10)
        for limite in [4, 6, 8]:
            marca = np.abs(z) > limite
            cuenta = np.convolve(marca.astype(int), np.ones(6, dtype=int), mode="full")[:len(marca)]
            activa = np.zeros(len(marca), dtype=bool)
            disparo = marca & (cuenta >= 3)
            disparo[:5] = False
            estado, limpias = False, 0
            for i in range(len(marca)):
                if estado:
                    limpias = 0 if marca[i] else limpias+1
                    if limpias == 12:
                        estado = False
                elif disparo[i]:
                    estado, limpias = True, 0
                activa[i] = estado
            inicios = marca & ~np.r_[False, marca[:-1]]
            inicios_activa = activa & ~np.r_[False, activa[:-1]]
            s = sensibilidad[sensibilidad.tag.eq(tag) & sensibilidad.limite_robusto.eq(limite)].iloc[0]
            assert s.lecturas_marcadas == marca.sum()
            assert s.episodios_instantaneos == inicios.sum()
            assert s.inicios_sostenidos == inicios_activa.sum()
            if limite == 6:
                np.testing.assert_array_equal(f[f"marca::{tag}"], marca)
                np.testing.assert_array_equal(f[f"sostenido::{tag}"], activa)
                for tipo, bandera in [("instantaneo", marca), ("sostenido", activa)]:
                    inicio = np.flatnonzero(bandera & ~np.r_[False, bandera[:-1]])
                    fin = np.flatnonzero(bandera & ~np.r_[bandera[1:], False])
                    e = episodios[episodios.tag.eq(tag) & episodios.tipo.eq(tipo)]
                    np.testing.assert_array_equal(e.inicio.to_numpy(), datos.date.iloc[inicio].to_numpy())
                    np.testing.assert_array_equal(e.fin_lectura.to_numpy(), datos.date.iloc[fin].to_numpy())
                    np.testing.assert_array_equal(e.cobertura_s, (fin-inicio+1)*5)
    # Captura retrospectiva, no validación con tres fallas etiquetadas.
    revision = pd.read_csv(SALIDA / "revision_extremos.csv")
    assert len(revision) == 3 and revision.marca_instantanea.all()
    assert not revision.candidata_IF.any()
    assert np.isnan(revision.demora_desde_extremo_s.iloc[0])
    np.testing.assert_array_equal(revision.demora_desde_extremo_s.iloc[1:], [5., 10.])
