"""Reconstruye las features y Ridge por ecuaciones, sin usar el módulo experimental."""

import json
from pathlib import Path

import numpy as np
import pandas as pd


RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "outputs/experimento_features"


def test_experimento_conserva_filas_particiones_y_seleccion_original():
    assert (SALIDA / "verificacion.json").exists(), "Ejecutar notebook 08 antes de esta integración."
    fuente = pd.read_csv(RAIZ / "data/raw/serie2/data.csv", parse_dates=["date"])
    usadas = pd.read_csv(SALIDA / "filas_modelado.csv")
    fuera = pd.read_csv(SALIDA / "filas_fuera_experimento.csv")
    assert len(usadas) == 34560 and len(fuera) == 51840
    ids = pd.concat([usadas.fila_fuente, fuera.fila_fuente])
    assert ids.is_unique and set(ids) == set(range(len(fuente)))
    pd.testing.assert_frame_equal(
        fuente.iloc[fuera.fila_fuente].reset_index(drop=True),
        fuera.drop(columns=["fila_fuente", "motivo"]).assign(date=lambda t: pd.to_datetime(t.date)),
    )
    assert fuera.motivo.notna().all()
    limite = fuente.date.iloc[0] + pd.Timedelta(days=4)
    pred = pd.read_csv(SALIDA / "predicciones_validacion.csv", parse_dates=["date"])
    assert len(pred) == 259200 and pred.date.lt(limite).all()
    for _, grupo in pred.groupby(["particion", "variante"]):
        assert len(grupo) == 8640 and grupo.date.is_unique
        np.testing.assert_allclose(grupo.observado, fuente.iloc[grupo.fila_fuente]["ZZQBCHLL.AV_0#"])
    nuevas = pd.read_csv(SALIDA / "selecciones_por_pliegue.csv").rename(columns={"sensor": "entrada"})
    anteriores = pd.read_csv(RAIZ / "outputs/serie2_selecciones_por_pliegue.csv")
    pd.testing.assert_frame_equal(nuevas, anteriores)
    decision = json.loads((SALIDA / "decision_experimental.json").read_text(encoding="utf-8"))
    assert decision["variante_recomendada"] == "Base 15"
    assert decision["comprobacion_final_evaluada"] is False


def test_nueve_predicciones_experimentales_reconstruidas_por_ecuacion_ridge():
    fuente = pd.read_csv(RAIZ / "data/raw/serie2/data.csv", parse_dates=["date"])
    rejilla = fuente.iloc[::2].copy()
    selecciones = pd.read_csv(SALIDA / "selecciones_por_pliegue.csv")
    predicciones = pd.read_csv(SALIDA / "predicciones_validacion.csv")
    objetivos = "ZZQBCHLL.AV_0#"
    soportes = {
        "aire_x_oxigeno": ["FT_8302.AV_0#", "AIR_8301A.AV_0#", "AIR_8301B.AV_0#"],
        "asimetria_oxigeno": ["AIR_8301A.AV_0#", "AIR_8301B.AV_0#"],
        "agua_x_temperatura": ["YJJWSLL.AV_0#", "TE_8332A.AV_0#"],
    }
    for dia in [1, 2, 3]:
        particion = f"Validación {dia}"
        limite = fuente.date.iloc[0] + pd.Timedelta(days=dia)
        train = rejilla.loc[rejilla.date.lt(limite - pd.Timedelta(minutes=5))]
        evaluacion = rejilla.loc[rejilla.date.ge(limite) & rejilla.date.lt(limite + pd.Timedelta(days=1))]
        columnas = selecciones.loc[selecciones.particion.eq(particion), "sensor"].tolist()
        y = train[objetivos].to_numpy()
        for candidata, soporte in soportes.items():
            requeridas = list(dict.fromkeys([*columnas, *soporte]))
            medianas = train[requeridas].median()
            a, b = train[requeridas].fillna(medianas), evaluacion[requeridas].fillna(medianas)
            matrices = []
            componentes = []
            for datos in [a, b]:
                if candidata == "aire_x_oxigeno":
                    componentes.append(np.column_stack([datos[soporte[0]], (datos[soporte[1]] + datos[soporte[2]]) / 2]))
                else:
                    componentes.append(datos[soporte].to_numpy())
            for datos, componentes_datos in zip([a, b], componentes):
                if candidata == "asimetria_oxigeno":
                    feature = np.abs(componentes_datos[:, 0] - componentes_datos[:, 1])
                else:
                    z = (componentes_datos - componentes[0].mean(axis=0)) / componentes[0].std(axis=0)
                    feature = z[:, 0] * z[:, 1]
                matrices.append(np.column_stack([datos[columnas].to_numpy(), feature]))
            media, escala = matrices[0].mean(axis=0), matrices[0].std(axis=0)
            z_train, z_eval = [(matriz - media) / escala for matriz in matrices]
            # Solución cerrada con intercepto, independiente de sklearn y del experimento.
            beta = np.linalg.solve(z_train.T @ z_train + 100 * np.eye(16), z_train.T @ (y - y.mean()))
            reconstruida = z_eval @ beta + y.mean()
            guardadas = predicciones.loc[predicciones.particion.eq(particion)
                                         & predicciones.variante.eq(f"{candidata} | sola")]
            np.testing.assert_array_equal(guardadas.fila_fuente, evaluacion.index)
            np.testing.assert_allclose(guardadas.estimado, reconstruida, rtol=0, atol=1e-8)
