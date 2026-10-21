"""Evalúa la estabilidad del ranking económico completo de Serie I."""

from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd


RAIZ = Path(__file__).resolve().parents[1]
ENTRADA = RAIZ / "data" / "processed" / "serie1_etl_provisional.csv"
SALIDA = RAIZ / "outputs" / "serie1_ranking"
PRECIOS = (0.15, 0.20, 0.25)
REFERENCIA = "L01-299"
REPLICAS = int(os.environ.get("RANKING_REPLICAS", "500"))
SEMILLA = 20261020


def preparar_celdas(filas: pd.DataFrame, ajustado: bool) -> pd.DataFrame:
    """Agrega repeticiones y construye expectativas por variedad y corte."""
    celdas = filas.groupby(
        ["CLONE", "CROP", "YEAR", "LOC"], as_index=False, observed=True
    )[["T_SPACRE", "TCA"]].mean()
    if not ajustado:
        return celdas

    ref = celdas.loc[
        celdas.CLONE.eq(REFERENCIA),
        ["CROP", "YEAR", "LOC", "T_SPACRE", "TCA"],
    ].rename(columns={"T_SPACRE": "AZUCAR_REF", "TCA": "CANA_REF"})
    comunes = celdas.merge(
        ref, on=["CROP", "YEAR", "LOC"], how="inner", validate="many_to_one"
    )
    comunes["AZUCAR_DIF"] = comunes.T_SPACRE - comunes.AZUCAR_REF
    comunes["CANA_DIF"] = comunes.TCA - comunes.CANA_REF
    return comunes


def evaluar_base(filas: pd.DataFrame, precio: float, ajustado: bool) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Reproduce el procedimiento sin remuestreo para reconciliar el notebook."""
    celdas = preparar_celdas(filas, ajustado)
    if ajustado:
        ref = celdas.loc[celdas.CLONE.eq(REFERENCIA)]
        medio_ref = ref.groupby("CROP")[["T_SPACRE", "TCA"]].mean()
        dif = celdas.groupby(["CLONE", "CROP"])[["AZUCAR_DIF", "CANA_DIF"]].mean()
        dif = dif.rename(columns={"AZUCAR_DIF": "T_SPACRE", "CANA_DIF": "TCA"})
        medias = dif.add(medio_ref, level="CROP").reset_index()
    else:
        medias = celdas.groupby(["CLONE", "CROP"])[["T_SPACRE", "TCA"]].mean().reset_index()

    conteo = celdas.groupby(["CLONE", "CROP"]).agg(
        anios=("YEAR", "nunique"), localidades=("LOC", "nunique"),
        ambientes=("YEAR", "size"),
    ).reset_index()
    resumen = medias.merge(conteo, on=["CLONE", "CROP"], validate="one_to_one")
    politicas, elegibilidad = _politicas_desde_resumen(resumen, precio)
    return politicas, elegibilidad, resumen


def _politicas_desde_resumen(resumen: pd.DataFrame, precio: float, universo: list[str] | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Aplica cobertura consecutiva y maximiza aporte entre duraciones admisibles."""
    politicas: list[dict] = []
    elegibilidad: list[dict] = []
    grupos = {clon: grupo for clon, grupo in resumen.groupby("CLONE", sort=True)}
    for clon in sorted(universo if universo is not None else grupos):
        if clon not in grupos:
            elegibilidad.append({"CLONE": clon, "ELEGIBLE": False, "MAX_CROP_ADMISIBLE": -1,
                                 "MOTIVO": "Ausente: sin ambiente comparable o sin filas económicas utilizables en la réplica."})
            continue
        grupo = grupos[clon]
        cortes = grupo.set_index("CROP")
        ultimo_admisible = -1
        for crop in range(4):
            if crop not in cortes.index:
                break
            fila = cortes.loc[crop]
            if fila.anios < 2 or fila.localidades < 2:
                break
            ultimo_admisible = crop
        if ultimo_admisible < 2:
            elegibilidad.append({"CLONE": clon, "ELEGIBLE": False, "MAX_CROP_ADMISIBLE": ultimo_admisible,
                                 "MOTIVO": "No alcanza dos años y dos localidades en CROP 0, 1 y 2 consecutivos."})
            continue
        elegibilidad.append({"CLONE": clon, "ELEGIBLE": True, "MAX_CROP_ADMISIBLE": ultimo_admisible, "MOTIVO": "Cumple cobertura consecutiva."})
        for ultimo in range(ultimo_admisible + 1):
            tramo = cortes.loc[range(ultimo + 1)]
            n = ultimo + 1
            valor = (precio * tramo.T_SPACRE.sum() - 14 * tramo.TCA.sum() - 350 * n - 1100) / n
            politicas.append({"CLONE": clon, "PRECIO_USD_LB": precio, "ULTIMO_CROP": ultimo,
                              "COSECHAS_TOTALES": n, "APORTE_ANUAL_USD_ACRE": valor,
                              "MAX_CROP_ADMISIBLE": ultimo_admisible})
    todas = pd.DataFrame(politicas)
    if not todas.empty:
        mejores = (todas.sort_values(["CLONE", "APORTE_ANUAL_USD_ACRE", "ULTIMO_CROP"],
                                     ascending=[True, False, True])
                   .drop_duplicates("CLONE").reset_index(drop=True))
    else:
        mejores = pd.DataFrame(columns=["CLONE", "PRECIO_USD_LB", "ULTIMO_CROP", "COSECHAS_TOTALES", "APORTE_ANUAL_USD_ACRE", "MAX_CROP_ADMISIBLE"])
    return mejores, pd.DataFrame(elegibilidad)


