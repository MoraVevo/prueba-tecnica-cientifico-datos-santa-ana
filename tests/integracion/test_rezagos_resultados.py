"""Revisión independiente: tiempos, correlaciones y solución matricial de Ridge."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "outputs/rezagos"
OBJETIVO = "ZZQBCHLL.AV_0#"


def test_conservacion_y_seleccion_de_rezagos_sin_futuro():
    control = json.loads((SALIDA / "verificacion.json").read_text(encoding="utf-8"))
    for ruta, huella in control["huellas_protegidas"].items():
        assert hashlib.sha256((RAIZ / ruta).read_bytes()).hexdigest() == huella
    crudo = pd.read_csv(RAIZ / "data/raw/serie2/data.csv", parse_dates=["date"])
    traza = pd.read_csv(SALIDA / "trazabilidad_filas.csv", parse_dates=["date"])
    fuera = pd.read_csv(SALIDA / "filas_excluidas.csv")
    pd.testing.assert_frame_equal(crudo, traza[crudo.columns])
    assert len(traza) == 86400 and traza.fila_original.is_unique
    assert traza.uso.eq("elegible").sum() == 34494
    assert len(fuera) == 51906 and fuera.motivo.notna().all()
    pd.testing.assert_frame_equal(fuera, traza[traza.uso.eq("fuera_del_estudio")]
                                  .assign(date=lambda t: t.date.astype(str)).reset_index(drop=True))
    rejilla = crudo.iloc[::2].set_index("date")
    correlaciones = pd.read_csv(SALIDA / "correlaciones_entrenamiento.csv")
    seleccion = pd.read_csv(SALIDA / "rezagos_por_entrenamiento.csv")
    particiones = pd.read_csv(RAIZ / "outputs/serie2_particiones.csv").iloc[:3]
    # Reconstrucción con arrays y corrcoef, sin helpers ni corrwith.
    for _, corte in particiones.iterrows():
        mascara = (rejilla.index >= rejilla.index[0] + pd.Timedelta(seconds=660)) & (
            rejilla.index <= pd.Timestamp(corte.fin_entrenamiento))
        for sensor, grupo in correlaciones[correlaciones.particion == corte.particion].groupby("sensor"):
            for f in grupo.itertuples():
                n = f.cambio_s // 10
                a, b = rejilla[sensor].to_numpy(), rejilla[OBJETIVO].to_numpy()
                if n:
                    a = np.r_[np.full(n, np.nan), a[n:] - a[:-n]]
                    b = np.r_[np.full(n, np.nan), b[n:] - b[:-n]]
                k = f.rezago_s // 10
                a = np.r_[np.full(k, np.nan), a[:-k]] if k else a
                a, b = a[mascara], b[mascara]
                validos = np.isfinite(a) & np.isfinite(b)
                assert validos.sum() == f.n_pares
                np.testing.assert_allclose(np.corrcoef(a[validos], b[validos])[0, 1], f.correlacion, atol=1e-12)
            positivos = grupo[(grupo.cambio_s == 10) & (grupo.rezago_s > 0)].copy()
            elegido = positivos.iloc[np.argmax(np.abs(positivos.correlacion.to_numpy()))].rezago_s
            guardado = seleccion[(seleccion.particion == corte.particion) & (seleccion.sensor == sensor)]
            assert elegido == guardado.rezago_s.iloc[0]
    assert not control["dia5_evaluado"] and not control["objetivo_pasado_como_entrada"]


def test_predicciones_reconstruidas_con_historia_por_busqueda_de_timestamp():
    datos = pd.read_csv(RAIZ / "data/raw/serie2/data.csv", parse_dates=["date"]).iloc[::2].set_index("date")
    origen = datos.index[0]
    pred = pd.read_csv(SALIDA / "predicciones.csv", parse_dates=["date"])
    assert len(pred) == 155520 and pred.date.lt(origen + pd.Timedelta(days=4)).all()
    columnas = pd.read_csv(RAIZ / "outputs/serie2_selecciones_por_pliegue.csv")
    seleccion = pd.read_csv(SALIDA / "rezagos_por_entrenamiento.csv")
    limites = pd.read_csv(RAIZ / "outputs/serie2_particiones.csv").iloc[:3]
    metricas = pd.read_csv(SALIDA / "metricas.csv").set_index(["particion", "variante"])
    presiones = {"PTCA_8322A.AV_0#", "PTCA_8324.AV_0#"}
    for _, corte in limites.iterrows():
        nombre = corte.particion
        train = (datos.index >= origen + pd.Timedelta(seconds=660)) & (
            datos.index <= pd.Timestamp(corte.fin_entrenamiento))
        for variante, p in pred[pred.particion == nombre].groupby("variante", sort=False):
            assert len(p) == 8640 and p.date.is_unique
            columnas_base = (datos.drop(columns=OBJETIVO).columns.tolist() if variante.startswith("29")
                             else columnas.loc[columnas.particion == nombre, "entrada"].tolist())
            historicas = []
            if "+ rezagos" in variante:
                historicas = columnas_base
            elif "dos presiones" in variante:
                historicas = list(presiones)
            elif "otras trece" in variante:
                historicas = [c for c in columnas_base if c not in presiones]
            a, b = datos.loc[train, columnas_base].to_numpy(), datos.loc[p.date, columnas_base].to_numpy()
            for f in seleccion[seleccion.particion == nombre].itertuples():
                if f.sensor in historicas:
                    # Reindex por fecha exacta; no shift compartido con implementación.
                    pasado_train = datos[f.sensor].reindex(datos.index[train] - pd.Timedelta(seconds=f.rezago_s)).values
                    pasado_eval = datos[f.sensor].reindex(pd.DatetimeIndex(p.date) - pd.Timedelta(seconds=f.rezago_s)).values
                    a, b = np.column_stack([a, pasado_train]), np.column_stack([b, pasado_eval])
            medianas = np.nanmedian(a, axis=0)
            a, b = np.where(np.isnan(a), medianas, a), np.where(np.isnan(b), medianas, b)
            media, escala = a.mean(axis=0), a.std(axis=0)
            a, b = (a - media) / escala, (b - media) / escala
            y = datos.loc[train, OBJETIVO].values
            coef = np.linalg.solve(a.T @ a + 100 * np.eye(a.shape[1]), a.T @ (y - y.mean()))
            esperado = y.mean() + b @ coef
            np.testing.assert_allclose(p.estimado, esperado, atol=1e-8, rtol=1e-9)
            np.testing.assert_array_equal(p.observado, datos.loc[p.date, OBJETIVO].values)
            errores = p.estimado.values - p.observado.values
            fila = metricas.loc[(nombre, variante)]
            assert fila.n_train == train.sum() and fila.n_eval == len(p)
            assert fila.entradas == a.shape[1]
            np.testing.assert_allclose(fila.MAE, np.abs(errores).mean(), atol=1e-12)
            np.testing.assert_allclose(fila.RMSE, np.sqrt(np.mean(errores ** 2)), atol=1e-12)
            np.testing.assert_allclose(fila.WAPE_pct, 100 * np.abs(errores).sum() / np.abs(p.observado).sum(), atol=1e-12)
    resumen = pd.read_csv(SALIDA / "resumen.csv").set_index("variante")
    for variante, grupo in pred.groupby("variante"):
        np.testing.assert_allclose(resumen.loc[variante, "MAE_medio"], np.abs(grupo.estimado - grupo.observado).mean())
        np.testing.assert_allclose(resumen.loc[variante, "WAPE_agregado"],
                                  100 * np.abs(grupo.estimado - grupo.observado).sum() / np.abs(grupo.observado).sum())
    anterior = pd.read_csv(RAIZ / "outputs/serie2_predicciones_validacion.csv")
    anterior = anterior[(anterior.modelo == "Ridge") & (anterior.variante == "Reducida 15")]
    reproduccion = pd.read_csv(SALIDA / "reproduccion_base_original.csv").set_index("particion")
    for nombre, filas in anterior.groupby("particion"):
        np.testing.assert_allclose(np.abs(filas.estimado - filas.observado).mean(),
                                   reproduccion.loc[nombre, "MAE"], atol=1e-12)
