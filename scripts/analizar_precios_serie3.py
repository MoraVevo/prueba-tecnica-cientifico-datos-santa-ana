"""Serie III.2: calidad, volatilidad y estados descriptivos del azúcar No. 11.

La sensibilidad excluye retornos sospechosos; no reconstruye contratos ni
convierte la serie continua en una serie certificada de un mismo contrato.
"""

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


MESES_PREVIOS = [2, 4, 6, 9]
MESES_ENTREGA = [3, 5, 7, 10]
TOLERANCIA_OHLC = 1e-5  # Menor que el tick 0.01; tolera ruido de coma flotante.


def ventana_enlace(fechas, ancho=1, diciembre_historico=False):
    """Proxy por sesiones observadas, no calendario certificado de vencimientos.

    Marca las últimas/primeras sesiones de meses adyacentes a las entregas
    actuales. Diciembre hasta 2009 es una sensibilidad histórica adicional:
    también existieron contratos de enero, con excepciones no reconstruidas.
    """
    meses = fechas.dt.to_period("M")
    posicion = fechas.groupby(meses).cumcount()
    inversa = fechas.groupby(meses).cumcount(ascending=False)
    # Solo fronteras rodeadas por datos. El CSV termina el 24-06-2024:
    # su última fila no es por ello el último día de negociación de junio.
    fin_observable = meses.lt(meses.max())
    inicio_observable = meses.gt(meses.min())
    marca = ((fechas.dt.month.isin(MESES_PREVIOS) & inversa.lt(ancho) & fin_observable) |
             (fechas.dt.month.isin(MESES_ENTREGA) & posicion.lt(ancho) & inicio_observable))
    if diciembre_historico:
        # Siete sesiones cubren también la excepción 22-12-2009, sin afirmar
        # que el proveedor haya seguido ese contrato o ese día para enlazar.
        marca |= ((fechas.dt.year.le(2009) & fechas.dt.month.eq(12) & inversa.lt(7) & fin_observable) |
                  (fechas.dt.year.le(2010) & fechas.dt.month.eq(1) & posicion.lt(ancho) & inicio_observable))
    return marca


def preparar(crudo):
    """Conserva cada fila y ambos extremos de los retornos retirados por sensibilidad."""
    p = crudo.copy(deep=True).reset_index(drop=True)
    p["date"] = pd.to_datetime(p.date)
    assert p.date.is_monotonic_increasing and p.date.is_unique
    campos = ["open", "high", "low", "close", "volume"]
    assert p[campos].notna().all().all()
    assert np.isfinite(p[campos].to_numpy()).all()
    assert p[campos[:4]].gt(0).all().all() and p.volume.ge(0).all()
    p["fecha_anterior"] = p.date.shift()
    p["cierre_anterior"] = p.close.shift()
    p["dias_desde_anterior"] = p.date.diff().dt.days
    p["retorno_simple_pct"] = 100 * (p.close / p.cierre_anterior - 1)
    p["retorno_log"] = np.log(p.close / p.cierre_anterior)
    p["ohlc_incoherente"] = ((p.high + TOLERANCIA_OHLC < p[["open", "low", "close"]].max(axis=1)) |
                              (p.low - TOLERANCIA_OHLC > p[["open", "high", "close"]].min(axis=1)))
    p["volumen_cero"] = p.volume.eq(0)
    p["proxy_enlace"] = ventana_enlace(p.date)
    p["proxy_enlace_amplia"] = ventana_enlace(p.date, ancho=2)
    p["proxy_diciembre_historico"] = ventana_enlace(p.date, diciembre_historico=True)
    p["extremo_con_ohlc_incoherente"] = p.ohlc_incoherente | p.ohlc_incoherente.shift(fill_value=False)
    p["extremo_con_volumen_cero"] = p.volumen_cero | p.volumen_cero.shift(fill_value=False)
    motivos = pd.Series("", index=p.index)
    for mascara, motivo in [
        (p.retorno_log.isna(), "sin_cierre_anterior"),
        (p.proxy_enlace, "ventana_proxy_enlace"),
        (p.extremo_con_ohlc_incoherente, "OHLC_actual_o_anterior_incoherente"),
        (p.extremo_con_volumen_cero, "volumen_actual_o_anterior_cero")
    ]:
        motivos.loc[mascara] += motivo + ";"
    p["motivo_fuera_sensibilidad"] = motivos.str.rstrip(";")
    p["admisible_sensibilidad"] = motivos.eq("")
    return p


