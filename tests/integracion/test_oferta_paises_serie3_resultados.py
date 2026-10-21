
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "outputs/serie3_oferta_paises"


@pytest.fixture(scope="module", autouse=True)
def generar_salidas_desde_fuentes():
    from scripts.analizar_oferta_paises_serie3 import ejecutar

    ejecutar(RAIZ)


def qr_coeficientes(d, rasgos):
    """Reconstrucción independiente mediante QR, sin llamar al módulo analítico."""
    x = np.column_stack([np.ones(len(d)), d[rasgos].to_numpy()])
    q, r = np.linalg.qr(x, mode="reduced")
    return np.linalg.solve(r, q.T @ d.y.to_numpy())


def test_celdas_crudas_completas_conservan_valor_flag_unidad_y_orden():
    fuente = pd.read_csv(RAIZ / "outputs/serie3_eda/revision/cana_todas_celdas.csv")
    salida = pd.read_csv(SALIDA / "celdas_originales_con_motivos.csv")
    assert len(salida) == len(fuente) == 27648
    assert_frame_equal(salida[fuente.columns], fuente, check_dtype=False)


def test_panel_y_rezagos_se_derivan_de_valores_originales_por_pais():
    """Contraste del supervisor: no reutiliza las transformaciones del panel."""
    fuente = pd.read_csv(RAIZ/"outputs/serie3_eda/revision/cana_todas_celdas.csv")
    precios = pd.read_csv(RAIZ/"data/raw/serie3/Sugar_data.csv", parse_dates=["date"])
    anual = {ano: grupo.close.to_numpy().mean()
             for ano, grupo in precios.groupby(precios.date.dt.year)}
    valores = {(f.area, f.elemento, f.ano): f.valor for f in fuente.itertuples()}
    unidades = {"superficie": ("Area harvested", "ha"), "produccion": ("Production", "t"),
                "rendimiento": ("Yield", "kg/ha")}
    panel = pd.read_csv(SALIDA/"panel_comparable.csv")
    for f in panel[panel.en_muestra].itertuples():
        for nombre, (elemento, unidad) in unidades.items():
            fila = fuente[(fuente.area == f.area) & (fuente.ano == f.ano) & (fuente.elemento == elemento)].iloc[0]
            assert fila.unidad == unidad
            actual = valores[f.area, elemento, f.ano]
            previo = valores[f.area, elemento, f.ano-1]
            anterior = valores[f.area, elemento, f.ano-2]
            assert getattr(f, nombre) == pytest.approx(actual)
            assert getattr(f, f"g_{nombre}") == pytest.approx(np.log(actual/previo), abs=1e-12)
            assert getattr(f, f"g_previa_{nombre}") == pytest.approx(np.log(previo/anterior), abs=1e-12)
        for lag in [0, 1, 2]:
            assert getattr(f, f"g_precio_{lag}") == pytest.approx(
                np.log(anual[f.ano-lag]/anual[f.ano-lag-1]), abs=1e-12)


def test_muestra_comun_flags_visibles_y_exclusiones_con_motivo():
    resumen = __import__("json").loads((SALIDA / "resumen.json").read_text(encoding="utf-8"))
    panel = pd.read_csv(SALIDA / "panel_comparable.csv")
    fuera = pd.read_csv(SALIDA / "celdas_fuera_analisis.csv")
    audit = pd.read_csv(SALIDA / "celdas_originales_con_motivos.csv")
    assert resumen["n_por_pais_objetivo"] == 20
    assert resumen["exclusiones_por_flag"] == 0
    assert resumen["flags_distintos_de_A_en_muestra_resultado"] == 54
    assert all(anos == list(range(2001, 2024))
               for anos in panel.groupby("area").ano.apply(list))
    assert panel[panel.en_muestra].groupby("area").size().eq(20).all()
    assert fuera.motivo_fuera_analisis.fillna("").ne("").all()
    assert audit.loc[audit.en_muestra_resultado, "motivo_fuera_analisis"].fillna("").eq("").all()
    assert audit.loc[audit.en_muestra_resultado, "flag"].notna().all()


def test_pendientes_panel_guardan_historia_previa_con_motivo():
    panel = pd.read_csv(SALIDA / "panel_comparable.csv")
    fuera = pd.read_csv(SALIDA / "panel_fuera_muestra.csv")
    assert len(fuera) == 7*3
    assert set(fuera.ano) == {2001, 2002, 2003}
    assert fuera.motivo_fuera_muestra.eq("historia_previa_para_cambio_y_rezagos").all()
    assert len(panel) == 7*23


