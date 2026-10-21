"""Reconstrucción independiente de cruces, regresiones y errores anuales."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


RAIZ = Path(__file__).resolve().parents[2]
OUT = RAIZ / "outputs/serie3_oferta"
RASGOS = {"media": [], "propia": ["g_previa"], "precio": ["p_1", "p_2"],
          "propia_precio": ["g_previa", "p_1", "p_2"]}


def test_conservacion_anual_unidades_flags_y_rezagos_desde_crudos():
    r = json.loads((OUT / "resumen.json").read_text(encoding="utf-8"))
    for ruta, huella in r["huellas"].items():
        assert hashlib.sha256((RAIZ / ruta).read_bytes()).hexdigest() == huella
    raw = pd.read_csv(RAIZ / "data/raw/serie3/Sugar_data.csv", parse_dates=["date"])
    dentro = raw[raw.date.dt.year.between(2001, 2023)]
    fuera = pd.read_csv(OUT / "precios_fuera_anual.csv", parse_dates=["date"])
    pd.testing.assert_frame_equal(fuera[raw.columns].reset_index(drop=True),
        raw[~raw.date.dt.year.between(2001, 2023)].reset_index(drop=True))
    assert len(dentro) == 5766 and len(fuera) == 331 and fuera.motivo_fuera_anual.notna().all()
    a = pd.read_csv(OUT / "precio_anual.csv").set_index("ano")
    for ano, d in dentro.groupby(dentro.date.dt.year):
        np.testing.assert_allclose(a.loc[ano, "precio"], np.mean(d.close.to_numpy()))
        medias = [d.loc[d.date.dt.month.eq(mes), "close"].to_numpy().mean() for mes in range(1, 13)]
        np.testing.assert_allclose(a.loc[ano, "precio_meses"], np.mean(medias))
        marca = (d.high+1e-5 < d[["open", "close", "low"]].max(axis=1)) | (
            d.low-1e-5 > d[["open", "close", "high"]].min(axis=1)) | d.volume.eq(0)
        np.testing.assert_allclose(a.loc[ano, "precio_sin_marcas"], d.loc[~marca, "close"].mean())
    c = pd.read_csv(RAIZ / "outputs/serie3_eda/revision/cana_todas_celdas.csv")
    usadas = pd.read_csv(OUT / "celdas_panel.csv")
    otras = pd.read_csv(OUT / "faostat_fuera_panel.csv")
    assert len(usadas) == 138 and len(otras) == 27510
    claves = ["fila_fuente", "ano"]
    unidas = pd.concat([usadas, otras]).sort_values(claves).reset_index(drop=True)
    # Los CSV con una columna enteramente vacía infieren float al releer;
    # normalizar tipos no cambia ninguna medición ni su máscara de faltantes.
    pd.testing.assert_frame_equal(unidas[c.columns].astype(c.dtypes.to_dict()),
        c.sort_values(claves).reset_index(drop=True))
    assert otras.motivo_fuera_panel.notna().all()
    panel = pd.read_csv(OUT / "panel_anual.csv")
    raw_fao = pd.read_csv(RAIZ / "data/raw/serie3/Production_Crops_Livestock_E_All_Data.csv", low_memory=False)
    sc = raw_fao[raw_fao.Item.eq("Sugar cane")].set_index(["Area", "Element"])
    for fila in panel.itertuples():
        for nombre, elemento in [("superficie", "Area harvested"), ("produccion", "Production"), ("rendimiento", "Yield")]:
            np.testing.assert_allclose(getattr(fila, nombre), sc.loc[(fila.area, elemento), f"Y{fila.ano}"])
            assert getattr(fila, f"flag_{nombre}") == sc.loc[(fila.area, elemento), f"Y{fila.ano}F"]
            vector = sc.loc[(fila.area, elemento)]
            if fila.ano >= 2002:
                np.testing.assert_allclose(getattr(fila, f"g_{nombre}"),
                    np.log(vector[f"Y{fila.ano}"]/vector[f"Y{fila.ano-1}"]), atol=1e-14)
            if fila.ano >= 2003:
                np.testing.assert_allclose(getattr(fila, f"g_previa_{nombre}"),
                    np.log(vector[f"Y{fila.ano-1}"]/vector[f"Y{fila.ano-2}"]), atol=1e-14)
        if fila.en_muestra:
            for lag in [0, 1, 2]:
                np.testing.assert_allclose(getattr(fila, f"g_precio_{lag}"),
                    np.log(a.loc[fila.ano-lag, "precio"]/a.loc[fila.ano-lag-1, "precio"]), atol=1e-14)
    assert panel.en_muestra.sum() == 40 and len(panel) == 46
    omitidos = pd.read_csv(OUT / "anos_fuera_muestra.csv")
    assert len(omitidos) == 6 and omitidos.motivo_fuera_muestra.notna().all()
    dias = pd.read_csv(OUT / "dias_fuera_sensibilidad.csv")
    assert len(dias) == 99 and dias.motivo_sensibilidad.notna().all()
    assert panel.residuo_identidad_log.abs().max() < 3e-6


def datos(g, objetivo, variante="precio"):
    return pd.DataFrame({"ano": g.ano, "y": g[f"g_{objetivo}"], "g_previa": g[f"g_previa_{objetivo}"],
                         "p_1": g[f"g_{variante}_1"], "p_2": g[f"g_{variante}_2"]})


def coef_qr(d, modelo):
    x = np.column_stack([np.ones(len(d)), d[RASGOS[modelo]].values])
    q, r = np.linalg.qr(x)
    return np.linalg.solve(r, q.T @ d.y.to_numpy())


def test_correlaciones_ajustes_y_sensibilidades_por_otra_solucion_matricial():
    p = pd.read_csv(OUT / "panel_anual.csv")
    p = p[p.en_muestra]
    for f in pd.read_csv(OUT / "correlaciones.csv").itertuples():
        g = p[p.area.eq(f.area)]
        esperado = np.corrcoef(g[f"{f.escala}_{f.objetivo}"], g[f"{f.escala}_precio_{f.rezago}"])[0, 1]
        np.testing.assert_allclose(f.r, esperado)
    for f in pd.read_csv(OUT / "ajustes.csv").itertuples():
        d = datos(p[p.area.eq(f.area)], f.objetivo, f.variante)
        if f.bloque == "2004_2013": d = d[d.ano <= 2013]
        if f.bloque == "2014_2023": d = d[d.ano >= 2014]
        nombres = ["intercepto"] + RASGOS[f.modelo]
        np.testing.assert_allclose([getattr(f, k) for k in nombres], coef_qr(d, f.modelo), atol=1e-12)
        assert f.n == len(d)
    for f in pd.read_csv(OUT / "omitir_un_ano.csv").itertuples():
        d = datos(p[p.area.eq(f.area) & p.ano.ne(f.ano_omitido)], f.objetivo)
        np.testing.assert_allclose([f.intercepto, f.g_previa, f.p_1, f.p_2], coef_qr(d, "propia_precio"), atol=1e-12)


def test_predicciones_estrictamente_anteriores_y_metricas_reconstruidas():
    panel = pd.read_csv(OUT / "panel_anual.csv")
    panel = panel[panel.en_muestra]
    pred = pd.read_csv(OUT / "evaluacion_temporal.csv")
    assert len(pred) == 240
    for f in pred.itertuples():
        d = datos(panel[panel.area.eq(f.area)], f.objetivo)
        train = d[d.ano < f.ano]
        test = d[d.ano.eq(f.ano)]
        b = coef_qr(train, f.modelo)
        x = np.r_[1., test[RASGOS[f.modelo]].values.ravel()]
        np.testing.assert_allclose(f.prediccion, x @ b, atol=1e-12)
        np.testing.assert_allclose(f.observado, test.y.iloc[0])
        assert f.n_train == len(train) and f.ultimo_ano_train == train.ano.max() == f.ano-1
    for f in pd.read_csv(OUT / "metricas_temporales.csv").itertuples():
        g = pred[pred.area.eq(f.area) & pred.objetivo.eq(f.objetivo) & pred.modelo.eq(f.modelo)]
        e = (g.prediccion-g.observado).values
        assert f.n == len(g) == 10
        np.testing.assert_allclose(f.MAE_puntos_log, 100*np.mean(np.abs(e)))
        np.testing.assert_allclose(f.RMSE_puntos_log, 100*np.sqrt(np.mean(e**2)))
