"""Contratos de cálculo: exclusión trazable, ventanas y retornos sin puentes."""

import numpy as np
import pandas as pd

from scripts.analizar_precios_serie3 import preparar, ventana_enlace, volatilidad_movil


def test_marcas_conservan_datos_y_no_unen_retornos_a_traves_de_exclusiones():
    fechas = pd.bdate_range("2024-01-03", periods=8)
    crudo = pd.DataFrame({"date": fechas, "open": np.arange(8)+10.,
        "high": np.arange(8)+11., "low": np.arange(8)+9.,
        "close": np.arange(8)+10., "volume": 100})
    crudo.loc[2, "volume"] = 0
    crudo.loc[5, "high"] = crudo.loc[5, "close"] - .02
    copia = crudo.copy(deep=True)
    p = preparar(crudo)
    pd.testing.assert_frame_equal(crudo, copia)
    pd.testing.assert_frame_equal(p[crudo.columns], crudo)
    assert p.index[p.admisible_sensibilidad].tolist() == [1,4,7]
    np.testing.assert_allclose(p.loc[4, "retorno_log"], np.log(14/13))
    assert "anterior_cero" in p.loc[3,"motivo_fuera_sensibilidad"]
    assert "anterior_incoherente" in p.loc[6,"motivo_fuera_sensibilidad"]


def test_proxy_no_convierte_ultimo_dato_truncado_en_vencimiento():
    fechas = pd.Series(pd.to_datetime(["2024-04-29","2024-04-30","2024-05-01",
        "2024-05-02","2024-06-20","2024-06-21","2024-06-24"]))
    assert fechas[ventana_enlace(fechas)].dt.strftime("%Y-%m-%d").tolist() == ["2024-04-30","2024-05-01"]
    amplia = ventana_enlace(fechas, ancho=2)
    assert amplia.iloc[:4].all() and not amplia.iloc[4:].any()
    historia = pd.Series(pd.to_datetime(["2009-12-17","2009-12-18","2009-12-21",
        "2009-12-22","2009-12-23","2009-12-24","2009-12-28","2009-12-29",
        "2009-12-30","2009-12-31","2010-01-04","2010-02-01"]))
    assert not ventana_enlace(historia).any()
    assert ventana_enlace(historia,diciembre_historico=True).iloc[3:11].all()


def test_ventana_movil_respeta_huecos_y_no_usa_retornos_futuros():
    r = pd.Series([np.nan,.01,.03,np.nan,.02,-.01,.04,.01,-.02])
    esperado = np.std([.03,.02,-.01], ddof=1)*np.sqrt(252)*100
    v = volatilidad_movil(r,ventana=4,minimo=3)
    assert v.iloc[:4].isna().all()
    np.testing.assert_allclose(v.iloc[5],esperado)
    cambio = r.copy(); cambio.iloc[6:] = 100
    pd.testing.assert_series_equal(v.iloc[:6],volatilidad_movil(cambio,4,3).iloc[:6])