def test_correlaciones_reconstruidas_independientemente():
    panel = pd.read_csv(SALIDA / "panel_comparable.csv")
    salida = pd.read_csv(SALIDA / "correlaciones.csv")
    for fila in salida.itertuples():
        g = panel[(panel.area == fila.area) & panel.en_muestra]
        x = g[f"{fila.escala}_precio_{fila.rezago_precio}"].to_numpy()
        y = g[f"{fila.escala}_{fila.objetivo}"].to_numpy()
        assert np.corrcoef(x, y)[0, 1] == pytest.approx(fila.correlacion, abs=1e-12)


def test_ajustes_bloques_y_omisiones_reconstruidos_por_qr():
    panel = pd.read_csv(SALIDA / "panel_comparable.csv")
    ajustes = pd.read_csv(SALIDA / "ajustes.csv")
    omisiones = pd.read_csv(SALIDA / "omitir_un_ano.csv")
    especificaciones = {
        "media": [], "propia": ["g_previa"], "precio": ["p_1", "p_2"],
        "propia_precio": ["g_previa", "p_1", "p_2"],
    }
    for fila in ajustes.itertuples():
        if fila.modelo not in especificaciones:
            continue
        g = panel[(panel.area == fila.area) & panel.en_muestra]
        d = pd.DataFrame({"ano":g.ano, "y":g[f"g_{fila.objetivo}"],
                          "g_previa":g[f"g_previa_{fila.objetivo}"],
                          "p_1":g.g_precio_1, "p_2":g.g_precio_2})
        if fila.bloque == "2004_2013":
            d = d[d.ano <= 2013]
        elif fila.bloque == "2014_2023":
            d = d[d.ano >= 2014]
        b = qr_coeficientes(d, especificaciones[fila.modelo])
        assert fila.intercepto == pytest.approx(b[0], abs=1e-10)
        for k, nombre in enumerate(especificaciones[fila.modelo], start=1):
            assert getattr(fila, nombre) == pytest.approx(b[k], abs=1e-10)
    for fila in omisiones.itertuples():
        g = panel[(panel.area == fila.area) & panel.en_muestra]
        d = pd.DataFrame({"ano":g.ano, "y":g[f"g_{fila.objetivo}"],
                          "g_previa":g[f"g_previa_{fila.objetivo}"],
                          "p_1":g.g_precio_1, "p_2":g.g_precio_2})
        d = d[d.ano != fila.ano_omitido]
        b = qr_coeficientes(d, especificaciones[fila.modelo])
        assert fila.intercepto == pytest.approx(b[0], abs=1e-10)
        for k, nombre in enumerate(especificaciones[fila.modelo], start=1):
            assert getattr(fila, nombre) == pytest.approx(b[k], abs=1e-10)


def test_predicciones_temporales_y_metricas_se_reconstruyen():
    panel = pd.read_csv(SALIDA / "panel_comparable.csv")
    pred = pd.read_csv(SALIDA / "evaluacion_temporal.csv")
    metricas = pd.read_csv(SALIDA / "metricas_temporales.csv")
    rasgos = {"media": [], "propia": ["g_previa"], "precio": ["p_1", "p_2"],
              "propia_precio": ["g_previa", "p_1", "p_2"]}
    for fila in pred.itertuples():
        g = panel[(panel.area == fila.area) & panel.en_muestra]
        d = pd.DataFrame({"ano":g.ano, "y":g[f"g_{fila.objetivo}"],
                          "g_previa":g[f"g_previa_{fila.objetivo}"],
                          "p_1":g.g_precio_1, "p_2":g.g_precio_2})
        train, test = d[d.ano < fila.ano], d[d.ano == fila.ano]
        b = qr_coeficientes(train, rasgos[fila.modelo])
        x = np.r_[1.0, test[rasgos[fila.modelo]].to_numpy()[0]]
        assert float(x @ b) == pytest.approx(fila.prediccion, abs=1e-10)
    recalculadas = pred.assign(error=lambda d: d.prediccion-d.observado).groupby(
        ["area","objetivo","modelo"]).error.agg(
            MAE_puntos_log=lambda x:100*x.abs().mean(),
            RMSE_puntos_log=lambda x:100*np.sqrt(np.square(x).mean())).reset_index()
    merged = metricas.merge(recalculadas,on=["area","objetivo","modelo"],suffixes=("_csv","_ind"))
    assert np.allclose(merged.MAE_puntos_log_csv, merged.MAE_puntos_log_ind, atol=1e-10)
    assert np.allclose(merged.RMSE_puntos_log_csv, merged.RMSE_puntos_log_ind, atol=1e-10)
