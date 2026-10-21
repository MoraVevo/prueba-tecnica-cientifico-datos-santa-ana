"""Pruebas focales del contraste de continuidad, sin red ni exclusión de filas."""

import numpy as np
import pandas as pd
import hashlib
from io import BytesIO

from scripts.verificar_continuidad_serie3 import preparar_fnb, preparar_mensual, preparar_revision


def test_descarga_en_frio_acepta_cabecera_csv_entrecomillada_y_reutiliza_cache(tmp_path, monkeypatch):
    """Formato real ERS: cabecera quoted; no requiere acceso a la red."""
    from scripts import verificar_continuidad_serie3 as modulo

    datos = (b'"Table_number","Year_cat","Period_cat","Year","Period","Value"\n'
             b'"3b","Calendar","Month",2003,12,4.667\n')
    llamadas = []
    def respuesta(url, timeout):
        llamadas.append(url)
        return BytesIO(datos)
    monkeypatch.setattr(modulo, "urlopen", respuesta)
    monkeypatch.setattr(modulo, "FUENTE_USDA_SHA256", hashlib.sha256(datos).hexdigest())
    ruta = tmp_path/"usda.csv"
    a = modulo.cargar_usda(ruta)
    b = modulo.cargar_usda(ruta)
    assert ruta.read_bytes() == datos and len(llamadas) == 1
    pd.testing.assert_frame_equal(a, b)
    assert a.Value.iloc[0] == 4.667


def test_promedio_mensual_conserva_todas_las_observaciones_y_compara_unidad_comun():
    crudo = pd.DataFrame({
        "date": pd.to_datetime(["2008-01-02", "2008-01-03", "2008-02-01"]),
        "open": [10.0, 11.0, 12.0], "high": [11.0, 12.0, 13.0],
        "low": [9.0, 10.0, 11.0], "close": [10.5, 11.5, 12.5], "volume": [1, 0, 2],
    })
    copia = crudo.copy(deep=True)
    usda = pd.DataFrame({
        "Table_number": ["3b", "3b", "3b"], "Year_cat": ["Calendar", "Calendar", "Fiscal"],
        "Period_cat": ["Month"] * 3, "Year": [2008] * 3,
        "Period": [1, 2, 1], "Value": [11.0, 12.5, 999.0],
    })
    mensual = preparar_mensual(crudo, usda)
    pd.testing.assert_frame_equal(crudo, copia)
    assert mensual.sesiones.tolist() == [2, 1]
    assert mensual.mes_completo_en_archivo.tolist() == [False, False]
    np.testing.assert_allclose(mensual.cierre_medio, [11.0, 12.5])
    np.testing.assert_allclose(mensual.diferencia_centavos, [0.0, 0.0])


def test_mismo_vencimiento_compara_cierres_y_marca_tabla_repetida():
    crudo = pd.DataFrame({
        "date": pd.to_datetime(["2010-11-05", "2010-11-12", "2010-11-19", "2010-11-26"]),
        "close": [31.76, 26.21, 26.15, 28.25], "volume": [1, 2, 3, 4],
    })
    r = preparar_fnb(crudo)
    assert r.contrato.eq("Mar-11").all()
    assert r.coincide_a_centavo.tolist() == [True, True, True, False]
    assert r.estado.tolist() == [
        "cotejo_publicado", "cotejo_publicado", "cotejo_publicado",
        "posible_republicacion_obsoleta",
    ]
    assert np.isnan(r.horizonte_dias_desde_cotejo_anterior.iloc[0])
    assert r.horizonte_dias_desde_cotejo_anterior.iloc[1:].tolist() == [7, 7, 7]
    np.testing.assert_allclose(r.retorno_contrato_vs_cotejo_pct.iloc[1:3], [
        100 * (26.21 / 31.76 - 1), 100 * (26.15 / 26.21 - 1),
    ])


def test_saltos_y_datos_ohlc_quedan_marcados_sin_eliminacion():
    crudo = pd.DataFrame({
        "date": pd.to_datetime(["2000-04-28", "2000-05-01", "2008-06-30", "2008-07-01"]),
        "open": [6.1, 6.55, 11.44, 13.10], "high": [6.45, 6.58, 11.59, 13.90],
        "low": [5.0, 6.4, 11.26, 13.1], "close": [5.16, 6.53, 12.04, 13.72],
        "volume": [0, 10, 20, 30],
    })
    r = preparar_revision(crudo)
    pd.testing.assert_frame_equal(crudo, pd.DataFrame({
        "date": pd.to_datetime(["2000-04-28", "2000-05-01", "2008-06-30", "2008-07-01"]),
        "open": [6.1, 6.55, 11.44, 13.10], "high": [6.45, 6.58, 11.59, 13.90],
        "low": [5.0, 6.4, 11.26, 13.1], "close": [5.16, 6.53, 12.04, 13.72],
        "volume": [0, 10, 20, 30],
    }))
    assert r.date.tolist() == [pd.Timestamp("2008-06-30")]
    assert r.ohlc_incoherente.tolist() == [True]
    assert r.volumen_cero.tolist() == [False]
