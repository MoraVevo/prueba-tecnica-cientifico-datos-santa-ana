"""Contraste descriptivo de aire/O2/gases a carga semejante para Serie II.5."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


COL = {
    "date": "date",
    "air": "FT_8302.AV_0#",
    "steam": "ZZQBCHLL.AV_0#",
    "pressure": "PTCA_8324.AV_0#",
    "o2_a": "AIR_8301A.AV_0#",
    "o2_b": "AIR_8301B.AV_0#",
    "gas_a": "TE_8319A.AV_0#",
    "gas_b": "TE_8319B.AV_0#",
    "return_a": "FT_8306A.AV_0#",
    "return_b": "FT_8306B.AV_0#",
}
NECESARIAS = [COL[k] for k in ("air", "steam", "pressure", "o2_a", "o2_b", "gas_a", "gas_b", "return_a", "return_b")]


def cargar_crudo(ruta: str | Path) -> pd.DataFrame:
    """Lee el CSV original sin modificarlo y comprueba su rejilla temporal."""
    datos = pd.read_csv(ruta, parse_dates=[COL["date"]])
    if len(datos) != 86_400:
        raise ValueError(f"Se esperaban 86,400 filas originales; llegaron {len(datos):,}.")
    if datos[COL["date"]].isna().any() or not datos[COL["date"]].is_unique:
        raise ValueError("Las fechas deben estar presentes y ser únicas.")
    if not datos[COL["date"]].is_monotonic_increasing:
        raise ValueError("Las filas deben estar ordenadas por fecha.")
    if not datos[COL["date"]].diff().dropna().eq(pd.Timedelta(seconds=5)).all():
        raise ValueError("La cadencia no es exactamente de cinco segundos.")
    faltan = sorted(set([COL["date"], *NECESARIAS]) - set(datos.columns))
    if faltan:
        raise ValueError(f"Faltan columnas requeridas: {faltan}")
    return datos


def agregar_bloques(datos: pd.DataFrame, cobertura_minima: int = 55) -> pd.DataFrame:
    """Resume bloques calendario de 5 min, reteniendo cobertura y rangos."""
    if cobertura_minima < 1 or cobertura_minima > 60:
        raise ValueError("La cobertura mínima debe estar entre 1 y 60.")
    fechas = datos[COL["date"]]
    bloque = ((fechas - fechas.iloc[0]) // pd.Timedelta(minutes=5)).astype(int)
    registros = []
    for bid, pos in datos.groupby(bloque, sort=True).indices.items():
        grupo = datos.iloc[pos]
        fila = {"bloque_id": int(bid), "inicio": grupo[COL["date"]].iloc[0],
                "fin": grupo[COL["date"]].iloc[-1], "dia": grupo[COL["date"]].iloc[0].date().isoformat(),
                "filas_fuente": len(grupo)}
        for c in NECESARIAS:
            s = grupo[c]
            fila[f"n__{c}"] = int(s.notna().sum())
            fila[c] = s.median()
            if c in (COL["steam"], COL["pressure"]):
                fila[f"rango__{c}"] = s.max() - s.min() if s.notna().any() else np.nan
        registros.append(fila)
    bloques = pd.DataFrame(registros)
    bloques["cobertura_ok"] = bloques[[f"n__{c}" for c in NECESARIAS]].ge(cobertura_minima).all(axis=1)
    return bloques


def preparar_contraste(bloques: pd.DataFrame, estabilidad: float = 1.0,
                       caliper_variable: float = 0.20, caliper_total: float = 0.30):
    """Clasifica población, terciles diarios y pares de carga sin reemplazo."""
    b = bloques.copy().reset_index(drop=True)
    b["estable"] = (b[f"rango__{COL['steam']}"] <= estabilidad) & (b[f"rango__{COL['pressure']}"] <= estabilidad)
    b["elegible"] = b.cobertura_ok & b.estable
    b["grupo_aire"] = "fuera_de_ambito"
    b["soporte"] = False
    b.loc[~b.cobertura_ok, "motivo"] = "cobertura_inferior_a_55_de_60"
    b.loc[b.cobertura_ok & ~b.estable, "motivo"] = "inestable_en_vapor_o_presion"
    b.loc[b.elegible, "motivo"] = "elegible_sin_pareja_aun"
    for dia, ix in b.loc[b.elegible].groupby("dia").groups.items():
        vals = b.loc[ix, COL["air"]]
        if len(vals) < 6:
            b.loc[ix, "motivo"] = "dia_con_menos_de_6_bloques_elegibles"
            continue
        q1, q2 = vals.quantile([1 / 3, 2 / 3]).to_numpy()
        b.loc[ix[vals <= q1], "grupo_aire"] = "bajo"
        b.loc[ix[vals >= q2], "grupo_aire"] = "alto"
        b.loc[ix[vals.gt(q1) & vals.lt(q2)], "grupo_aire"] = "tercil_medio"
        b.loc[ix[b.loc[ix, "grupo_aire"].eq("tercil_medio")], "motivo"] = "tercil_medio_no_en_contraste_primario"

    pares = []
    for dia, d in b.loc[b.grupo_aire.isin(["bajo", "alto"])].groupby("dia", sort=True):
        bajos = d.loc[d.grupo_aire.eq("bajo")].copy()
        altos = d.loc[d.grupo_aire.eq("alto")].copy()
        # La escala se estima con todos los bloques elegibles del día,
        # incluidos los del tercil medio, según el diseño previo.
        escala = b.loc[b.dia.eq(dia) & b.elegible, [COL["steam"], COL["pressure"]]].std(ddof=0).replace(0, np.nan)
        if escala.isna().any():
            continue
        x_hi = altos[[COL["steam"], COL["pressure"]]].to_numpy(float)
        x_lo = bajos[[COL["steam"], COL["pressure"]]].to_numpy(float)
        delta = (x_hi[:, None, :] - x_lo[None, :, :]) / escala.to_numpy(float)
        distancia = np.sqrt(np.square(delta).sum(axis=2))
        valido = (np.abs(delta) <= caliper_variable).all(axis=2) & (distancia <= caliper_total)
        cand = []
        for ai, bi in np.argwhere(valido):
            cand.append((float(distancia[ai, bi]), int(altos.iloc[ai].bloque_id),
                         int(bajos.iloc[bi].bloque_id), float(delta[ai, bi, 0]),
                         float(delta[ai, bi, 1])))
        usados_a, usados_b = set(), set()
        for dist, aid, bid, ds, dp in sorted(cand):
            if aid in usados_a or bid in usados_b:
                continue
            usados_a.add(aid); usados_b.add(bid)
            pares.append({"dia": dia, "bloque_alto": aid, "bloque_bajo": bid,
                          "distancia_carga_sd": dist, "dif_vapor_sd": ds, "dif_presion_sd": dp})
    p = pd.DataFrame(pares, columns=["dia", "bloque_alto", "bloque_bajo", "distancia_carga_sd", "dif_vapor_sd", "dif_presion_sd"])
    matched = set(p.bloque_alto.astype(int)) | set(p.bloque_bajo.astype(int)) if len(p) else set()
    b.loc[b.bloque_id.isin(matched), "motivo"] = "incluido_en_par_emparejado"
    b.loc[b.elegible & b.grupo_aire.isin(["bajo", "alto"]) & ~b.bloque_id.isin(matched), "motivo"] = "sin_pareja_dentro_de_caliper"
    b.loc[b.elegible & b.grupo_aire.isin(["bajo", "alto"]), "soporte"] = b.bloque_id.isin(matched)
    return b, p


def balance_carga(bloques: pd.DataFrame, pares: pd.DataFrame) -> pd.DataFrame:
    """Compara carga entre extremos antes y después del emparejamiento."""
    salida = []
    for dia, d in bloques.loc[bloques.grupo_aire.isin(["bajo", "alto"])].groupby("dia", sort=True):
        escala_base = bloques.loc[bloques.dia.eq(dia) & bloques.elegible]
        for nombre, mask in (("antes", d.index.to_series().isin(d.index)),):
            extremos = d.loc[mask]
            for variable in (COL["steam"], COL["pressure"]):
                escala = escala_base[variable].std(ddof=0)
                dif = extremos.loc[extremos.grupo_aire.eq("alto"), variable].mean() - extremos.loc[extremos.grupo_aire.eq("bajo"), variable].mean()
                salida.append({"dia": dia, "etapa": nombre, "variable": variable,
                               "diferencia_media_alto_menos_bajo": dif,
                               "diferencia_media_estandarizada": dif / escala if escala else np.nan})
        pdia = pares.loc[pares.dia.eq(dia)]
        if len(pdia):
            ix_alto, ix_bajo = pdia.bloque_alto.astype(int), pdia.bloque_bajo.astype(int)
            matched = bloques.set_index("bloque_id")
            for variable in (COL["steam"], COL["pressure"]):
                escala = escala_base[variable].std(ddof=0)
                dif = (matched.loc[ix_alto, variable].to_numpy() - matched.loc[ix_bajo, variable].to_numpy())
                salida.append({"dia": dia, "etapa": "despues", "variable": variable,
                               "diferencia_media_alto_menos_bajo": float(np.mean(dif)),
                               "diferencia_media_estandarizada": float(np.mean(dif) / escala) if escala else np.nan})
    return pd.DataFrame(salida, columns=["dia", "etapa", "variable", "diferencia_media_alto_menos_bajo", "diferencia_media_estandarizada"])


def resumir_pares(bloques: pd.DataFrame, pares: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Calcula contrastes alto menos bajo y contexto de asimetría/retorno."""
    resultados = [COL[k] for k in ("air", "o2_a", "o2_b", "gas_a", "gas_b", "return_a", "return_b")]
    filas = []
    lookup = bloques.set_index("bloque_id")
    for _, p in pares.iterrows():
        hi, lo = lookup.loc[int(p.bloque_alto)], lookup.loc[int(p.bloque_bajo)]
        fila = p.to_dict()
        for c in resultados:
            fila[f"dif__{c}"] = hi[c] - lo[c]
        fila["dif__asimetria_o2_a_menos_b"] = (hi[COL["o2_a"]] - hi[COL["o2_b"]]) - (lo[COL["o2_a"]] - lo[COL["o2_b"]])
        fila["dif__asimetria_gas_a_menos_b"] = (hi[COL["gas_a"]] - hi[COL["gas_b"]]) - (lo[COL["gas_a"]] - lo[COL["gas_b"]])
        filas.append(fila)
    campos_detalle = ["dia", "bloque_alto", "bloque_bajo", "distancia_carga_sd", "dif_vapor_sd", "dif_presion_sd"]
    campos_detalle += [f"dif__{c}" for c in resultados] + ["dif__asimetria_o2_a_menos_b", "dif__asimetria_gas_a_menos_b"]
    detalle = pd.DataFrame(filas, columns=campos_detalle)
    resumen = []
    if len(detalle):
        campos = [f"dif__{c}" for c in resultados] + ["dif__asimetria_o2_a_menos_b", "dif__asimetria_gas_a_menos_b"]
        for dia, d in detalle.groupby("dia", sort=True):
            for campo in campos:
                resumen.append({"dia": dia, "medida": campo, "n_pares": len(d),
                                "mediana_alto_menos_bajo": d[campo].median(),
                                "q1": d[campo].quantile(.25), "q3": d[campo].quantile(.75)})
        for campo in campos:
            resumen.append({"dia": "total_pares_no_independientes", "medida": campo, "n_pares": len(detalle),
                            "mediana_alto_menos_bajo": detalle[campo].median(),
                            "q1": detalle[campo].quantile(.25), "q3": detalle[campo].quantile(.75)})
    return detalle, pd.DataFrame(resumen, columns=["dia", "medida", "n_pares", "mediana_alto_menos_bajo", "q1", "q3"])


