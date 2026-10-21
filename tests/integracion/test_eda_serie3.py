"""Contrastes independientes del EDA: crudo, ámbito, denominadores y unidades."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


RAIZ = Path(__file__).resolve().parents[2]
OUT = RAIZ / "outputs/serie3_eda/revision"


def test_eda_conserva_todas_las_celdas_y_aplica_ambito_1961_2023():
    r = json.loads((OUT / "verificacion.json").read_text(encoding="utf-8"))
    for ruta, huella in r["huellas_fuentes"].items():
        assert hashlib.sha256((RAIZ / ruta).read_bytes()).hexdigest() == huella
    raw = pd.read_csv(RAIZ / "data/raw/serie3/Production_Crops_Livestock_E_All_Data.csv", low_memory=False)
    sc = raw[raw.Item == "Sugar cane"]
    tipos = {"motivo_fuera_ambito": "string"}
    todas = pd.read_csv(OUT / "cana_todas_celdas.csv", dtype=tipos)
    paises = pd.read_csv(OUT / "cana_paises.csv", dtype=tipos)
    fuera = pd.read_csv(OUT / "filas_fuera_ambito.csv", dtype=tipos)
    assert len(todas) == len(paises) + len(fuera) == 27648
    assert not todas.duplicated(["fila_fuente", "ano"]).any()
    assert fuera.motivo_fuera_ambito.notna().all()
    pd.testing.assert_frame_equal(pd.concat([paises, fuera]).sort_values(["fila_fuente", "ano"]).reset_index(drop=True),
                                  todas.sort_values(["fila_fuente", "ano"]).reset_index(drop=True))
    # Otra ruta: cada vector anual se contrasta directamente con las filas fuente.
    for ano, g in todas.groupby("ano"):
        original = raw.loc[g.fila_fuente]
        np.testing.assert_allclose(g.valor, original[f"Y{ano}"], equal_nan=True)
        np.testing.assert_array_equal(g.flag.fillna(""), original[f"Y{ano}F"].fillna(""))
        np.testing.assert_array_equal(g.codigo_area, original["Area Code"])
    assert paises.ano.between(1961, 2023).all() and paises.codigo_area.lt(5000).all()
    assert not paises.area.isin(["China", "Ethiopia PDR", "Sudan (former)"]).any()
    assert paises.area.nunique() == 112 and len(paises) == 21168
    bajas = pd.read_csv(OUT / "paises_baja_cobertura.csv")
    assert len(bajas) == 12 and bajas.area.nunique() == 4
    noflag = pd.read_csv(RAIZ / "data/raw/serie3/Production_Crops_Livestock_E_All_Data_NOFLAG.csv", low_memory=False)
    noflag = noflag[noflag.Item == "Sugar cane"].set_index(["Area Code", "Element Code"])
    sc = sc.set_index(["Area Code", "Element Code"])
    anos = [c for c in sc if c.startswith("Y") and c[1:].isdigit()]
    np.testing.assert_allclose(sc[anos], noflag.reindex(sc.index)[anos], equal_nan=True)


def test_calidad_balance_y_tripletas_reconstruidos_desde_crudo():
    raw = pd.read_csv(RAIZ / "data/raw/serie3/Production_Crops_Livestock_E_All_Data.csv", low_memory=False)
    sc = raw[raw.Item == "Sugar cane"]
    prod = sc[sc.Element == "Production"].set_index("Area")
    calidad = pd.read_csv(OUT / "calidad_por_ano.csv").set_index("ano")
    balance = pd.read_csv(OUT / "balance_mundial.csv").set_index("ano")
    area = sc[sc.Element == "Area harvested"].set_index("Area")
    rendimiento = sc[sc.Element == "Yield"].set_index("Area")
    coherencia = pd.read_csv(OUT / "coherencia_area_rendimiento_produccion.csv")
    for ano in range(1961, 2024):
        c = f"Y{ano}"
        g = prod[(prod["Area Code"] < 5000) & ~prod.index.isin(["China", "Ethiopia PDR", "Sudan (former)"])]
        observadas = g[g[c].notna()]
        assert calidad.loc[ano, "n_observadas"] == len(observadas)
        np.testing.assert_allclose(calidad.loc[ano, "proporcion_no_oficial"],
                                  observadas[c + "F"].isin(["E", "I", "X"]).sum() / len(observadas))
        # El total histórico incluye predecesores, pero nunca China agregado.
        vector = prod.loc[(prod["Area Code"] < 5000) & (prod.index != "China"), c]
        esperado = np.nansum(vector.values)
        np.testing.assert_allclose(balance.loc[ano, "suma_territorios"], esperado, atol=1e-5)
        assert abs(esperado - prod.loc["World", c]) < .051
        comparacion = coherencia[coherencia.ano == ano].set_index("area")
        esperado_t = area[c] * rendimiento[c] / 1000
        np.testing.assert_allclose(comparacion.loc[esperado_t.index, "produccion_calculada"], esperado_t, equal_nan=True)
        area_implicita = prod[c] * 1000 / rendimiento[c].replace(0, np.nan)
        np.testing.assert_allclose(comparacion.loc[area_implicita.index, "area_implicita_ha"], area_implicita, equal_nan=True)
    marcas = coherencia[coherencia.en_ambito_paises & coherencia.revisar]
    assert len(marcas) == 63 and marcas.compatible_redondeo_area_1ha.all()
