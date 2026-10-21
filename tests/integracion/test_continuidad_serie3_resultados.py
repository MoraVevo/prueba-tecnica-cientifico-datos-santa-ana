"""Reconstruye salidas del contraste con ecuaciones independientes sencillas."""

import json
from pathlib import Path

import numpy as np
import pandas as pd


RAIZ = Path(__file__).resolve().parents[2]
OUT = RAIZ / "outputs/serie3_continuidad"


def test_contraste_mensual_y_movimientos_mar11_se_reconstruyen_desde_fuentes():
    crudo = pd.read_csv(RAIZ / "data/raw/serie3/Sugar_data.csv", parse_dates=["date"])
    mensual = pd.read_csv(OUT / "contraste_mensual_usda.csv")
    ref = pd.read_csv(OUT / "ers_precios_azucar_world_2026-10-20.csv", low_memory=False)
    ref = ref.loc[
        ref.Table_number.astype(str).eq("3b") & ref.Year_cat.eq("Calendar") & ref.Period_cat.eq("Month")
    ].copy()
    ref["mes"] = ref.Year.astype(int).astype(str) + "-" + ref.Period.astype(int).astype(str).str.zfill(2)
    m = crudo.assign(mes=crudo.date.dt.strftime("%Y-%m")).groupby("mes").close.mean()
    z = mensual.set_index("mes")
    assert len(crudo) == 6097 and len(mensual) == 292
    assert mensual.mes_completo_en_archivo.sum() == 291
    assert mensual.loc[~mensual.mes_completo_en_archivo, "mes"].tolist() == ["2024-06"]
    np.testing.assert_allclose(z.cierre_medio, m.loc[z.index], atol=1e-12)
    for fila in ref.itertuples():
        if fila.mes in z.index:
            assert z.loc[fila.mes, "usda_cercano_mensual"] == fila.Value
    np.testing.assert_allclose(
        z.diferencia_centavos,
        z.cierre_medio - z.usda_cercano_mensual,
        equal_nan=True,
        atol=1e-12,
    )

    fnb = pd.read_csv(OUT / "movimientos_mismo_vencimiento_fnb.csv", parse_dates=["date"])
    elegidos = fnb[fnb.estado.eq("cotejo_publicado")]
    assert elegidos.contrato.eq("Mar-11").all()
    assert len(elegidos) == 3 and elegidos.coincide_a_centavo.all()
    np.testing.assert_allclose(elegidos.close, elegidos.referencia, atol=0.0049)
    assert fnb.iloc[-1].estado == "posible_republicacion_obsoleta"
    assert fnb.iloc[1].horizonte_dias_desde_cotejo_anterior == 7

    insee = pd.read_csv(OUT / "divergencia_2003_insee.csv").set_index("mes")
    assert insee.index.tolist() == ["2003-10", "2003-11", "2003-12"]
    np.testing.assert_allclose(insee.insee_cercano, [6.1, 6.2, 6.3])
    assert (insee.diferencia_csv_centavos.abs() < .05).all()
    assert (insee.diferencia_ers_centavos.abs() > .3).all()


def test_sensibilidades_no_certifican_ni_ajustan_la_serie():
    def rechazar_constante(valor):
        raise ValueError(f"Constante no válida en JSON: {valor}")
    d = json.loads((OUT / "decision_continuidad.json").read_text(encoding="utf-8"),
                   parse_constant=rechazar_constante)
    assert d["usda_filas_contraste"] == 292
    assert d["usda_meses_completos_contraste"] == 291
    assert d["usda_meses_parciales_separados"] == 1
    assert d["fnb_coincidencias_csv_a_centavo"] == 3
    assert len(d["insee_2003_contraste"]) == 3
    assert d["ohlc_incoherentes_sin_exclusion"] == 11
    assert d["ohlc_incoherentes_dentro_proxy_enlace"] == 11
    assert len(d["usda_meses_completos_diferencia_abs_mayor_1_pct"]) > 0
    assert d["revision_filas_marcadas_sin_exclusion"] > 0
    assert d["reconstruccion_de_ticker_yahoo_confirmada"] is False
    assert d["precios_diarios_oficiales_historicos_gratuitos_completos"] is False
    assert d["roll_ajustado_o_corregido"] is False
