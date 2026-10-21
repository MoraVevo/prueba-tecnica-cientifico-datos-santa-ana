"""Reconstruye rankings y política con filas expandidas por año, sin usar el helper del script."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest


RAIZ = Path(__file__).resolve().parents[2]
OUT = RAIZ / "outputs" / "serie1_ranking"


def reconstruir_replica_expandiendo_anios(replica: int) -> pd.DataFrame:
    etl = pd.read_csv(RAIZ / "data" / "processed" / "serie1_etl_provisional.csv", low_memory=False)
    datos = etl.loc[etl.STAGE.eq(5) & etl[["T_SPACRE", "TCA"]].notna().all(axis=1) & ~etl.REQUIERE_REVISION.astype(bool)].copy()
    sorteos = pd.read_csv(OUT / "anios_remuestreados.csv").set_index("REPLICA").loc[replica].to_numpy(dtype=int)
    # Expansión literal: una copia completa del conglomerado por cada sorteo.
    repetidas = pd.concat([
        datos.loc[datos.YEAR.eq(ano)].assign(DRAW=indice)
        for indice, ano in enumerate(sorteos)
    ], ignore_index=True)
    celdas = repetidas.groupby(["CLONE", "CROP", "YEAR", "LOC", "DRAW"], as_index=False)[["T_SPACRE", "TCA"]].mean()
    control = celdas.loc[celdas.CLONE.eq("L01-299"), ["CROP", "YEAR", "LOC", "DRAW", "T_SPACRE", "TCA"]]
    pares = celdas.merge(control, on=["CROP", "YEAR", "LOC", "DRAW"], suffixes=("", "_ref"), validate="many_to_one")
    pares["d_azucar"] = pares.T_SPACRE - pares.T_SPACRE_ref
    pares["d_cana"] = pares.TCA - pares.TCA_ref
    ref_crop = control.groupby("CROP")[["T_SPACRE", "TCA"]].mean()
    resultados = []
    for clon, grupo in pares.groupby("CLONE"):
        cortes = grupo.groupby("CROP").agg(
            anios=("YEAR", "nunique"), localidades=("LOC", "nunique"),
            da=("d_azucar", "mean"), dc=("d_cana", "mean"),
        )
        ultimo_admisible = -1
        for crop in range(4):
            if crop not in cortes.index or cortes.loc[crop, "anios"] < 2 or cortes.loc[crop, "localidades"] < 2:
                break
            ultimo_admisible = crop
        if ultimo_admisible < 2:
            continue
        for ultimo in range(ultimo_admisible + 1):
            tr = cortes.loc[range(ultimo + 1)]
            n = ultimo + 1
            azucar = tr.da.sum() + ref_crop.loc[range(ultimo + 1), "T_SPACRE"].sum()
            cana = tr.dc.sum() + ref_crop.loc[range(ultimo + 1), "TCA"].sum()
            aporte = (0.20 * azucar - 14 * cana - 350 * n - 1100) / n
            resultados.append((clon, ultimo, n, aporte))
    decisiones = pd.DataFrame(resultados, columns=["CLONE", "ULTIMO_CROP", "COSECHAS_TOTALES", "APORTE_ANUAL_USD_ACRE"])
    return (decisiones.sort_values(["CLONE", "APORTE_ANUAL_USD_ACRE", "ULTIMO_CROP"], ascending=[True, False, True])
            .drop_duplicates("CLONE").sort_values("APORTE_ANUAL_USD_ACRE", ascending=False).reset_index(drop=True))


def test_base_reconstruida_coincide_con_politicas_vigentes_y_unidades():
    actual = pd.read_csv(OUT / "politicas_base_reconstruidas.csv")
    vigente = pd.read_csv(RAIZ / "data" / "processed" / "serie1_politicas_renovacion.csv")
    vigente = vigente.loc[vigente.PRECIO_USD_LB.eq(0.20), ["CLONE", "ULTIMO_CROP", "APORTE_ANUAL_USD_ACRE"]]
    unido = actual.merge(vigente, on=["CLONE", "ULTIMO_CROP"], suffixes=("_nuevo", "_vigente"), validate="one_to_one")
    assert len(unido) == len(vigente)
    np.testing.assert_allclose(unido.APORTE_ANUAL_USD_ACRE_nuevo, unido.APORTE_ANUAL_USD_ACRE_vigente, rtol=0, atol=1e-8)
    etl = pd.read_csv(RAIZ / "data" / "processed" / "serie1_etl_provisional.csv", low_memory=False)
    completas = etl.loc[etl.T_SPACRE.gt(0) & etl.TCA.gt(0) & etl.TRS_TON.gt(0)]
    # TCA (ton/ac) × TRS_TON (lb/ton) reconstruye T_SPACRE en lb/ac.
    ratio = completas.T_SPACRE / (completas.TCA * completas.TRS_TON)
    assert ratio.median() == pytest.approx(1.0, abs=0.002)


def test_conserva_flags_exclusiones_y_ambientes_sin_referencia():
    etl = pd.read_csv(RAIZ / "data" / "processed" / "serie1_etl_provisional.csv", low_memory=False)
    incluidas = pd.read_csv(OUT / "filas_incluidas.csv", low_memory=False)
    excluidas = pd.read_csv(OUT / "filas_fuera_analisis.csv", low_memory=False)
    conteos = pd.read_json(OUT / "conteos.json", typ="series")
    assert len(incluidas) + len(excluidas) == len(etl)
    assert "REQUIERE_REVISION" in incluidas and "REQUIERE_REVISION" in excluidas
    assert not incluidas.REQUIERE_REVISION.astype(bool).any()
    assert set(excluidas.MOTIVO_EXCLUSION.dropna()).issuperset({
        "Fuera de STAGE=5: análisis económico de notebook 03 delimita outfield.",
        "Falta T_SPACRE o TCA; no puede calcularse aporte económico.",
        "Alerta de calidad REQUIERE_REVISION; se conserva en sensibilidad marcada.",
    })
    sin_ref = pd.read_csv(OUT / "ambientes_sin_referencia.csv")
    assert len(sin_ref) == conteos.ambientes_sin_referencia
    assert sin_ref.MOTIVO_EXCLUSION.str.contains("No existe L01-299").all()


def test_replicas_reconstruyen_rangos_aportes_y_denominadores_independientemente():
    ranking = pd.read_csv(OUT / "ranking_replicas.csv")
    eleg = pd.read_csv(OUT / "elegibilidad_replicas.csv")
    resumen = pd.read_csv(OUT / "resumen_ranking.csv")
    assert eleg.REPLICA.nunique() == int(pd.read_json(OUT / "conteos.json", typ="series").replicas)
    assert set(eleg.CLONE.unique()) == set(pd.read_csv(RAIZ / "data" / "processed" / "serie1_etl_provisional.csv", low_memory=False).query("STAGE == 5").CLONE.unique())
    elegibles = eleg.query("ESCENARIO == 'ajustado' and PRECIO_USD_LB == 0.2").groupby("REPLICA").ELEGIBLE.sum()
    assert (elegibles >= 3).all()
    for replica in [1, max(1, int(eleg.REPLICA.max()) // 2), int(eleg.REPLICA.max())]:
        if elegibles.loc[replica] < 3:
            continue
        independiente = reconstruir_replica_expandiendo_anios(replica)
        guardado = ranking.query("ESCENARIO == 'ajustado' and PRECIO_USD_LB == 0.2 and REPLICA == @replica").sort_values("RANGO").reset_index(drop=True)
        assert len(independiente) == len(guardado)
        assert independiente.CLONE.tolist() == guardado.CLONE.tolist()
        np.testing.assert_allclose(independiente.APORTE_ANUAL_USD_ACRE, guardado.APORTE_ANUAL_USD_ACRE, rtol=0, atol=1e-8)
        np.testing.assert_array_equal(independiente.COSECHAS_TOTALES, guardado.COSECHAS_TOTALES)
    principal = resumen.query("ESCENARIO == 'ajustado' and PRECIO_USD_LB == 0.2")
    assert len(principal) == 40
    assert principal.replicas_total.eq(eleg.REPLICA.nunique()).all()
    assert principal.frecuencia_top3_sobre_todas_replicas.between(0, 1).all()


def test_hocp09_es_alternativa_estable_condicionada_a_cobertura_de_hocp14():
    eleg = pd.read_csv(OUT / "elegibilidad_replicas.csv").query("ESCENARIO == 'ajustado' and PRECIO_USD_LB == 0.2")
    ranking = pd.read_csv(OUT / "ranking_replicas.csv").query("ESCENARIO == 'ajustado' and PRECIO_USD_LB == 0.2")
    por_replica = eleg.pivot(index="REPLICA", columns="CLONE", values="ELEGIBLE")
    h09 = ranking.loc[ranking.CLONE.eq("HOCP09-804"), ["REPLICA", "RANGO", "APORTE_ANUAL_USD_ACRE"]].set_index("REPLICA")
    unido = por_replica[["HOCP14-885", "HOCP09-804"]].join(h09)
    no_h14 = unido.loc[~unido["HOCP14-885"]]
    si_h14 = unido.loc[unido["HOCP14-885"]]
    assert int(por_replica["HOCP09-804"].sum()) == 499
    assert int(no_h14["HOCP09-804"].sum()) == 297
    assert int((no_h14.RANGO.le(3)).sum()) == 264
    assert int(si_h14["HOCP09-804"].sum()) == 202
    assert int((si_h14.RANGO.le(3)).sum()) == 7
    assert no_h14.RANGO.median() == 3
    assert si_h14.RANGO.median() == 4
    assert h09.APORTE_ANUAL_USD_ACRE.median() == pytest.approx(598.633081, abs=1e-5)

