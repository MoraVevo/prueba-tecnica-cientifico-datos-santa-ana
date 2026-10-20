"""Vista de proceso para regímenes, independiente de las entradas del sensor virtual."""

import numpy as np
import pandas as pd


PRESIONES_HOGAR = [f"PT_8313{letra}.AV_0#" for letra in "ABCDEF"]
FAMILIAS = {
    "Presión de vapor": ["PTCA_8324.AV_0#"],
    "Temperatura del hogar": ["TE_8313B.AV_0#"],
    "Temperatura de gases": ["TE_8319A.AV_0#", "TE_8319B.AV_0#"],
    "Precalentamiento del aire": ["TE_8303.AV_0#", "TE_8304.AV_0#"],
    "Suministro de aire": ["FT_8301.AV_0#", "FT_8302.AV_0#"],
    "Oxígeno": ["AIR_8301A.AV_0#", "AIR_8301B.AV_0#"],
    "Presión del hogar": ["presion_hogar_sintesis"],
}
ENTRADAS = [c for columnas in FAMILIAS.values() for c in columnas]
PESOS = pd.Series({c: 1 / np.sqrt(len(columnas)) for columnas in FAMILIAS.values() for c in columnas})


def construir_vista(datos, minutos=1):
    """Resume intervalos completos y conserva correspondencia de todas las filas.

    La mediana describe estados sostenidos; no elimina los picos del crudo.
    Una etiqueta de esta vista solo estaría disponible al cerrar el intervalo.
    """
    assert datos.date.is_unique and datos.date.is_monotonic_increasing
    assert datos.date.diff().dropna().eq(pd.Timedelta(seconds=5)).all()
    inicio = datos.date.iloc[0]
    intervalo = pd.Timedelta(minutes=minutos)
    grupos = ((datos.date - inicio) // intervalo).astype(int)
    numericas = datos.drop(columns="date")
    vista = numericas.groupby(grupos.to_numpy()).median()
    vista.index.name = "intervalo"
    conteos = grupos.value_counts().sort_index()
    assert conteos.eq(minutos * 12).all(), "Hay intervalos incompletos; revisar sin descartar filas."
    vista["inicio"] = inicio + pd.to_timedelta(vista.index * minutos, unit="min")
    vista["disponible_desde"] = vista.inicio + intervalo
    vista["fin_lectura"] = vista.disponible_desde - pd.Timedelta(seconds=5)
    vista["filas_fuente"] = conteos.to_numpy()
    entradas = vista[[c for c in ENTRADAS if c != "presion_hogar_sintesis"]].copy()
    # Síntesis numérica del nivel común; no es una presión física calibrada del hogar.
    entradas["presion_hogar_sintesis"] = vista[PRESIONES_HOGAR].median(axis=1)
    entradas = entradas[ENTRADAS]
    assert entradas.notna().all().all() and np.isfinite(entradas.to_numpy()).all()
    correspondencia = pd.DataFrame({
        "fila_fuente": np.arange(len(datos)), "date": datos.date.to_numpy(),
        "intervalo": grupos.to_numpy(),
    })
    return vista, entradas, correspondencia


def resumir_episodios(vista, etiquetas):
    """Duraciones como intervalos completos, sin sumar solo diferencias de timestamps."""
    tabla = vista[["inicio", "disponible_desde"]].copy()
    tabla["regimen"] = np.asarray(etiquetas)
    cambios = tabla.regimen.ne(tabla.regimen.shift()).cumsum()
    episodios = tabla.groupby(cambios, sort=False).agg(
        regimen=("regimen", "first"), inicio=("inicio", "first"),
        fin=("disponible_desde", "last"), intervalos=("regimen", "size"),
    ).reset_index(drop=True)
    episodios["minutos"] = (episodios.fin - episodios.inicio).dt.total_seconds() / 60
    return episodios
