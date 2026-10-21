"""Auditoría reproducible de la fuente de caña para el inciso 1 de Serie III."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ANTERIORES = {"Czechoslovakia", "Ethiopia PDR", "Serbia and Montenegro",
              "Sudan (former)", "USSR", "Yugoslav SFR"}


def auditar(raiz):
    raiz = Path(raiz)
    fuente = raiz / "data/raw/serie3"
    out = raiz / "outputs/serie3_eda/revision"
    out.mkdir(parents=True, exist_ok=True)
    rutas = [fuente / f for f in ["Production_Crops_Livestock_E_All_Data.csv",
                                  "Production_Crops_Livestock_E_All_Data_NOFLAG.csv",
                                  "Production_Crops_Livestock_E_AreaCodes.csv",
                                  "Production_Crops_Livestock_E_Flags.csv"]]
    huellas = {str(p.relative_to(raiz)): hashlib.sha256(p.read_bytes()).hexdigest() for p in rutas}
    raw = pd.read_csv(rutas[0], low_memory=False)
    sc = raw[raw.Item == "Sugar cane"].copy()
    sc.insert(0, "fila_fuente", sc.index)
    assert not sc.duplicated(["Area Code", "Element Code"]).any()
    areas = pd.read_csv(rutas[2])
    assert areas["Area Code"].is_unique
    assert sc["Area Code"].isin(areas["Area Code"]).all()
    unidades = sc.groupby("Element").Unit.unique().map(list).to_dict()
    assert unidades == {"Area harvested": ["ha"], "Production": ["t"], "Yield": ["kg/ha"]}
    anos = [c for c in sc if c.startswith("Y") and c[1:].isdigit()]
    assert set(f"Y{y}" for y in range(1961, 2024)).issubset(anos)
    sinflags = pd.read_csv(rutas[1], low_memory=False)
    sinflags = sinflags[sinflags.Item == "Sugar cane"].sort_values(["Area Code", "Element Code"])
    ordenado = sc.sort_values(["Area Code", "Element Code"])
    assert np.array_equal(ordenado[["Area Code", "Element Code"]].values,
                          sinflags[["Area Code", "Element Code"]].values)
    np.testing.assert_allclose(ordenado[anos], sinflags[anos], equal_nan=True)
    # El código ya existe en el crudo. Unir por nombre pierde variantes con ;/,
    # sin aportar identificación: se valida contra diccionario por código.
    partes = []
    for y in anos:
        t = sc[["fila_fuente", "Area Code", "Area", "Element", "Unit", y, y + "F", y + "N"]].copy()
        t.columns = ["fila_fuente", "codigo_area", "area", "elemento", "unidad", "valor", "flag", "nota"]
        t["ano"] = int(y[1:])
        partes.append(t)
    largo = pd.concat(partes, ignore_index=True)
    largo["motivo_fuera_ambito"] = ""
    largo.loc[largo.codigo_area >= 5000, "motivo_fuera_ambito"] = "agregado_regional_o_grupo"
    largo.loc[largo.area == "China", "motivo_fuera_ambito"] = "agregado_China_componentes_separados"
    largo.loc[largo.area.isin(ANTERIORES), "motivo_fuera_ambito"] = "entidad_historica_no_empalmada"
    fuera_periodo = ~largo.ano.between(1961, 2023)
    largo.loc[fuera_periodo, "motivo_fuera_ambito"] = (
        largo.loc[fuera_periodo, "motivo_fuera_ambito"] + ";ano_fuera_1961_2023").str.strip(";")
    largo["en_ambito_paises"] = largo.motivo_fuera_ambito.eq("")
    assert largo.flag.dropna().isin(["A", "E", "I", "X", "M"]).all()
    assert not largo.valor.lt(0).any()
    largo["revisar_flag"] = ((largo.valor.notna() & (largo.flag.isna() | largo.flag.eq("M"))) |
                             (largo.valor.isna() & largo.flag.isin(["A", "E", "I", "X"])))
    largo.to_csv(out / "cana_todas_celdas.csv", index=False)
    largo[~largo.en_ambito_paises].to_csv(out / "filas_fuera_ambito.csv", index=False)
    paises = largo[largo.en_ambito_paises].copy()
    paises.to_csv(out / "cana_paises.csv", index=False)
    cobertura = paises.groupby(["codigo_area", "area", "elemento"]).agg(
        n_anos=("valor", "count"), n_ceros=("valor", lambda a: a.eq(0).sum()),
        n_flags_no_oficiales=("flag", lambda a: a.isin(["E", "I", "X"]).sum()),
    ).reset_index()
    cobertura["baja_cobertura"] = cobertura.n_anos < 10
    cobertura.to_csv(out / "cobertura_paises.csv", index=False)
    cobertura[cobertura.baja_cobertura].to_csv(out / "paises_baja_cobertura.csv", index=False)
    # Denominador explícito: solo producción con valor observado. Desconocidas
    # y ausentes se contabilizan aparte; no convertir ausencias en cadenas.
    calidad = []
    for ano, g in paises[paises.elemento == "Production"].groupby("ano"):
        observadas = g[g.valor.notna()]
        calidad.append({"ano": ano, "n_areas": len(g), "n_observadas": len(observadas),
                        "n_ausentes": int(g.valor.isna().sum()),
                        "n_no_oficiales": int(observadas.flag.isin(["E", "I", "X"]).sum()),
                        "n_sin_flag": int(observadas.flag.isna().sum()),
                        "proporcion_no_oficial": observadas.flag.isin(["E", "I", "X"]).mean()})
    calidad = pd.DataFrame(calidad)
    calidad.to_csv(out / "calidad_por_ano.csv", index=False)
    flags = paises.assign(flag=lambda t: t.flag.fillna("sin_flag")).groupby(["elemento", "flag"]).size()
    flags.rename("celdas").to_csv(out / "flags_conteo.csv")
    # Producción (t) = área (ha) × rendimiento (kg/ha) / 1,000.
    coherencia = largo.pivot(index=["codigo_area", "area", "ano"], columns="elemento", values="valor").reset_index()
    coherencia["produccion_calculada"] = coherencia["Area harvested"] * coherencia.Yield / 1000
    coherencia["diferencia_t"] = coherencia.produccion_calculada - coherencia.Production
    coherencia["error_relativo"] = coherencia.diferencia_t.abs() / coherencia.Production.abs().replace(0, np.nan)
    coherencia["completa"] = coherencia[["Area harvested", "Yield", "Production"]].notna().all(axis=1)
    coherencia["en_periodo"] = coherencia.ano.between(1961, 2023)
    coherencia["en_ambito_paises"] = coherencia.area.isin(paises.area.unique()) & coherencia.en_periodo
    coherencia["revisar"] = coherencia.completa & (
        (coherencia.error_relativo > .01) |
        ((coherencia.Production == 0) & (coherencia.produccion_calculada != 0)))
    coherencia["motivo"] = np.where(coherencia.revisar, "discrepancia_mayor_1pct_o_cero_incoherente", "")
    # Diagnóstico de precisión: si el área se redondeó a ha enteras, una
    # diferencia de <=0.5 ha puede generar grandes errores relativos en áreas
    # pequeñas. Es compatibilidad numérica bajo supuesto, no error demostrado.
    coherencia["area_implicita_ha"] = coherencia.Production * 1000 / coherencia.Yield.replace(0, np.nan)
    coherencia["distancia_area_implicita_ha"] = (coherencia.area_implicita_ha - coherencia["Area harvested"]).abs()
    coherencia["compatible_redondeo_area_1ha"] = coherencia.distancia_area_implicita_ha <= .500001
    coherencia.to_csv(out / "coherencia_area_rendimiento_produccion.csv", index=False)
    coherencia[coherencia.revisar].to_csv(out / "revisar_coherencia.csv", index=False)
    # Balance mundial histórico: conservar predecesores en sus años; retirarlos
    # siempre subestima el pasado. Esta vista no concatena sus trayectorias.
    mundo = []
    produccion = largo[largo.elemento == "Production"]
    for ano, g in produccion.groupby("ano"):
        territorios = g[(g.codigo_area < 5000) & (g.area != "China")]
        total = territorios.valor.sum(min_count=1)
        referencia = g.loc[g.area == "World", "valor"].iloc[0]
        componentes = g[g.area.isin(["China, mainland", "China, Taiwan Province of",
                                     "China, Hong Kong SAR", "China, Macao SAR"])].valor.sum(min_count=1)
        china = g.loc[g.area == "China", "valor"].iloc[0]
        mundo.append({"ano": ano, "suma_territorios": total, "World": referencia,
                      "diferencia_t": total - referencia,
                      "diferencia_relativa": (total - referencia) / referencia,
                      "china_menos_componentes_t": china - componentes})
    pd.DataFrame(mundo).to_csv(out / "balance_mundial.csv", index=False)
    # Extremos descriptivos: marcas para revisión, conservadas sin exclusión.
    rendimiento = paises[paises.elemento == "Yield"]
    limite = rendimiento.valor.quantile(.99)
    extremos = rendimiento[rendimiento.valor >= limite].copy()
    extremos["motivo_revision"] = "percentil99_global_descriptivo_no_prueba_de_error"
    extremos.to_csv(out / "extremos_rendimiento.csv", index=False)
    resumen = {
        "filas_cana_ancha": len(sc), "areas_totales": sc.Area.nunique(),
        "anos_en_fuente": [int(a[1:]) for a in anos], "periodo_analisis": [1961, 2023],
        "celdas_totales": len(largo), "celdas_paises": len(paises),
        "celdas_fuera_ambito": int((~largo.en_ambito_paises).sum()),
        "areas_en_ambito": paises.area.nunique(), "unidades": unidades,
        "baja_cobertura_filas": int(cobertura.baja_cobertura.sum()),
        "baja_cobertura_areas": cobertura.loc[cobertura.baja_cobertura, "area"].nunique(),
        "celdas_sin_valor": int(largo.valor.isna().sum()),
        "celdas_cero": int(largo.valor.eq(0).sum()), "flags_revisar": int(largo.revisar_flag.sum()),
        "tripletas_revisar": int(coherencia.revisar.sum()),
        "tripletas_paises_revisar": int((coherencia.en_ambito_paises & coherencia.revisar).sum()),
        "marcas_paises_compatibles_redondeo_area": int((coherencia.en_ambito_paises & coherencia.revisar & coherencia.compatible_redondeo_area_1ha).sum()),
        "p99_rendimiento_kg_ha": float(limite), "extremos_marcados": len(extremos),
        "NOFLAG_coincide": True, "huellas_fuentes": huellas,
        "exclusiones_por_error": 0, "listo_segmentacion": "con decisiones de cobertura y sensibilidad; sin imputación automática",
    }
    for p, h in huellas.items():
        assert hashlib.sha256((raiz / p).read_bytes()).hexdigest() == h
    (out / "verificacion.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"resumen": resumen, "paises": paises, "cobertura": cobertura,
            "calidad": calidad, "coherencia": coherencia, "largo": largo}


if __name__ == "__main__":
    print(json.dumps(auditar(Path(__file__).resolve().parents[1])["resumen"], ensure_ascii=True, indent=2))