def volatilidad_movil(retornos, ventana=63, minimo=50):
    """Desviación muestral de log-retornos, sqrt(252); sin comprimir huecos.

    Requiere la ventana temporal completa y el mínimo de retornos observados.
    No es volatilidad implícita, pronóstico ni intervalo de confianza.
    """
    v = retornos.rolling(ventana, min_periods=minimo).std(ddof=1) * np.sqrt(252) * 100
    return v.where(np.arange(len(v)) >= ventana)


def estados(volatilidad, limites):
    """Cuartiles históricos: estados descriptivos, sin entrenamiento predictivo."""
    estado = pd.Series("sin_cobertura", index=volatilidad.index)
    estado.loc[volatilidad.notna() & volatilidad.le(limites[0])] = "baja"
    estado.loc[volatilidad.gt(limites[0]) & volatilidad.le(limites[1])] = "intermedia"
    estado.loc[volatilidad.gt(limites[1])] = "alta"
    return estado


def resumir(retornos):
    r = retornos.dropna()
    simple = np.expm1(r) * 100
    return {"n_retornos": len(r), "vol_anualizada_pct": r.std(ddof=1)*np.sqrt(252)*100,
            "q01_simple_pct": simple.quantile(.01), "q99_simple_pct": simple.quantile(.99),
            "p99_abs_log_pct": r.abs().quantile(.99)*100,
            "min_simple_pct": simple.min(), "max_simple_pct": simple.max()}


