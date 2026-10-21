"""Asociación anual entre precio publicado y oferta de caña; no identifica causas."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.analizar_precios_serie3 import preparar


OBJETIVOS = {"superficie": "Area harvested", "produccion": "Production", "rendimiento": "Yield"}
MODELOS = {"media": [], "propia": ["g_previa"],
           "precio": ["p_1", "p_2"], "propia_precio": ["g_previa", "p_1", "p_2"]}


def anualizar(crudo):
    """Conserva días originales y aparta años truncados, sin rellenar sesiones."""
    p = preparar(crudo)
    p["ano"] = p.date.dt.year
    p["mes"] = p.date.dt.month
    p["motivo_fuera_anual"] = np.select(
        [p.ano.eq(2000), p.ano.eq(2024)],
        ["2000_comienza_en_marzo", "2024_parcial_y_fuera_FAOSTAT_1961_2023"], default="")
    dentro = p[p.motivo_fuera_anual.eq("")].copy()
    assert dentro.ano.between(2001, 2023).all()
    assert dentro.groupby("ano").mes.nunique().eq(12).all()
    anual = dentro.groupby("ano").agg(precio=("close", "mean"), n_dias=("close", "size"),
        primera_fecha=("date", "min"), ultima_fecha=("date", "max"))
    anual["precio_meses"] = dentro.groupby(["ano", "mes"]).close.mean().groupby("ano").mean()
    marca = dentro.ohlc_incoherente | dentro.volumen_cero
    dentro["motivo_sensibilidad"] = [";".join(r) for r in zip(
        np.where(dentro.ohlc_incoherente, "OHLC_incoherente", ""),
        np.where(dentro.volumen_cero, "volumen_cero", ""))]
    dentro["motivo_sensibilidad"] = dentro.motivo_sensibilidad.str.strip(";")
    anual["precio_sin_marcas"] = dentro[~marca].groupby("ano").close.mean()
    anual["n_marcas"] = dentro.groupby("ano").motivo_sensibilidad.apply(lambda s: s.ne("").sum())
    assert anual.index.tolist() == list(range(2001, 2024))
    return anual, p[p.motivo_fuera_anual.ne("")].copy(), dentro[marca].copy()


def construir_panel(celdas, anual):
    """Une por año calendario, mantiene flags y calcula rezagos antes de seleccionar."""
    c = celdas.copy()
    c["motivo_fuera_panel"] = [";".join(x for x in r if x) for r in zip(
        np.where(~c.area.isin(["Guatemala", "World"]), "otro_ambito_geografico", ""),
        np.where(~c.ano.between(2001, 2023), "sin_precio_anual_completo_en_ambito", ""))]
    usada = c[c.motivo_fuera_panel.eq("")].copy()
    valores = usada.pivot(index=["area", "ano"], columns="elemento", values="valor")
    flags = usada.pivot(index=["area", "ano"], columns="elemento", values="flag")
    valores = valores.rename(columns={v: k for k, v in OBJETIVOS.items()})
    flags = flags.rename(columns={v: f"flag_{k}" for k, v in OBJETIVOS.items()})
    panel = valores.join(flags).reset_index().merge(anual.reset_index(), on="ano", validate="many_to_one")
    panel = panel.sort_values(["area", "ano"]).reset_index(drop=True)
    for area, g in panel.groupby("area"):
        assert g.ano.tolist() == list(range(2001, 2024)), area
    for k in OBJETIVOS:
        assert panel[k].gt(0).all()
        panel[f"log_{k}"] = np.log(panel[k])
        panel[f"g_{k}"] = panel.groupby("area")[f"log_{k}"].diff()
        panel[f"g_previa_{k}"] = panel.groupby("area")[f"g_{k}"].shift(1)
    for precio in ["precio", "precio_meses", "precio_sin_marcas"]:
        panel[f"log_{precio}"] = np.log(panel[precio])
        panel[f"g_{precio}"] = panel.groupby("area")[f"log_{precio}"].diff()
        for lag in [0, 1, 2]:
            panel[f"log_{precio}_{lag}"] = panel.groupby("area")[f"log_{precio}"].shift(lag)
            panel[f"g_{precio}_{lag}"] = panel.groupby("area")[f"g_{precio}"].shift(lag)
    panel["en_muestra"] = panel.ano.between(2004, 2023)
    panel["motivo_fuera_muestra"] = np.where(panel.en_muestra, "", "historia_insuficiente_para_cambio_precio_rezagado_dos_anos")
    panel["residuo_identidad_log"] = panel.log_produccion - panel.log_superficie - panel.log_rendimiento + np.log(1000)
    return panel, c[c.motivo_fuera_panel.ne("")].copy(), usada


def vista_modelo(g, objetivo, precio="precio"):
    """Los predictores de precio son exclusivamente t-1 y t-2."""
    return pd.DataFrame({"ano": g.ano, "y": g[f"g_{objetivo}"],
        "g_previa": g[f"g_previa_{objetivo}"],
        "p_1": g[f"g_{precio}_1"], "p_2": g[f"g_{precio}_2"]})


def ajustar(d, modelo):
    """Mínimos cuadrados sin penalización; intercepto explícito y rango comprobado."""
    x = np.column_stack([np.ones(len(d)), d[MODELOS[modelo]].to_numpy()])
    assert np.isfinite(x).all() and np.isfinite(d.y).all()
    b, _, rango, _ = np.linalg.lstsq(x, d.y.to_numpy(), rcond=None)
    assert rango == x.shape[1]
    return dict(zip(["intercepto"] + MODELOS[modelo], b))


def evaluar_temporal(d):
    """Diagnóstico retrospectivo con versión final, sin afirmar disponibilidad real."""
    filas = []
    for ano in range(2014, 2024):
        train, test = d[d.ano < ano], d[d.ano.eq(ano)]
        assert len(train) >= 10 and len(test) == 1
        for modelo, rasgos in MODELOS.items():
            b = ajustar(train, modelo)
            pred = b["intercepto"] + sum(b[k]*float(test[k].iloc[0]) for k in rasgos)
            filas.append({"ano": ano, "modelo": modelo, "observado": float(test.y.iloc[0]),
                "prediccion": pred, "n_train": len(train), "ultimo_ano_train": int(train.ano.max()),
                **{f"beta_{k}": v for k, v in b.items()}})
    return pd.DataFrame(filas)


def ejecutar(raiz):
    salida = raiz / "outputs/serie3_oferta"
    salida.mkdir(parents=True, exist_ok=True)
    fuentes = [raiz / "data/raw/serie3/Sugar_data.csv", raiz / "outputs/serie3_eda/revision/cana_todas_celdas.csv"]
    huellas = {str(p.relative_to(raiz)): hashlib.sha256(p.read_bytes()).hexdigest() for p in fuentes}
    crudo, celdas = pd.read_csv(fuentes[0]), pd.read_csv(fuentes[1])
    anual, fuera_precio, revision = anualizar(crudo)
    panel, fuera_fao, usada = construir_panel(celdas, anual)
    for nombre, tabla in {"precio_anual": anual.reset_index(), "precios_fuera_anual": fuera_precio,
            "dias_fuera_sensibilidad": revision, "panel_anual": panel, "celdas_panel": usada,
            "faostat_fuera_panel": fuera_fao, "anos_fuera_muestra": panel[~panel.en_muestra]}.items():
        tabla.to_csv(salida / f"{nombre}.csv", index=False)
    correlaciones, ajustes, omisiones, predicciones = [], [], [], []
    for area, g in panel[panel.en_muestra].groupby("area"):
        assert len(g) == 20
        for objetivo in OBJETIVOS:
            for escala in ["log", "g"]:
                for lag in [0, 1, 2]:
                    correlaciones.append({"area": area, "objetivo": objetivo, "escala": escala,
                        "rezago": lag, "n": len(g),
                        "r": g[f"{escala}_{objetivo}"].corr(g[f"{escala}_precio_{lag}"])})
            for variante in ["precio", "precio_meses", "precio_sin_marcas"]:
                d = vista_modelo(g, objetivo, variante)
                modelos = MODELOS if variante == "precio" else ["propia_precio"]
                for modelo in modelos:
                    bloques = {"completo": d}
                    if modelo == "propia_precio" and variante == "precio":
                        bloques.update({"2004_2013": d[d.ano <= 2013], "2014_2023": d[d.ano >= 2014]})
                    for bloque, datos in bloques.items():
                        b = ajustar(datos, modelo)
                        estimado = b["intercepto"] + sum(b[k]*datos[k] for k in MODELOS[modelo])
                        r2 = 1 - np.square(datos.y-estimado).sum()/np.square(datos.y-datos.y.mean()).sum()
                        ajustes.append({"area": area, "objetivo": objetivo, "variante": variante,
                            "modelo": modelo, "bloque": bloque, "n": len(datos), "r2": r2, **b})
                if variante == "precio":
                    predicciones.append(evaluar_temporal(d).assign(area=area, objetivo=objetivo))
                    for ano in d.ano:
                        b = ajustar(d[d.ano.ne(ano)], "propia_precio")
                        omisiones.append({"area": area, "objetivo": objetivo, "ano_omitido": ano, **b})
    pd.DataFrame(correlaciones).to_csv(salida / "correlaciones.csv", index=False)
    pd.DataFrame(ajustes).to_csv(salida / "ajustes.csv", index=False)
    pd.DataFrame(omisiones).to_csv(salida / "omitir_un_ano.csv", index=False)
    pred = pd.concat(predicciones, ignore_index=True)
    pred.to_csv(salida / "evaluacion_temporal.csv", index=False)
    metricas = [{"area": area, "objetivo": objetivo, "modelo": modelo, "n": len(g),
        "MAE_puntos_log": 100*(g.prediccion-g.observado).abs().mean(),
        "RMSE_puntos_log": 100*np.sqrt(np.square(g.prediccion-g.observado).mean())}
        for (area, objetivo, modelo), g in pred.groupby(["area", "objetivo", "modelo"])]
    pd.DataFrame(metricas).to_csv(salida / "metricas_temporales.csv", index=False)
    for p in fuentes:
        assert hashlib.sha256(p.read_bytes()).hexdigest() == huellas[str(p.relative_to(raiz))]
    resumen = {"huellas": huellas, "filas_precio_crudo": len(crudo),
        "filas_precio_anual": int(anual.n_dias.sum()), "filas_precio_fuera": len(fuera_precio),
        "dias_marcados_sensibilidad": len(revision), "anos_precio_completo": len(anual),
        "celdas_faostat": len(celdas), "celdas_en_panel": len(usada), "celdas_fuera_panel": len(fuera_fao),
        "filas_panel": len(panel), "filas_muestra": int(panel.en_muestra.sum()),
        "filas_fuera_muestra": int((~panel.en_muestra).sum()),
        "max_residuo_identidad_log": float(panel.residuo_identidad_log.abs().max()),
        "n_por_ambito": 20, "evaluaciones_por_ambito_objetivo_modelo": 10,
        "identificacion_causal": False, "disponibilidad_historica_FAOSTAT_certificada": False,
        "exclusiones_por_error_demostrado": 0, "rejilla_ampliada_por_resultados": False}
    (salida / "resumen.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    return resumen


if __name__ == "__main__":
    print(json.dumps(ejecutar(Path(__file__).resolve().parents[1]), ensure_ascii=True, indent=2))