def auditar_filas(datos: pd.DataFrame, bloques: pd.DataFrame) -> pd.DataFrame:
    """Asigna cada fila original a un bloque y el papel/motivo de este."""
    n_por_bloque = bloques.set_index("bloque_id")
    bid = ((datos[COL["date"]] - datos[COL["date"]].iloc[0]) // pd.Timedelta(minutes=5)).astype(int)
    auditoria = pd.DataFrame({"fila_fuente_1based": np.arange(1, len(datos) + 1), "date": datos[COL["date"]], "bloque_id": bid})
    auditoria["grupo_aire"] = auditoria.bloque_id.map(n_por_bloque.grupo_aire)
    auditoria["motivo"] = auditoria.bloque_id.map(n_por_bloque.motivo)
    auditoria["incluida_contraste"] = auditoria["motivo"].eq("incluido_en_par_emparejado")
    if len(auditoria) != len(datos) or auditoria.bloque_id.isna().any():
        raise AssertionError("La auditoría debe cubrir cada fila fuente una sola vez.")
    return auditoria


def ejecutar(ruta: str | Path, salida: str | Path, estabilidad: float = 1.0,
             caliper_variable: float = 0.20, caliper_total: float = 0.30,
             *, datos: pd.DataFrame | None = None,
             bloques_crudos: pd.DataFrame | None = None) -> dict:
    datos = cargar_crudo(ruta) if datos is None else datos
    bloques = agregar_bloques(datos) if bloques_crudos is None else bloques_crudos
    clasificados, pares = preparar_contraste(bloques, estabilidad, caliper_variable, caliper_total)
    detalle, resumen = resumir_pares(clasificados, pares)
    balance = balance_carga(clasificados, pares)
    auditoria = auditar_filas(datos, clasificados)
    out = Path(salida); out.mkdir(parents=True, exist_ok=True)
    clasificados.to_csv(out / "auditoria_bloques.csv", index=False)
    auditoria.to_csv(out / "auditoria_filas.csv", index=False)
    clasificados.loc[~clasificados["soporte"].fillna(False)].to_csv(out / "bloques_fuera_soporte.csv", index=False)
    fuera = auditoria.loc[~auditoria.incluida_contraste].reset_index(drop=True)
    crudo_fuera = datos.loc[~auditoria.incluida_contraste.to_numpy()].drop(columns=COL["date"]).reset_index(drop=True)
    pd.concat([fuera, crudo_fuera], axis=1).to_csv(out / "filas_fuera_contraste.csv", index=False)
    pares.to_csv(out / "pares_carga.csv", index=False)
    detalle.to_csv(out / "diferencias_pareadas.csv", index=False)
    resumen.to_csv(out / "resumen_diferencias.csv", index=False)
    balance.to_csv(out / "balance_carga.csv", index=False)
    dia = clasificados.groupby("dia").agg(bloques=("bloque_id", "size"), elegibles=("elegible", "sum"),
        soporte=("soporte", "sum"), tercil_bajo=("grupo_aire", lambda x: int(x.eq("bajo").sum())),
        tercil_alto=("grupo_aire", lambda x: int(x.eq("alto").sum()))).reset_index()
    dia["pares"] = dia.dia.map(pares.groupby("dia").size()).fillna(0).astype(int) if len(pares) else 0
    dia.to_csv(out / "soporte_por_dia.csv", index=False)
    conteos = {"filas_crudas": len(datos), "bloques": len(clasificados),
               "filas_en_bloques_emparejados": int(auditoria.incluida_contraste.sum()),
               "filas_fuera_contraste": int((~auditoria.incluida_contraste).sum()),
               "pares": len(pares), "estabilidad_rango_unidades_originales": estabilidad,
               "caliper_por_variable_sd": caliper_variable, "caliper_euclideo_sd": caliper_total}
    (out / "conteos.json").write_text(json.dumps(conteos, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"bloques": clasificados, "pares": pares, "detalle": detalle, "resumen": resumen,
            "balance": balance,
            "auditoria": auditoria, "por_dia": dia, "conteos": conteos}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, default=Path("data/raw/serie2/data.csv"))
    parser.add_argument("--salida", type=Path, default=Path("outputs/serie2_carga"))
    parser.add_argument("--estabilidad", type=float, default=1.0, help="Rango intrabloque máximo en vapor y presión, unidades originales.")
    parser.add_argument("--caliper-variable", type=float, default=.20, help="Máxima diferencia estandarizada por variable de carga.")
    parser.add_argument("--caliper-total", type=float, default=.30, help="Máxima distancia estandarizada conjunta de carga.")
    args = parser.parse_args()
    resultado = ejecutar(args.entrada, args.salida, args.estabilidad, args.caliper_variable, args.caliper_total)
    print(json.dumps(resultado["conteos"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