def ejecutar(raiz):
    raiz = Path(raiz)
    salida = raiz / "outputs/serie3_precios"
    salida.mkdir(parents=True, exist_ok=True)
    fuente = raiz / "data/raw/serie3/Sugar_data.csv"
    huella = hashlib.sha256(fuente.read_bytes()).hexdigest()
    crudo = pd.read_csv(fuente)
    p = preparar(crudo)
    restricciones_calidad = p.extremo_con_ohlc_incoherente | p.extremo_con_volumen_cero
    variantes = {
        "observada": p.retorno_log.notna(),
        "proxy_enlace": ~p.proxy_enlace & p.retorno_log.notna(),
        "restringida": p.admisible_sensibilidad,
        "ventana_amplia": ~(p.proxy_enlace_amplia | restricciones_calidad) & p.retorno_log.notna(),
        "diciembre_historico": ~(p.proxy_diciembre_historico | restricciones_calidad) & p.retorno_log.notna(),
    }
    resumen = pd.DataFrame([{"variante": nombre, **resumir(p.retorno_log.where(mascara))}
                            for nombre, mascara in variantes.items()])
    resumen.to_csv(salida / "sensibilidad_retornos.csv", index=False)
    anuales = []
    for nombre in ["observada", "restringida"]:
        for ano, indices in p.groupby(p.date.dt.year).groups.items():
            r = p.loc[indices, "retorno_log"].where(variantes[nombre].loc[indices])
            anuales.append({"ano": ano, "variante": nombre,
                            "periodo_parcial": ano in [p.date.dt.year.min(), p.date.dt.year.max()], **resumir(r)})
    pd.DataFrame(anuales).to_csv(salida / "volatilidad_anual.csv", index=False)
    r = p.retorno_log.where(p.admisible_sensibilidad)
    p["vol_63_observada_pct"] = volatilidad_movil(p.retorno_log)
    p["n_retornos_63_restringida"] = r.rolling(63).count()
    p["vol_63_restringida_pct"] = volatilidad_movil(r)
    p["vol_21_restringida_pct"] = volatilidad_movil(r, 21, 16)
    limites = p.vol_63_restringida_pct.quantile([.25, .75]).to_list()
    p["estado_63"] = estados(p.vol_63_restringida_pct, limites)
    p["estado_63_observada"] = estados(p.vol_63_observada_pct, limites)
    p["estado_21"] = estados(p.vol_21_restringida_pct, p.vol_21_restringida_pct.quantile([.25,.75]).to_list())
    umbral = p.retorno_log.abs().quantile(.99)
    p["extremo_p99_observado"] = p.retorno_log.abs().ge(umbral)
    p["extremo_p99_restringido"] = r.abs().ge(r.abs().quantile(.99))
    agrupacion = p.estado_63.ne(p.estado_63.shift()).cumsum()
    episodios = p.groupby(agrupacion).agg(
        estado=("estado_63", "first"), inicio=("date", "min"), fin=("date", "max"),
        sesiones=("date", "size"), vol_mediana_pct=("vol_63_restringida_pct", "median"))
    episodios.to_csv(salida / "episodios_estados.csv", index=False)
    p.groupby("estado_63").agg(sesiones=("date", "size"),
        vol_mediana_pct=("vol_63_restringida_pct", "median"),
        precio_mediano_cent_lb=("close", "median")).to_csv(salida / "perfiles_estados.csv")
    # Correlación solo entre pares de sesiones originales: no unir huecos retirados.
    correlaciones = []
    for nombre in ["observada", "restringida"]:
        x = p.retorno_log.where(variantes[nombre])
        for rezago in [1,5]:
            for transformacion in ["retorno", "absoluto"]:
                y = x.abs() if transformacion == "absoluto" else x
                pares = pd.concat([y, y.shift(rezago)], axis=1).dropna()
                correlaciones.append({"variante": nombre, "rezago_sesiones": rezago,
                    "transformacion": transformacion, "n_pares": len(pares),
                    "correlacion": pares.iloc[:,0].corr(pares.iloc[:,1])})
    pd.DataFrame(correlaciones).to_csv(salida / "dependencia_retornos.csv", index=False)
    p.to_csv(salida / "precios_y_marcas.csv", index=False)
    p[~p.admisible_sensibilidad].to_csv(salida / "retornos_fuera_sensibilidad.csv", index=False)
    p[p.extremo_p99_observado | p.extremo_p99_restringido].to_csv(salida / "extremos.csv", index=False)
    p[p.ohlc_incoherente].to_csv(salida / "revision_ohlc.csv", index=False)
    p[p.volumen_cero].to_csv(salida / "revision_volumen.csv", index=False)
    p[p.dias_desde_anterior > 4].to_csv(salida / "revision_huecos.csv", index=False)
    comparables = p.estado_63.ne("sin_cobertura") & p.estado_63_observada.ne("sin_cobertura")
    decision = {"fuente_sha256": huella, "filas_crudas": len(crudo), "retornos_observados": int(p.retorno_log.notna().sum()),
        "retornos_restringidos": int(p.admisible_sensibilidad.sum()),
        "filas_fuera_sensibilidad": int((~p.admisible_sensibilidad).sum()),
        "ohlc_incoherentes": int(p.ohlc_incoherente.sum()), "volumen_cero": int(p.volumen_cero.sum()),
        "ohlc_en_proxy_enlace": int((p.ohlc_incoherente & p.proxy_enlace).sum()),
        "retornos_proxy_enlace": int((p.proxy_enlace & p.retorno_log.notna()).sum()),
        "fraccion_suma_cuadrados_proxy": float(p.loc[p.proxy_enlace,"retorno_log"].pow(2).sum()/p.retorno_log.pow(2).sum()),
        "p99_abs_log_observado_pct": umbral*100, "limites_estados_63_pct": limites,
        "cambio_estado_por_restriccion_pct": float(100*p.loc[comparables,"estado_63"].ne(p.loc[comparables,"estado_63_observada"]).mean()),
        "n_estados_comparables": int(comparables.sum()), "ventana_sesiones": 63,
        "minimo_retornos_ventana": 50, "anualizacion": 252,
        "construccion_contratos_confirmada": False, "ajuste_de_enlaces": False,
        "serie_restringida_certificada": False,
        "uso": "Descripción histórica y sensibilidad; no pronóstico ni rentabilidad negociable"}
    # Dos precios contrastados con publicaciones externas: no validan todas las fechas.
    corroboracion = pd.DataFrame([
        {"fecha":"2010-11-11", "precio_referencia_cent_lb":29.66, "contrato":"Mar-11", "fuente":"f007",
         "alcance":"cierre previo implícito: 27.98 + caída intradía 1.68; Bloomberg"},
        {"fecha":"2010-11-12", "precio_referencia_cent_lb":26.21, "contrato":"Mar-11", "fuente":"f005",
         "alcance":"tabla ICE Sugar Futures de informe FNB; cotejo puntual, no liquidación oficial certificada"}
    ])
    corroboracion["fecha"] = pd.to_datetime(corroboracion.fecha)
    corroboracion = corroboracion.merge(p[["date","close"]], left_on="fecha", right_on="date", validate="one_to_one")
    corroboracion["diferencia_cent_lb"] = corroboracion.close - corroboracion.precio_referencia_cent_lb
    corroboracion.to_csv(salida / "contraste_externo.csv", index=False)
    assert hashlib.sha256(fuente.read_bytes()).hexdigest() == huella
    (salida / "decision.json").write_text(json.dumps(decision,ensure_ascii=False,indent=2),encoding="utf-8")
    return decision


if __name__ == "__main__":
    print(json.dumps(ejecutar(Path(__file__).resolve().parents[1]),ensure_ascii=True,indent=2))