def _preparar_series(celdas: pd.DataFrame, ajustado: bool, anios: np.ndarray) -> tuple[dict, dict]:
    """Precalcula aportes por año para remuestrear sin reagrupar filas."""
    posiciones = {int(anio): i for i, anio in enumerate(anios)}
    series: dict[tuple[str, int], dict] = {}
    for (clon, crop), grupo in celdas.groupby(["CLONE", "CROP"], sort=False):
        valor_a = "AZUCAR_DIF" if ajustado else "T_SPACRE"
        valor_c = "CANA_DIF" if ajustado else "TCA"
        por_anio = grupo.groupby("YEAR").agg(
            suma_a=(valor_a, "sum"), suma_c=(valor_c, "sum"), n=(valor_a, "size")
        )
        suma_a = np.zeros(len(anios)); suma_c = np.zeros(len(anios)); n = np.zeros(len(anios))
        for anio, fila in por_anio.iterrows():
            j = posiciones[int(anio)]
            suma_a[j], suma_c[j], n[j] = fila.suma_a, fila.suma_c, fila.n
        locs = {posiciones[int(anio)]: set(gg.LOC.astype(str)) for anio, gg in grupo.groupby("YEAR")}
        series[(str(clon), int(crop))] = {"a": suma_a, "c": suma_c, "n": n, "locs": locs}
    refs: dict[int, tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
    if ajustado:
        ref = celdas.loc[celdas.CLONE.eq(REFERENCIA)]
        for crop, grupo in ref.groupby("CROP"):
            por_anio = grupo.groupby("YEAR").agg(
                suma_a=("AZUCAR_REF", "sum"), suma_c=("CANA_REF", "sum"), n=("AZUCAR_REF", "size")
            )
            a = np.zeros(len(anios)); c = np.zeros(len(anios)); n = np.zeros(len(anios))
            for anio, fila in por_anio.iterrows():
                j = posiciones[int(anio)]
                a[j], c[j], n[j] = fila.suma_a, fila.suma_c, fila.n
            refs[int(crop)] = (a, c, n)
    return series, refs


def _resumen_replica(series: dict, refs: dict, pesos: np.ndarray, ajustado: bool, universo: list[str]) -> pd.DataFrame:
    """Recalcula medias y cobertura; YEAR repetido pesa, pero cuenta una vez como año."""
    filas = []
    for (clon, crop), s in series.items():
        pesos_celdas = pesos * s["n"]
        n = pesos_celdas.sum()
        if n <= 0:
            continue
        anios_con_dato = int(np.count_nonzero((pesos > 0) & (s["n"] > 0)))
        localidades = set().union(*(s["locs"].get(int(i), set()) for i in np.flatnonzero((pesos > 0) & (s["n"] > 0))))
        a = float(np.dot(pesos, s["a"]) / n)
        c = float(np.dot(pesos, s["c"]) / n)
        if ajustado and crop in refs:
            ra, rc, rn = refs[crop]
            nr = float(np.dot(pesos, rn))
            if nr <= 0:
                continue
            a += float(np.dot(pesos, ra) / nr)
            c += float(np.dot(pesos, rc) / nr)
        filas.append({"CLONE": clon, "CROP": crop, "T_SPACRE": a, "TCA": c,
                      "ambientes": int(n), "anios": anios_con_dato, "localidades": len(localidades)})
    return pd.DataFrame(filas)


def ejecutar() -> dict[str, pd.DataFrame | dict]:
    """Reconcilia escenario base y guarda réplicas, auditoría y resúmenes."""
    SALIDA.mkdir(parents=True, exist_ok=True)
    datos = pd.read_csv(ENTRADA, low_memory=False)
    etapa5 = datos.loc[datos.STAGE.eq(5)].copy()
    completos = etapa5.loc[etapa5[["T_SPACRE", "TCA"]].notna().all(axis=1)].copy()
    excluidas = completos.loc[completos.REQUIERE_REVISION.astype(bool)].copy()
    principal = completos.loc[~completos.index.isin(excluidas.index)].copy()
    fuera_etapa = datos.loc[~datos.STAGE.eq(5)].copy()
    fuera_etapa["MOTIVO_EXCLUSION"] = "Fuera de STAGE=5: análisis económico de notebook 03 delimita outfield."
    faltantes = etapa5.loc[etapa5[["T_SPACRE", "TCA"]].isna().any(axis=1)].copy()
    faltantes["MOTIVO_EXCLUSION"] = "Falta T_SPACRE o TCA; no puede calcularse aporte económico."
    excluidas["MOTIVO_EXCLUSION"] = "Alerta de calidad REQUIERE_REVISION; se conserva en sensibilidad marcada."
    filas_fuera = pd.concat([fuera_etapa, faltantes, excluidas], ignore_index=True)
    filas_fuera.to_csv(SALIDA / "filas_fuera_analisis.csv", index=False)
    # Alias descriptivo para facilitar auditoría de todas las exclusiones del escenario.
    exclusiones = filas_fuera
    exclusiones.to_csv(SALIDA / "filas_excluidas.csv", index=False)
    principal.to_csv(SALIDA / "filas_incluidas.csv", index=False)

    escenarios = {
        "ajustado": (preparar_celdas(principal, True), PRECIOS),
        "sin_ajuste": (preparar_celdas(principal, False), (0.20,)),
        "marcadas_incluidas": (preparar_celdas(completos, True), (0.20,)),
    }
    universo = sorted(etapa5.CLONE.dropna().astype(str).unique().tolist())
    llaves_ambiente = principal.groupby(["CLONE", "CROP", "YEAR", "LOC"], as_index=False)[["T_SPACRE", "TCA"]].mean()
    llave_ref = llaves_ambiente.loc[llaves_ambiente.CLONE.eq(REFERENCIA), ["CROP", "YEAR", "LOC"]]
    cobertura_ref = llaves_ambiente.merge(llave_ref, on=["CROP", "YEAR", "LOC"], how="left", indicator=True)
    cobertura_ref = cobertura_ref.loc[cobertura_ref._merge.eq("left_only")].drop(columns="_merge")
    cobertura_ref["MOTIVO_EXCLUSION"] = "No existe L01-299 en el mismo CROP, YEAR y LOC; no entra al contraste ajustado."
    cobertura_ref.to_csv(SALIDA / "ambientes_sin_referencia.csv", index=False)
    # Reconstrucción determinista del procedimiento vigente, comparada antes de bootstrap.
    _, base_elegibilidad, base_resumen = evaluar_base(principal, 0.20, True)
    vigente = pd.read_csv(RAIZ / "data" / "processed" / "serie1_politicas_renovacion.csv")
    vigente20 = vigente.loc[vigente.PRECIO_USD_LB.eq(0.20)].sort_values(["CLONE", "ULTIMO_CROP"]).reset_index(drop=True)
    # Reconstruye todas las duraciones para comparar la tabla fuente, no solo el óptimo.
    from_notebook = vigente20[["CLONE", "ULTIMO_CROP", "APORTE_ANUAL_USD_ACRE"]]
    all_policy = []
    for clon, grp in base_resumen.groupby("CLONE"):
        elig = base_elegibilidad.loc[base_elegibilidad.CLONE.eq(clon), "ELEGIBLE"].iloc[0]
        if not elig:
            continue
        cs = grp.set_index("CROP")
        max_crop = int(base_elegibilidad.loc[base_elegibilidad.CLONE.eq(clon), "MAX_CROP_ADMISIBLE"].iloc[0])
        for ultimo in range(max_crop + 1):
            tr = cs.loc[range(ultimo + 1)]
            n = ultimo + 1
            all_policy.append({"CLONE": clon, "ULTIMO_CROP": ultimo,
                               "APORTE_ANUAL_USD_ACRE": (0.20*tr.T_SPACRE.sum()-14*tr.TCA.sum()-350*n-1100)/n})
    reconciliacion = pd.DataFrame(all_policy).sort_values(["CLONE", "ULTIMO_CROP"]).reset_index(drop=True)
    comparacion = reconciliacion.merge(from_notebook, on=["CLONE", "ULTIMO_CROP"], suffixes=("_nuevo", "_notebook"), validate="one_to_one")
    if len(comparacion) != len(from_notebook) or not np.allclose(comparacion.APORTE_ANUAL_USD_ACRE_nuevo, comparacion.APORTE_ANUAL_USD_ACRE_notebook, rtol=0, atol=1e-8):
        raise AssertionError("La reconstrucción base no coincide con las políticas del notebook 03.")
    reconciliacion.to_csv(SALIDA / "politicas_base_reconstruidas.csv", index=False)

    anios = np.sort(principal.YEAR.unique())
    rng = np.random.default_rng(SEMILLA)
    draws = rng.choice(anios, size=(REPLICAS, len(anios)), replace=True)
    matrices = {
        nombre: _preparar_series(celdas, nombre != "sin_ajuste", anios)
        for nombre, (celdas, _) in escenarios.items()
    }
    pd.DataFrame(draws, columns=[f"sorteo_{i+1:02d}" for i in range(len(anios))]).assign(REPLICA=np.arange(1, REPLICAS+1)).to_csv(SALIDA / "anios_remuestreados.csv", index=False)
    filas = []
    elegibilidad_filas = []
    for rep, anios_rep in enumerate(draws, start=1):
        for nombre, (celdas, precios_escenario) in escenarios.items():
            ajustado = nombre != "sin_ajuste"
            pesos = np.bincount(np.searchsorted(anios, anios_rep), minlength=len(anios))
            resumen_rep = _resumen_replica(*matrices[nombre], pesos, ajustado, universo)
            for precio in precios_escenario:
                mejor, eleg = _politicas_desde_resumen(resumen_rep, precio, universo)
                eleg = eleg.assign(ESCENARIO=nombre, PRECIO_USD_LB=precio, REPLICA=rep)
                elegibilidad_filas.extend(eleg.to_dict("records"))
                if not mejor.empty:
                    mejor = mejor.sort_values("APORTE_ANUAL_USD_ACRE", ascending=False).reset_index(drop=True)
                    mejor["RANGO"] = np.arange(1, len(mejor)+1)
                    mejor["EN_TOP3"] = mejor.RANGO.le(3)
                    mejor["ESCENARIO"] = nombre
                    mejor["REPLICA"] = rep
                    filas.extend(mejor.to_dict("records"))
    replicados = pd.DataFrame(filas)
    eleg_replicas = pd.DataFrame(elegibilidad_filas)
    replicados.to_csv(SALIDA / "ranking_replicas.csv", index=False)
    eleg_replicas.to_csv(SALIDA / "elegibilidad_replicas.csv", index=False)

    columnas_resumen_ranking = ["ESCENARIO", "PRECIO_USD_LB", "CLONE", "replicas_con_ranking",
                                "top3_replicas", "rango_p05", "rango_mediano", "rango_p95",
                                "aporte_p05", "aporte_mediano", "aporte_p95", "politica_moda",
                                "frecuencia_politica_moda"]
    if replicados.empty:
        resumen_ranking = pd.DataFrame(columns=columnas_resumen_ranking)
    else:
        resumen_ranking = (replicados.groupby(["ESCENARIO", "PRECIO_USD_LB", "CLONE"], as_index=False)
               .agg(replicas_con_ranking=("REPLICA", "nunique"),
                    top3_replicas=("EN_TOP3", "sum"),
                    rango_p05=("RANGO", lambda s: s.quantile(.05)),
                    rango_mediano=("RANGO", "median"), rango_p95=("RANGO", lambda s: s.quantile(.95)),
                    aporte_p05=("APORTE_ANUAL_USD_ACRE", lambda s: s.quantile(.05)),
                    aporte_mediano=("APORTE_ANUAL_USD_ACRE", "median"),
                    aporte_p95=("APORTE_ANUAL_USD_ACRE", lambda s: s.quantile(.95)),
                    politica_moda=("COSECHAS_TOTALES", lambda s: int(s.mode().iloc[0])),
                    frecuencia_politica_moda=("COSECHAS_TOTALES", lambda s: float(s.value_counts(normalize=True).max()))))
    eleg_rep_count = eleg_replicas.groupby(["ESCENARIO", "PRECIO_USD_LB", "REPLICA"]).ELEGIBLE.sum().groupby(["ESCENARIO", "PRECIO_USD_LB"]).agg(replicas_total="size", replicas_con_menos_de_tres=lambda s: int((s < 3).sum())).reset_index()
    resumen_eleg = (eleg_replicas.groupby(["ESCENARIO", "PRECIO_USD_LB", "CLONE"], as_index=False)
                    .agg(replicas_elegible=("ELEGIBLE", "sum"), replicas_con_elegibilidad_observada=("REPLICA", "nunique")))
    resumen = resumen_eleg.merge(resumen_ranking, on=["ESCENARIO", "PRECIO_USD_LB", "CLONE"], how="left")
    resumen = resumen.merge(eleg_rep_count, on=["ESCENARIO", "PRECIO_USD_LB"], how="left")
    resumen["replicas_con_ranking"] = resumen.replicas_con_ranking.fillna(0).astype(int)
    resumen["top3_replicas"] = resumen.top3_replicas.fillna(0).astype(int)
    resumen["frecuencia_top3_condicional"] = resumen.top3_replicas.div(resumen.replicas_elegible.where(resumen.replicas_elegible.gt(0)))
    resumen["frecuencia_top3_sobre_todas_replicas"] = resumen.top3_replicas / resumen.replicas_total
    resumen.to_csv(SALIDA / "resumen_ranking.csv", index=False)
    conteos = {
        "filas_etapa5": int(len(etapa5)), "filas_completas": int(len(completos)),
        "filas_incluidas_escenario_principal": int(len(principal)),
        "filas_fuera_stage5": int(len(fuera_etapa)),
        "filas_excluidas_por_faltantes": int(len(faltantes)),
        "filas_excluidas_por_revision": int(len(excluidas)),
        "filas_marcadas_solo_revision_en_completos": int(completos.REQUIERE_REVISION.astype(bool).sum()),
        "anios": anios.astype(int).tolist(), "replicas": REPLICAS, "semilla": SEMILLA,
        "clones_universo_stage5": int(len(universo)),
        "ambientes_sin_referencia": int(len(cobertura_ref)),
    }
    (SALIDA / "conteos.json").write_text(json.dumps(conteos, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"base": reconciliacion, "replicas": replicados, "elegibilidad": eleg_replicas, "resumen": resumen, "conteos": conteos}


if __name__ == "__main__":
    resultado = ejecutar()
    print(json.dumps(resultado["conteos"], indent=2, ensure_ascii=False))
    print(resultado["resumen"].query("ESCENARIO == 'ajustado' and PRECIO_USD_LB == 0.20 and CLONE in ['HOCP14-885','L01-299','HO12-615','L01-283']").to_string(index=False))
