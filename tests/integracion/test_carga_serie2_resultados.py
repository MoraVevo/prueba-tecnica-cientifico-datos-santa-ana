import numpy as np
import pandas as pd

from scripts.comparar_carga_serie2 import COL, ejecutar


def test_resultados_y_trazabilidad_se_reproducen_desde_csv_original(tmp_path):
    crudo = pd.read_csv("data/raw/serie2/data.csv", parse_dates=["date"])
    r = ejecutar("data/raw/serie2/data.csv", tmp_path, estabilidad=2.0,
                 caliper_variable=.25, caliper_total=.30)

    assert len(crudo) == r["conteos"]["filas_crudas"] == 86_400
    assert len(r["bloques"]) == 1_440
    assert len(r["auditoria"]) == 86_400
    assert r["auditoria"].fila_fuente_1based.tolist() == list(range(1, 86_401))
    assert int(r["auditoria"].incluida_contraste.sum()) == r["conteos"]["filas_en_bloques_emparejados"]
    assert len(r["pares"]) > 0
    assert r["pares"].bloque_alto.is_unique and r["pares"].bloque_bajo.is_unique

    # Recalcula la mediana y la diferencia para un par desde las filas fuente.
    p = r["pares"].iloc[0]
    def mediana_bloque(bid, variable):
        lo, hi = int(bid) * 60, (int(bid) + 1) * 60
        return crudo.iloc[lo:hi][variable].median()
    esperado = mediana_bloque(p.bloque_alto, COL["o2_a"]) - mediana_bloque(p.bloque_bajo, COL["o2_a"])
    observado = r["detalle"].iloc[0][f"dif__{COL['o2_a']}"]
    assert np.isclose(observado, esperado)

    # Recalcula todos los calipers usando la desviación estándar de todos los
    # bloques elegibles del día, incluidos los del tercil medio.
    lookup = r["bloques"].set_index("bloque_id")
    for pair in r["pares"].itertuples(index=False):
        dia = lookup.loc[pair.bloque_alto, "dia"]
        eligibles = r["bloques"].loc[(r["bloques"].dia == dia) & r["bloques"].elegible]
        scales = eligibles[[COL["steam"], COL["pressure"]]].std(ddof=0)
        diffs = (lookup.loc[pair.bloque_alto, [COL["steam"], COL["pressure"]]].to_numpy(float)
                 - lookup.loc[pair.bloque_bajo, [COL["steam"], COL["pressure"]]].to_numpy(float)) / scales.to_numpy(float)
        assert np.abs(diffs).max() <= .25 + 1e-12
        assert np.sqrt(np.square(diffs).sum()) <= .30 + 1e-12

    balance = r["balance"]
    despues = balance.loc[(balance.etapa == "despues") & (balance.variable == COL["steam"]), "diferencia_media_estandarizada"]
    assert len(despues) > 0 and despues.abs().max() <= .25
    fuera = pd.read_csv(tmp_path / "filas_fuera_contraste.csv")
    assert len(fuera) == 86_400 - r["conteos"]["filas_en_bloques_emparejados"]
    assert COL["o2_a"] in fuera.columns
    fila_fuera = int(fuera.iloc[0].fila_fuente_1based) - 1
    assert np.isclose(fuera.iloc[0][COL["o2_a"]], crudo.iloc[fila_fuera][COL["o2_a"]])
    assert (tmp_path / "auditoria_filas.csv").exists()
    assert (tmp_path / "filas_fuera_contraste.csv").exists()
    assert (tmp_path / "bloques_fuera_soporte.csv").exists()


def test_matriz_final_fija_soporte_y_pares_por_escenario():
    m = pd.read_csv("outputs/serie2_carga/matriz_sensibilidad.csv").set_index(
        ["rango_original", "caliper_sd_variable"]
    )
    assert len(m) == 9
    assert m.caliper_total_sd.eq(.30).all()
    assert (m.loc[.5, "pares"] == 0).all()
    assert m.loc[(1.0, .20), "bloques_elegibles"] == 65
    assert m.loc[(1.0, .20), "pares"] == 0
    assert m.loc[(2.0, .20), "bloques_elegibles"] == 1_016
    assert m.loc[(2.0, .20), "pares"] == 46
    assert m.loc[(2.0, .20), "bloques_pareados"] == 92
    assert m.loc[(2.0, .20), "filas_fuente_emparejadas"] == 5_520
    assert m.loc[(2.0, .25), "pares"] == 59
    assert m.loc[(2.0, .20), "max_abs_smd_vapor_despues"] < .10
    assert m.loc[(2.0, .20), "max_abs_smd_presion_despues"] < .10
