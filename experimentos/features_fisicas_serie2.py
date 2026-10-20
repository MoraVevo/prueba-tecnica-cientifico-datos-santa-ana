"""Preparación aislada de las tres hipótesis físicas, sin modificar la campeona."""

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


SOPORTES = {
    "aire_x_oxigeno": ["FT_8302.AV_0#", "AIR_8301A.AV_0#", "AIR_8301B.AV_0#"],
    "asimetria_oxigeno": ["AIR_8301A.AV_0#", "AIR_8301B.AV_0#"],
    "agua_x_temperatura": ["YJJWSLL.AV_0#", "TE_8332A.AV_0#"],
}


def preparar_entradas(entrenamiento, evaluacion, columnas_base, candidata=None):
    """Aprende medianas y escalas en entrenamiento; devuelve las mismas filas e índices.

    Las columnas base se conservan y, si corresponde, se añade una sola feature.
    Los soportes sirven para calcularla aunque no sean entradas lineales del modelo.
    El escalado final de todas las entradas corresponde al pipeline de Ridge.
    """
    soportes = SOPORTES[candidata] if candidata is not None else []
    requeridas = list(dict.fromkeys([*columnas_base, *soportes]))
    imputador = SimpleImputer(strategy="median").fit(entrenamiento[requeridas])
    limpio_train = pd.DataFrame(
        imputador.transform(entrenamiento[requeridas]),
        columns=requeridas, index=entrenamiento.index,
    )
    limpio_eval = pd.DataFrame(
        imputador.transform(evaluacion[requeridas]),
        columns=requeridas, index=evaluacion.index,
    )
    train = limpio_train[columnas_base].copy()
    evaluadas = limpio_eval[columnas_base].copy()
    ajustes = {
        "sensores_requeridos": requeridas,
        "medianas": dict(zip(requeridas, imputador.statistics_.tolist())),
    }
    if candidata is None:
        return train, evaluadas, ajustes

    if candidata == "asimetria_oxigeno":
        a, b = soportes
        train[candidata] = (limpio_train[a] - limpio_train[b]).abs()
        evaluadas[candidata] = (limpio_eval[a] - limpio_eval[b]).abs()
    else:
        if candidata == "aire_x_oxigeno":
            flujo, oxigeno_a, oxigeno_b = soportes
            componentes_train = np.column_stack([
                limpio_train[flujo], (limpio_train[oxigeno_a] + limpio_train[oxigeno_b]) / 2,
            ])
            componentes_eval = np.column_stack([
                limpio_eval[flujo], (limpio_eval[oxigeno_a] + limpio_eval[oxigeno_b]) / 2,
            ])
        else:
            componentes_train = limpio_train[soportes].to_numpy()
            componentes_eval = limpio_eval[soportes].to_numpy()
        escalador = StandardScaler().fit(componentes_train)
        train[candidata] = np.prod(escalador.transform(componentes_train), axis=1)
        evaluadas[candidata] = np.prod(escalador.transform(componentes_eval), axis=1)
        ajustes["medias_componentes"] = escalador.mean_.tolist()
        ajustes["escalas_componentes"] = escalador.scale_.tolist()
    return train, evaluadas, ajustes
