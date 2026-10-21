
import numpy as np
import pandas as pd
import pytest

from scripts.analizar_oferta_paises_serie3 import ajustar, preparar_celdas


def test_ajuste_recupera_coeficientes_conocidos():
    x1 = np.linspace(-1, 1, 12)
    x2 = np.cos(np.arange(12))
    x3 = np.sin(np.arange(12)*0.7)
    y = 0.3 + 0.7*x1 - 0.2*x2 + 0.1*x3
    d = pd.DataFrame({"y": y, "g_previa": x1, "p_1": x2, "p_2": x3})
    beta = ajustar(d, "propia_precio")
    assert beta["intercepto"] == pytest.approx(0.3)
    assert beta["g_previa"] == pytest.approx(0.7)
    assert beta["p_1"] == pytest.approx(-0.2)
    assert beta["p_2"] == pytest.approx(0.1)


def test_flags_se_marcan_para_revision_sin_cambiar_motivo_exclusion():
    import pytest
    origen = pd.DataFrame({
        "area": ["Guatemala", "Guatemala", "Guatemala"],
        "ano": [2004, 2004, 2004],
        "elemento": ["Area harvested"]*3, "unidad": ["ha"]*3,
        "valor": [100.0, 101.0, 102.0], "flag": ["A", "E", None],
    })
    resultado = preparar_celdas(origen)
    assert resultado.valor.tolist() == origen.valor.tolist()
    assert resultado.unidad.tolist() == origen.unidad.tolist()
    assert resultado.flag.iloc[0] == "A"
    assert resultado.marca_calidad_solo_revision.tolist() == [False, True, False]
    assert resultado.motivo_fuera_analisis.eq("").all()
    assert resultado.motivo_revision.tolist() == [
        "", "flag_no_A_conservado_solo_revision", "flag_ausente"
    ]


def test_celda_de_otra_geografia_queda_marcada_fuera():
    origen = pd.DataFrame({
        "area": ["Brasil"], "ano": [2004], "elemento": ["Production"],
        "unidad": ["t"], "valor": [500.0], "flag": ["A"],
    })
    resultado = preparar_celdas(origen)
    assert resultado.motivo_fuera_analisis.iloc[0] == "fuera_de_paises_fijados"
    assert not resultado.en_muestra_resultado.iloc[0]
