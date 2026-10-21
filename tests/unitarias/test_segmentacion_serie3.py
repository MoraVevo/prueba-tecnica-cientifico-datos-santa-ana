"""Propiedades del diseño: ceros trazables y pares sin seleccionar por rendimiento."""
import numpy as np
import pandas as pd

from scripts.segmentar_paises_serie3 import representar, buscar_pares


def test_rasgos_no_imputan_ceros_y_exigen_historia_comparable():
    filas = []
    for area, inicio in [("Guatemala", 1961), ("SinHistoria", 2010)]:
        for ano in range(inicio, 2024):
            for elemento, valor in [("Area harvested", 1000.), ("Yield", 50000.), ("Production", 50000.)]:
                filas.append({"area": area, "ano": ano, "elemento": elemento, "valor": valor})
    largo = pd.DataFrame(filas)
    largo.loc[largo.area.eq("Guatemala") & largo.ano.eq(1965) & largo.elemento.eq("Area harvested"), "valor"] = 0
    copia = largo.copy(deep=True)
    rasgos, criterios, bloques, tripletas = representar(largo)
    pd.testing.assert_frame_equal(largo, copia)
    assert rasgos.index.tolist() == ["Guatemala"]
    assert not criterios.set_index("area").loc["SinHistoria", "elegible"]
    assert "1961_1970" in criterios.set_index("area").loc["SinHistoria", "motivo"]
    assert rasgos.loc["Guatemala", "area_reciente_ha"] == 1000
    assert abs(rasgos.loc["Guatemala", "tendencia_area_pct"]) < 1e-10
    assert rasgos.loc["Guatemala", "variabilidad_area_log"] == 0
    cero = tripletas[tripletas.area.eq("Guatemala") & tripletas.ano.eq(1965)].iloc[0]
    assert not cero.tripleta_positiva and cero["Area harvested"] == 0


def test_pares_son_invariantes_a_cualquier_cambio_de_rendimiento():
    f = pd.DataFrame({"area_reciente_ha": [100,25,50,75,100,200,400,500],
                      "tendencia_area_pct": [1,1,0,1,2,1,0,3],
                      "variabilidad_area_log": [3,4,2,3,4,2,1,5],
                      "rendimiento_reciente_kg_ha": np.arange(8)+1.},
                     index=["Guatemala", *list("ABCDEFG")])
    f["log_area_reciente"] = np.log(f.area_reciente_ha)
    esperado = buscar_pares(f)
    f["rendimiento_reciente_kg_ha"] = np.arange(8)[::-1]*1e8
    f["log_rendimiento_reciente"] = 1000
    f["produccion_reciente_t"] = -1e15
    pd.testing.assert_frame_equal(buscar_pares(f), esperado)
    assert not esperado.loc["Guatemala", "elegido"]
    assert not esperado.loc["G", "admisible"]
