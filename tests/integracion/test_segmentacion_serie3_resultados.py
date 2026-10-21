"""Reconstruye rasgos, conservación, distancias y referencia sin helpers del modelo."""
import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import adjusted_rand_score


RAIZ = Path(__file__).resolve().parents[2]
OUT = RAIZ / "outputs/serie3_segmentacion"


def test_rasgos_y_exclusiones_reconstruidos_sin_imputacion():
    origen = RAIZ / "outputs/serie3_eda/revision/cana_paises.csv"
    decision = json.loads((OUT / "decision.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(origen.read_bytes()).hexdigest() == decision["fuente_sha256"]
    largo = pd.read_csv(origen)
    f = pd.read_csv(OUT / "paises_y_rasgos.csv").set_index("area")
    excluidas = pd.read_csv(OUT / "filas_fuera_segmentacion.csv")
    assert len(f) == 74 and len(excluidas) == 7182
    assert set(f.index).isdisjoint(excluidas.area.unique())
    assert len(largo[largo.area.isin(f.index)]) + len(excluidas) == len(largo) == 21168
    assert excluidas.motivo.notna().all()
    claves = ["area", "ano", "elemento"]
    original = largo[~largo.area.isin(f.index)].sort_values(claves).reset_index(drop=True)
    pd.testing.assert_frame_equal(original, excluidas[largo.columns].sort_values(claves).reset_index(drop=True))
    todo = largo.pivot(index=["area", "ano"], columns="elemento", values="valor")
    elegibles = []
    for area in largo.area.unique():
        g = todo.loc[area]
        valores = g[["Area harvested", "Yield", "Production"]].to_numpy()
        positivos = np.all(valores > 0, axis=1)
        ventanas = [(1961,1970),(1971,1980),(1981,1990),(1991,2000),(2001,2010),(2011,2023)]
        suficiente = all(np.sum(positivos & (g.index >= a) & (g.index <= b)) >= np.ceil(.6*(b-a+1)) for a,b in ventanas)
        suficiente &= np.sum(positivos & (g.index >= 2019)) >= 4
        if not suficiente:
            continue
        elegibles.append(area)
        g = g.loc[positivos]
        recientes = g.loc[2019:2023]
        for elemento, nombre in [("Area harvested", "area"),("Yield", "rendimiento")]:
            mediana = np.median(recientes[elemento])
            np.testing.assert_allclose(f.loc[area, f"log_{nombre}_reciente"], np.log(mediana))
            x = np.array([np.median(g.loc[a:b].index) for a,b in ventanas])
            y = np.log([np.median(g.loc[a:b, elemento]) for a,b in ventanas])
            pendiente = np.sum((x-x.mean())*(y-y.mean())) / np.sum((x-x.mean())**2)
            np.testing.assert_allclose(f.loc[area, f"tendencia_{nombre}_pct"], 100*np.expm1(pendiente), atol=1e-10)
            diferencias = np.diff(np.log(g[elemento]))[np.diff(g.index) == 1]
            mad = np.median(np.abs(diferencias-np.median(diferencias))) * 148.26
            np.testing.assert_allclose(f.loc[area, f"variabilidad_{nombre}_log"], mad, atol=1e-10)
    assert set(elegibles) == set(f.index)
    traza = pd.read_csv(OUT / "tripletas_fuera_rasgos.csv")
    assert not traza.tripleta_positiva.any() and traza.motivo_fuera_rasgos.notna().all()


def test_grupos_pares_y_benchmark_por_ecuaciones_independientes():
    f = pd.read_csv(OUT / "paises_y_rasgos.csv").set_index("area")
    decision = json.loads((OUT / "decision.json").read_text(encoding="utf-8"))
    archivo = joblib.load(OUT / "modelo_perfiles.joblib")
    a = f[decision["rasgos"]].values
    z = (a - a.mean(axis=0)) / a.std(axis=0)
    centros = archivo["modelo"].cluster_centers_
    asignados = ((z[:,None,:] - centros[None,:,:])**2).sum(axis=2).argmin(axis=1)
    assert adjusted_rand_score(asignados, f.grupo) == 1
    assert np.bincount(asignados).min() >= 5
    diag = pd.read_csv(OUT / "eleccion_k.csv")
    admisibles = diag[diag.menor_grupo >= 5]
    assert decision["k"] == admisibles[admisibles.silueta >= admisibles.silueta.max()-.02].k.min()
    a = f[decision["rasgos_pares"]].values
    z = (a - a.mean(axis=0)) / a.std(axis=0)
    gt = f.index.get_loc("Guatemala")
    distancias = np.sqrt(np.mean((z-z[gt])**2, axis=1))
    ratio = f.area_reciente_ha / f.loc["Guatemala", "area_reciente_ha"]
    candidatos = np.flatnonzero(ratio.between(.25,4).values & (np.arange(len(f)) != gt))
    elegidos = f.index[candidatos[np.argsort(distancias[candidatos])[:5]]].tolist()
    assert elegidos == decision["pares_GT"]
    largo = pd.read_csv(RAIZ / "outputs/serie3_eda/revision/cana_paises.csv")
    ref = pd.read_csv(OUT / "referencia_productividad.csv")
    for fila in ref.itertuples():
        valores = largo[largo.elemento.eq("Yield") & largo.ano.eq(fila.ano) & largo.area.isin(elegidos)]
        gt = largo[largo.area.eq("Guatemala") & largo.ano.eq(fila.ano) & largo.elemento.eq("Yield")].iloc[0]
        if fila.solo_oficial:
            valores = valores[valores.flag.eq("A")]
        y = valores.loc[valores.valor > 0, "valor"].values
        assert len(y) == fila.n_pares
        if len(y) < 3 or (fila.solo_oficial and gt.flag != "A"):
            assert np.isnan(fila.ratio_GT_mediana)
            continue
        np.testing.assert_allclose(fila.ratio_GT_mediana, gt.valor / np.median(y))
        np.testing.assert_allclose(fila.ratio_GT_p75, gt.valor / np.percentile(y,75))
    np.testing.assert_allclose(decision["ratio_GT_mediana_reciente"], ref.loc[~ref.solo_oficial, "ratio_GT_mediana"].median())
    oficiales = pd.read_csv(OUT / "elegibilidad_solo_A.csv").set_index("area")
    assert not oficiales.loc["Guatemala", "elegible"] and oficiales.loc["Guatemala", "n_recientes"] == 2
    assert not decision["recursos_naturales_observados"] and not decision["costos_observados"]
