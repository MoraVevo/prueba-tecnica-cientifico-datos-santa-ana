"""Método no supervisado y simulación offline de las reglas del inciso 4."""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline


def crear_detector(semilla=42):
    """Parámetros fijos, sin etiquetas de falla ni búsqueda de contaminación."""
    return make_pipeline(
        SimpleImputer(strategy="median"),
        IsolationForest(n_estimators=200, max_samples=1024, contamination="auto",
                        random_state=semilla, n_jobs=2),
    )


def contexto_cerrado(fechas, etiquetas_minuto):
    """Usa solo el último minuto cuyo cierre ya ocurrió; no rellena con el futuro."""
    assert fechas.is_monotonic_increasing
    referencias = etiquetas_minuto[["disponible_desde", "regimen"]]
    assert referencias.disponible_desde.is_monotonic_increasing
    contexto = pd.merge_asof(
        pd.DataFrame({"date": fechas.to_numpy()}), referencias,
        left_on="date", right_on="disponible_desde", direction="backward",
    )
    contexto.index = fechas.index
    contexto["regimen_cerrado"] = contexto.regimen.fillna(0).astype(int)
    return contexto[["disponible_desde", "regimen_cerrado"]]


def umbrales_por_contexto(puntajes, perfiles, cuantil=.99):
    """Cuantiles de referencia; el perfil cero usa el umbral global, no es otro régimen."""
    puntajes, perfiles = np.asarray(puntajes), np.asarray(perfiles)
    umbrales = {0: float(np.quantile(puntajes, cuantil))}
    for perfil in np.unique(perfiles):
        if perfil != 0:
            umbrales[int(perfil)] = float(np.quantile(puntajes[perfiles == perfil], cuantil))
    return umbrales


def simular_aviso(candidatas, requeridas=3, ventana=6, despeje=12):
    """Mayoría reciente para activar, recuperación consecutiva para cerrar; sin notificaciones.

    Con pasos de cinco segundos, seis muestras cubren una ventana nominal de 30 s.
    Se exige que la muestra actual sea candidata. Todo el cálculo es causal.
    """
    candidatas = pd.Series(candidatas, dtype=bool)
    disparo = candidatas & candidatas.rolling(ventana, min_periods=ventana).sum().ge(requeridas)
    activas, inicios, cierres = [], [], []
    estado, limpias = False, 0
    for candidata, activar in zip(candidatas, disparo):
        inicio = cierre = False
        if estado:
            limpias = 0 if candidata else limpias + 1
            if limpias >= despeje:
                estado, cierre = False, True
        elif activar:
            estado, inicio, limpias = True, True, 0
        activas.append(estado)
        inicios.append(inicio)
        cierres.append(cierre)
    return pd.DataFrame({"activo": activas, "inicio_aviso": inicios, "cierre_aviso": cierres},
                        index=candidatas.index)


def episodios_marcados(fechas, banderas):
    """Lista tramos contiguos y su cobertura, manteniendo también el último timestamp."""
    tabla = pd.DataFrame({"date": np.asarray(fechas), "bandera": np.asarray(banderas, dtype=bool)})
    grupos = tabla.bandera.ne(tabla.bandera.shift(fill_value=False)).cumsum()
    filas = []
    for _, g in tabla.loc[tabla.bandera].groupby(grupos.loc[tabla.bandera]):
        filas.append(dict(inicio=g.date.iloc[0], fin_lectura=g.date.iloc[-1],
                          fin=g.date.iloc[-1]+pd.Timedelta(seconds=5),
                          lecturas=len(g), cobertura_s=len(g)*5))
    return pd.DataFrame(filas, columns=["inicio", "fin_lectura", "fin", "lecturas", "cobertura_s"])
