"""Orientación de rezagos y ajustes con resultados conocidos."""

import numpy as np
import pandas as pd

from scripts.analizar_oferta_serie3 import ajustar, construir_panel, evaluar_temporal


def test_rezagos_son_cambios_de_anos_anteriores_y_no_miran_futuro():
    anos = np.arange(2001, 2024)
    anual = pd.DataFrame({"precio": np.exp(.03*np.arange(23)**1.2)}, index=anos)
    anual.index.name = "ano"
    anual["precio_meses"] = anual.precio
    anual["precio_sin_marcas"] = anual.precio
    celdas = pd.DataFrame([{"area": area, "ano": ano, "elemento": e, "valor": v, "flag": "A"}
        for area in ["Guatemala", "World"] for ano in anos
        for e, v in [("Area harvested", 100+ano), ("Yield", 50000.),
                     ("Production", (100+ano)*50)]])
    panel, _, _ = construir_panel(celdas, anual)
    fila = panel[(panel.area == "Guatemala") & panel.ano.eq(2014)].iloc[0]
    np.testing.assert_allclose(fila.g_precio_1, np.log(anual.loc[2013, "precio"]/anual.loc[2012, "precio"]))
    np.testing.assert_allclose(fila.g_precio_2, np.log(anual.loc[2012, "precio"]/anual.loc[2011, "precio"]))
    assert panel.residuo_identidad_log.abs().max() < 1e-12
    alterado = anual.copy()
    alterado.loc[2014:, ["precio", "precio_meses", "precio_sin_marcas"]] *= 10
    nuevo, _, _ = construir_panel(celdas, alterado)
    cols = ["g_precio_1", "g_precio_2"]
    pd.testing.assert_frame_equal(panel.loc[panel.ano <= 2014, cols], nuevo.loc[nuevo.ano <= 2014, cols])


def test_coeficientes_conocidos_y_evaluacion_sin_objetivo_futuro():
    rng = np.random.default_rng(16)
    d = pd.DataFrame(rng.normal(size=(20, 3)), columns=["g_previa", "p_1", "p_2"])
    d["ano"] = np.arange(2004, 2024)
    d["y"] = .02 + .3*d.g_previa + .1*d.p_1 - .2*d.p_2
    b = ajustar(d, "propia_precio")
    np.testing.assert_allclose(list(b.values()), [.02, .3, .1, -.2], atol=1e-14)
    base = evaluar_temporal(d)
    assert len(base) == 40 and (base.ultimo_ano_train < base.ano).all()
    alterado = d.copy()
    alterado.loc[alterado.ano >= 2018, "y"] += 50
    nuevo = evaluar_temporal(alterado)
    np.testing.assert_allclose(base.loc[base.ano <= 2018, "prediccion"],
                               nuevo.loc[nuevo.ano <= 2018, "prediccion"])
    assert not np.allclose(base.loc[base.ano > 2018, "prediccion"], nuevo.loc[nuevo.ano > 2018, "prediccion"])
