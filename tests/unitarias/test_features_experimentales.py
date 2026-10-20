"""Verifica fórmulas e independencia de la evaluación en el experimento físico."""

import numpy as np
import pandas as pd
import pytest

from experimentos.features_fisicas_serie2 import SOPORTES, preparar_entradas


@pytest.mark.parametrize("candidata", list(SOPORTES))
def test_feature_aprende_solo_del_entrenamiento_y_conserva_filas(candidata):
    datos = pd.DataFrame({
        "FT_8302.AV_0#": [10., 20., 30., 40.],
        "AIR_8301A.AV_0#": [1., 3., 2., 4.],
        "AIR_8301B.AV_0#": [2., 1., 4., 3.],
        "YJJWSLL.AV_0#": [1., np.nan, 3., 5.],
        "TE_8332A.AV_0#": [530., 534., 537., 539.],
    }, index=[2, 4, 6, 8])
    original = datos.copy(deep=True)
    base = ["YJJWSLL.AV_0#"]
    evaluacion = datos.iloc[[0, 2]].copy()
    train, pred, ajuste = preparar_entradas(datos, evaluacion, base, candidata)
    futura = evaluacion * 1e6
    otra_train, _, otro_ajuste = preparar_entradas(datos, futura, base, candidata)
    pd.testing.assert_frame_equal(train, otra_train)
    assert ajuste == otro_ajuste
    assert train.index.equals(datos.index) and pred.index.equals(evaluacion.index)
    assert train.columns.tolist() == [*base, candidata]
    pd.testing.assert_frame_equal(datos, original)
    assert ajuste["medianas"][base[0]] == 3
    assert np.isfinite(pred.to_numpy()).all()

    limpio = datos.fillna({base[0]: 3})
    if candidata == "asimetria_oxigeno":
        esperado = (limpio[SOPORTES[candidata][0]] - limpio[SOPORTES[candidata][1]]).abs()
    else:
        if candidata == "aire_x_oxigeno":
            componentes = np.column_stack([
                limpio["FT_8302.AV_0#"],
                (limpio["AIR_8301A.AV_0#"] + limpio["AIR_8301B.AV_0#"]) / 2,
            ])
        else:
            componentes = limpio[SOPORTES[candidata]].to_numpy()
        # Reconstrucción de la fórmula, sin reutilizar el escalador de producción.
        normalizados = (componentes - componentes.mean(axis=0)) / componentes.std(axis=0)
        esperado = normalizados[:, 0] * normalizados[:, 1]
    np.testing.assert_allclose(train[candidata], esperado, rtol=0, atol=1e-12)
