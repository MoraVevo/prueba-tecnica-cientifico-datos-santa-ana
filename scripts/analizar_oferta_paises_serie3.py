"""Comparación reproducible de asociaciones anuales de precio y oferta por país."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.analizar_oferta_serie3 import anualizar

PAISES = ["Guatemala", "Indonesia", "Bolivia (Plurinational State of)", "Viet Nam", "Nepal", "Kenya"]
AMBITOS = [*PAISES, "World"]
OBJETIVOS = {"superficie": "Area harvested", "produccion": "Production"}
MODELOS = {"media": [], "propia": ["g_previa"], "precio": ["p_1", "p_2"],
           "propia_precio": ["g_previa", "p_1", "p_2"]}
ANOS = list(range(2004, 2024))


def preparar_celdas(celdas):
    """Mantiene todas las celdas y agrega motivo/flag de revisión sin descartarlas."""
    out = celdas.copy()
    motivos = []
    revisiones = []
    for fila in out.itertuples():
        razon = []
        revision = []
        if fila.area not in AMBITOS:
            razon.append("fuera_de_paises_fijados")
        if fila.ano < 1961 or fila.ano > 2023:
            razon.append("fuera_de_historia_FAOSTAT_1961_2023")
        elif fila.ano <= 2002:
            razon.append("historia_previa_sin_precio_completo")
        elif fila.ano == 2003:
            razon.append("historia_previa_para_cambio_y_rezagos_2004")
        if fila.area in AMBITOS and 1961 <= fila.ano <= 2023:
            if pd.isna(fila.flag) or fila.flag == "":
                revision.append("flag_ausente")
            elif fila.flag != "A":
                revision.append("flag_no_A_conservado_solo_revision")
        motivos.append(";".join(razon))
        revisiones.append(";".join(revision))
    out["motivo_fuera_analisis"] = motivos
    out["motivo_revision"] = revisiones
    out["marca_calidad_solo_revision"] = out.flag.notna() & out.flag.ne("") & out.flag.ne("A")
    out["en_muestra_resultado"] = out.area.isin(AMBITOS) & out.ano.between(2004, 2023)
    return out


def construir_panel(celdas, anual):
    """Prepara series completas y rezagos fijados en el diseño previo."""
    usar = celdas[celdas.area.isin(AMBITOS) & celdas.ano.between(2001, 2023)].copy()
    valores = usar.pivot(index=["area", "ano"], columns="elemento", values="valor")
    flags = usar.pivot(index=["area", "ano"], columns="elemento", values="flag")
    mapa = {**OBJETIVOS, "rendimiento": "Yield"}
    valores = valores.rename(columns={v: k for k, v in mapa.items()})
    flags = flags.rename(columns={v: f"flag_{k}" for k, v in mapa.items()})
    panel = valores.join(flags).reset_index().merge(anual.reset_index(), on="ano", validate="many_to_one")
    panel = panel.sort_values(["area", "ano"]).reset_index(drop=True)
    for area, grupo in panel.groupby("area"):
        assert grupo.ano.tolist() == list(range(2001, 2024)), area
    for objetivo in [*OBJETIVOS, "rendimiento"]:
        assert panel[objetivo].gt(0).all()
        panel[f"log_{objetivo}"] = np.log(panel[objetivo])
        panel[f"g_{objetivo}"] = panel.groupby("area")[f"log_{objetivo}"].diff()
        panel[f"g_previa_{objetivo}"] = panel.groupby("area")[f"g_{objetivo}"].shift(1)
    for nombre in ["precio", "precio_meses", "precio_sin_marcas"]:
        panel[f"log_{nombre}"] = np.log(panel[nombre])
        panel[f"g_{nombre}"] = panel.groupby("area")[f"log_{nombre}"].diff()
        for lag in [0, 1, 2]:
            panel[f"log_{nombre}_{lag}"] = panel.groupby("area")[f"log_{nombre}"].shift(lag)
            panel[f"g_{nombre}_{lag}"] = panel.groupby("area")[f"g_{nombre}"].shift(lag)
    panel["en_muestra"] = panel.ano.isin(ANOS)
    panel["motivo_fuera_muestra"] = np.where(panel.en_muestra, "", "historia_previa_para_cambio_y_rezagos")
    panel["residuo_identidad_log"] = panel.log_produccion-panel.log_superficie-panel.log_rendimiento+np.log(1000)
    return panel


def vista_modelo(grupo, objetivo, precio="precio"):
    return pd.DataFrame({"ano": grupo.ano, "y": grupo[f"g_{objetivo}"],
                         "g_previa": grupo[f"g_previa_{objetivo}"],
                         "p_1": grupo[f"g_{precio}_1"], "p_2": grupo[f"g_{precio}_2"]}).reset_index(drop=True)


def ajustar(datos, modelo):
    """OLS descriptivo con intercepto explícito."""
    rasgos = MODELOS[modelo]
    x = np.column_stack([np.ones(len(datos)), datos[rasgos].to_numpy()])
    assert np.isfinite(x).all() and np.isfinite(datos.y).all()
    beta, _, rango, _ = np.linalg.lstsq(x, datos.y.to_numpy(), rcond=None)
    assert rango == x.shape[1]
    return dict(zip(["intercepto", *rasgos], beta))


def evaluar_temporal(datos):
    filas = []
    for ano in range(2014, 2024):
        train, test = datos[datos.ano < ano], datos[datos.ano == ano]
        assert len(train) >= 10 and len(test) == 1
        for modelo, rasgos in MODELOS.items():
            beta = ajustar(train, modelo)
            pred = beta["intercepto"] + sum(beta[k]*float(test[k].iloc[0]) for k in rasgos)
            filas.append({"ano": ano, "modelo": modelo, "observado": float(test.y.iloc[0]),
                          "prediccion": pred, "n_train": len(train),
                          "ultimo_ano_train": int(train.ano.max()),
                          **{f"beta_{k}": v for k, v in beta.items()}})
    return pd.DataFrame(filas)


def ejecutar(raiz):
    salida = raiz / "outputs/serie3_oferta_paises"
    salida.mkdir(parents=True, exist_ok=True)
    fs = [raiz/"data/raw/serie3/Sugar_data.csv",
          raiz/"outputs/serie3_eda/revision/cana_todas_celdas.csv"]
    huellas = {str(p.relative_to(raiz)): hashlib.sha256(p.read_bytes()).hexdigest() for p in fs}
    crudo, celdas = pd.read_csv(fs[0]), pd.read_csv(fs[1])
    anual, precios_fuera, dias_revision = anualizar(crudo)
    auditoria = preparar_celdas(celdas)
    panel = construir_panel(celdas, anual)
    auditoria.to_csv(salida/"celdas_originales_con_motivos.csv", index=False)
    auditoria[~auditoria.en_muestra_resultado].to_csv(salida/"celdas_fuera_analisis.csv", index=False)
    auditoria[auditoria.area.isin(AMBITOS)].to_csv(salida/"celdas_paises_seleccionados.csv", index=False)
    panel.to_csv(salida/"panel_comparable.csv", index=False)
    panel[~panel.en_muestra].to_csv(salida/"panel_fuera_muestra.csv", index=False)
    precios_fuera.to_csv(salida/"precios_fuera_anual.csv", index=False)
    dias_revision.to_csv(salida/"dias_precio_marcados_revision.csv", index=False)
    anual.reset_index().to_csv(salida/"precio_anual.csv", index=False)
    correlaciones, ajustes, omisiones, predicciones = [], [], [], []
    for area in AMBITOS:
        g = panel[(panel.area == area) & panel.en_muestra].copy()
        assert g.ano.tolist() == ANOS and len(g) == 20
        for objetivo in [*OBJETIVOS, "rendimiento"]:
            for escala in ["log", "g"]:
                for lag in [0, 1, 2]:
                    correlaciones.append({"area": area, "objetivo": objetivo, "escala": escala,
                        "rezago_precio": lag, "n": 20,
                        "correlacion": g[f"{escala}_{objetivo}"].corr(g[f"{escala}_precio_{lag}"])})
            if objetivo == "rendimiento":
                continue
            datos = vista_modelo(g, objetivo)
            for modelo in MODELOS:
                bloques = {"completo_2004_2023": datos}
                if modelo == "propia_precio":
                    bloques["2004_2013"] = datos[datos.ano <= 2013]
                    bloques["2014_2023"] = datos[datos.ano >= 2014]
                for bloque, sub in bloques.items():
                    beta = ajustar(sub, modelo)
                    yhat = beta["intercepto"] + sum(beta[k]*sub[k] for k in MODELOS[modelo])
                    r2 = 1-np.square(sub.y-yhat).sum()/np.square(sub.y-sub.y.mean()).sum()
                    ajustes.append({"area": area, "objetivo": objetivo, "modelo": modelo,
                        "bloque": bloque, "n": len(sub), "r2_descriptivo": r2, **beta})
                for ano in datos.ano:
                    beta = ajustar(datos[datos.ano != ano], modelo)
                    omisiones.append({"area": area, "objetivo": objetivo,
                        "modelo": modelo, "ano_omitido": ano, **beta})
            predicciones.append(evaluar_temporal(datos).assign(area=area, objetivo=objetivo))
            for variante in ["precio_meses", "precio_sin_marcas"]:
                d = vista_modelo(g, objetivo, variante)
                beta = ajustar(d, "propia_precio")
                ajustes.append({"area": area, "objetivo": objetivo,
                    "modelo": f"propia_precio_{variante}", "bloque": "completo_2004_2023",
                    "n": len(d), **beta})
    pd.DataFrame(correlaciones).to_csv(salida/"correlaciones.csv", index=False)
    pd.DataFrame(ajustes).to_csv(salida/"ajustes.csv", index=False)
    pd.DataFrame(omisiones).to_csv(salida/"omitir_un_ano.csv", index=False)
    pred = pd.concat(predicciones, ignore_index=True)
    pred.to_csv(salida/"evaluacion_temporal.csv", index=False)
    metricas = [{"area": area, "objetivo": obj, "modelo": mod, "n": len(g),
                 "MAE_puntos_log": 100*(g.prediccion-g.observado).abs().mean(),
                 "RMSE_puntos_log": 100*np.sqrt(np.square(g.prediccion-g.observado).mean())}
                for (area,obj,mod),g in pred.groupby(["area","objetivo","modelo"])]
    pd.DataFrame(metricas).to_csv(salida/"metricas_temporales.csv", index=False)
    for ruta, huella in huellas.items():
        assert hashlib.sha256((raiz/ruta).read_bytes()).hexdigest() == huella
    conteo = auditoria[auditoria.area.isin(AMBITOS)].groupby(
        ["area","elemento","flag"], dropna=False).size().rename("n").reset_index()
    conteo.to_csv(salida/"conteo_flags.csv", index=False)
    motivos = (auditoria.assign(motivo=auditoria.motivo_fuera_analisis.str.split(";"))
        .explode("motivo").query("motivo != ''").groupby("motivo")
        .size().rename("n_celdas").reset_index())
    motivos.to_csv(salida/"conteos_motivos_fuera_analisis.csv", index=False)
    seleccionadas = auditoria[auditoria.area.isin(AMBITOS)]
    resumen = {"huellas": huellas, "celdas_crudas_totales": len(celdas),
        "celdas_paises_seleccionados": int(auditoria.area.isin(AMBITOS).sum()),
        "celdas_fuera_analisis": int((~auditoria.en_muestra_resultado).sum()),
        "celdas_en_muestra_resultado": int(auditoria.en_muestra_resultado.sum()),
        "filas_panel": len(panel), "paises_comparados": PAISES, "World_solo_contexto": True,
        "n_por_pais_objetivo": 20,
        "flags_distintos_de_A_solo_marcados_1961_2023": int(seleccionadas.marca_calidad_solo_revision.sum()),
        "flags_distintos_de_A_en_muestra_resultado": int(
            seleccionadas.loc[seleccionadas.en_muestra_resultado, "marca_calidad_solo_revision"].sum()),
        "exclusiones_por_flag": 0,
        "residuo_identidad_log_maximo": float(panel.residuo_identidad_log.abs().max()),
        "n_correlaciones": len(correlaciones), "n_ajustes": len(ajustes),
        "n_omisiones": len(omisiones), "estimacion_causal": False,
        "disponibilidad_historica_faostat_certificada": False}
    (salida/"resumen.json").write_text(json.dumps(resumen,ensure_ascii=False,indent=2),encoding="utf-8")
    return resumen


if __name__ == "__main__":
    print(json.dumps(ejecutar(Path(__file__).resolve().parents[1]),ensure_ascii=False,indent=2))
