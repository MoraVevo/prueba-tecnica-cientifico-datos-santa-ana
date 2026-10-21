import numpy as np
import pandas as pd

from scripts.comparar_carga_serie2 import (
    COL, NECESARIAS, agregar_bloques, auditar_filas, preparar_contraste,
    resumir_pares,
)


def datos_dos_bloques(faltantes=0):
    fechas = pd.date_range("2022-01-01", periods=120, freq="5s")
    d = pd.DataFrame({"date": fechas})
    for c in NECESARIAS:
        d[c] = 10.0
    d.loc[60:, COL["air"]] = 20.0
    d.loc[60:, COL["o2_a"]] = 4.0
    d.loc[60:, COL["o2_b"]] = 3.0
    d.loc[60:, COL["gas_a"]] = 400.0
    d.loc[60:, COL["gas_b"]] = 390.0
    # Variación interna suficiente para revisar agregación y filtro de estabilidad.
    d.loc[0, COL["steam"]] = 10.2
    if faltantes:
        d.loc[:faltantes - 1, COL["gas_a"]] = np.nan
    return d


def test_agregacion_usa_bloques_de_60_y_mantiene_cobertura_por_sensor():
    d = datos_dos_bloques(faltantes=6)
    b = agregar_bloques(d)
    assert len(b) == 2
    assert b.filas_fuente.tolist() == [60, 60]
    assert b[f"n__{COL['gas_a']}"].tolist() == [54, 60]
    assert b.cobertura_ok.tolist() == [False, True]
    assert b.loc[0, COL["steam"]] == 10.0
    assert np.isclose(b.loc[0, f"rango__{COL['steam']}"] , 0.2)


def test_matching_exige_dia_soporte_y_balance_de_carga():
    d = datos_dos_bloques()
    b = agregar_bloques(d)
    # El emparejamiento unitario de dos bloques se prueba con una réplica
    # de bloques que comparte carga y día, pero separa claramente el aire.
    base = b.iloc[0].copy()
    filas = []
    aire_niveles = [10, 11, 12, 13, 14, 15, 20, 21, 22, 23, 24, 25]
    carga = [10, 11, 12] * 4
    for i, aire in enumerate(aire_niveles):
        x = base.copy()
        x["bloque_id"] = i
        x["dia"] = "2022-01-01"
        x[COL["air"]] = aire
        x[COL["steam"]] = float(carga[i])
        x[COL["pressure"]] = float(5 + carga[i] * .1)
        x["rango__" + COL["steam"]] = .1
        x["rango__" + COL["pressure"]] = .01
        x["cobertura_ok"] = True
        for c in NECESARIAS:
            x[f"n__{c}"] = 60
            x[c] = x.get(c, 10.0)
        filas.append(x)
    clas, pares = preparar_contraste(pd.DataFrame(filas), estabilidad=1.0,
                                     caliper_variable=.20, caliper_total=.30)
    assert len(pares) > 0
    assert pares.bloque_alto.is_unique and pares.bloque_bajo.is_unique
    assert pares.dia.eq("2022-01-01").all()
    assert pares.dif_vapor_sd.abs().max() <= .20
    assert pares.dif_presion_sd.abs().max() <= .20
    assert clas.loc[clas.soporte, "motivo"].eq("incluido_en_par_emparejado").all()


def test_resumen_conserva_todas_las_filas_y_diferencia_alto_menos_bajo():
    d = datos_dos_bloques()
    b = agregar_bloques(d)
    b["dia"] = "2022-01-01"
    # Contraste explícito de los dos bloques, independientemente del matcher.
    pares = pd.DataFrame([{"dia": "2022-01-01", "bloque_alto": 1, "bloque_bajo": 0,
                           "distancia_carga_sd": 0.0, "dif_vapor_sd": 0.0, "dif_presion_sd": 0.0}])
    detalle, _ = resumir_pares(b, pares)
    assert detalle.loc[0, f"dif__{COL['o2_a']}"] == -6.0
    assert detalle.loc[0, f"dif__{COL['gas_a']}"] == 390.0
    b, _ = preparar_contraste(b)
    auditoria = auditar_filas(d, b)
    assert len(auditoria) == len(d) == 120
    assert auditoria.fila_fuente_1based.tolist() == list(range(1, 121))
    assert auditoria.bloque_id.value_counts().to_dict() == {0: 60, 1: 60}
