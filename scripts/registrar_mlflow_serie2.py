"""Registra en MLflow la comparación histórica y la versión candidata de Serie II."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import joblib
import mlflow
import pandas as pd
from mlflow.models import ModelSignature
from mlflow.types import ColSpec, DataType, Schema
from mlflow.tracking import MlflowClient


RAIZ = Path(__file__).resolve().parents[1]
DIR_SALIDA = RAIZ / "outputs" / "mlflow_entrega_validada"
BASE_DATOS = DIR_SALIDA / "mlflow.db"
ARTEFACTOS = DIR_SALIDA / "artefactos"
NOMBRE_EXPERIMENTO = "Prueba Santa Ana - sensor virtual Serie II"
NOMBRE_MODELO = "serie2_sensor_virtual_ridge_17"
ID_REGISTRO = "serie2_ridge17_validacion_historica_v1"
VARIANTE_CAMPEONA = "15 actuales + historia dos presiones"

FUENTES = {
    "resumen_validacion": RAIZ / "mlflow" / "fuentes" / "comparacion_validacion.csv",
    "metricas_por_ventana": RAIZ / "mlflow" / "fuentes" / "metricas_por_ventana.csv",
    "decision": RAIZ / "mlflow" / "fuentes" / "decision_modelo.json",
    "modelo_ajustado": RAIZ / "mlflow" / "fuentes" / "sensor_virtual_ridge17.joblib",
    "contrato_api": RAIZ / "mlflow" / "fuentes" / "contrato_api.json",
}
CODIGO_FUENTE = [
    RAIZ / "experimentos" / "rezagos_serie2.py",
    RAIZ / "scripts" / "entrenar_campeona_serie2.py",
    RAIZ / "scripts" / "exportar_modelo_serie2.py",
]


def _sha256(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def _preparar() -> tuple[pd.DataFrame, pd.DataFrame, dict, dict, Path]:
    """Comprueba que el registro coincide con el modelo y resultados guardados."""
    for nombre, ruta in FUENTES.items():
        if not ruta.is_file():
            raise FileNotFoundError(f"Falta el artefacto requerido '{nombre}': {ruta}")

    resumen = pd.read_csv(FUENTES["resumen_validacion"])
    metricas = pd.read_csv(FUENTES["metricas_por_ventana"])
    decision = json.loads(FUENTES["decision"].read_text(encoding="utf-8"))
    contrato = json.loads(FUENTES["contrato_api"].read_text(encoding="utf-8"))
    guardado = joblib.load(FUENTES["modelo_ajustado"])

    requeridas = {"variante", "entradas", "MAE_medio", "peor_MAE_diario", "WAPE_agregado"}
    if not requeridas.issubset(resumen.columns):
        raise ValueError("El resumen de validación no contiene las columnas esperadas.")
    if not {"variante", "MAE", "RMSE", "R2", "sesgo"}.issubset(metricas.columns):
        raise ValueError("Las métricas por ventana no contienen las columnas esperadas.")
    candidatos = resumen[resumen["variante"].eq(VARIANTE_CAMPEONA)]
    filas_campeona = metricas[metricas["variante"].eq(VARIANTE_CAMPEONA)]
    if len(candidatos) != 1 or len(filas_campeona) != 3:
        raise ValueError("La comparación ya no tiene una fila resumen y tres ventanas para la campeona.")
    fila = candidatos.iloc[0]
    if int(fila["entradas"]) != 17 or int(decision["alpha"]) != 100:
        raise ValueError("La configuración guardada ya no coincide con la campeona de 17 entradas.")
    if abs(float(fila["MAE_medio"]) - float(decision["MAE_validacion"])) > 1e-9:
        raise ValueError("El MAE del resumen no coincide con la decisión versionada.")
    if abs(float(fila["WAPE_agregado"]) - float(decision["WAPE_validacion_pct"])) > 1e-9:
        raise ValueError("El WAPE del resumen no coincide con la decisión versionada.")
    if _sha256(FUENTES["modelo_ajustado"]) != contrato["huella_joblib_sha256"]:
        raise ValueError("La huella del modelo ajustado no coincide con el contrato de la API.")
    if len(guardado.get("columnas", [])) != 17:
        raise ValueError("El artefacto ajustado no contiene las 17 entradas esperadas.")
    if guardado["columnas"] != [entrada["nombre"] for entrada in contrato["entradas"]]:
        raise ValueError("El orden de entradas no coincide entre el modelo ajustado y la API.")
    modelo = guardado.get("modelo")
    if modelo is None or getattr(modelo, "n_features_in_", None) != 17:
        raise ValueError("El artefacto no contiene el Ridge ajustado con 17 entradas.")
    if not filas_campeona["particion"].astype(str).str.startswith("Validación ").all():
        raise ValueError("Las filas de comparación no corresponden a validaciones temporales.")
    if len(resumen) != 6:
        raise ValueError("Se esperaba la comparación histórica de seis variantes.")
    return resumen, metricas, decision, contrato, modelo


def _crear_experimento(tracking_uri: str) -> str:
    mlflow.set_tracking_uri(tracking_uri)
    cliente = MlflowClient()
    experimento = cliente.get_experiment_by_name(NOMBRE_EXPERIMENTO)
    if experimento is not None:
        return experimento.experiment_id
    return mlflow.create_experiment(
        NOMBRE_EXPERIMENTO,
        artifact_location=ARTEFACTOS.resolve().as_uri(),
        tags={
            "alcance": "registro retrospectivo de Serie II",
            "incluye_datos_crudos": "false",
        },
    )


def _registrar() -> dict:
    os.environ.setdefault("MLFLOW_DISABLE_AGENT_HINT", "1")
    DIR_SALIDA.mkdir(parents=True, exist_ok=True)
    ARTEFACTOS.mkdir(parents=True, exist_ok=True)
    resumen, metricas, decision, contrato, modelo = _preparar()
    uri_db = f"sqlite:///{BASE_DATOS.resolve().as_posix()}"
    experimento_id = _crear_experimento(uri_db)
    mlflow.set_experiment(experiment_id=experimento_id)
    cliente = MlflowClient()

    anteriores = cliente.search_runs(
        [experimento_id],
        filter_string=f"tags.registro_id = '{ID_REGISTRO}'",
        max_results=100,
    )
    finalizado = [
        corrida
        for corrida in anteriores
        if corrida.data.tags.get("registro_finalizado") == "true"
    ]
    if finalizado:
        ids_padre = {corrida.info.run_id for corrida in finalizado}
        ids_hijos = {
            corrida.info.run_id
            for corrida in anteriores
            if corrida.data.tags.get("mlflow.parentRunId") in ids_padre
        }
        versiones = [
            int(version.version)
            for version in cliente.search_model_versions(f"name = '{NOMBRE_MODELO}'")
            if version.run_id in ids_hijos
        ]
        return {
            "estado": "ya_registrado",
            "runs_total": len(finalizado) + len(ids_hijos),
            "runs_padre": len(finalizado),
            "runs_candidatos": len(ids_hijos),
            "version_modelo": max(versiones) if versiones else None,
            "registro_id": ID_REGISTRO,
        }
    if anteriores:
        raise RuntimeError(
            "Existe un registro parcial en la base MLflow. Revísalo antes de crear otro lote."
        )

    resumen = resumen.copy()
    metricas = metricas.copy()
    run_ids: list[str] = []
    version_registrada: int | None = None

    with mlflow.start_run(
        run_name="comparacion_temporal_reconstruida",
        tags={
            "registro_id": ID_REGISTRO,
            "tipo_registro": "retrospectivo",
            "metodo": "importación de resultados ya calculados",
            "reentrenamiento": "false",
        },
    ) as run_comparacion:
        mlflow.log_param("serie", "II")
        mlflow.log_param("objetivo", "ZZQBCHLL.AV_0#")
        mlflow.log_param("ventanas_temporales", 3)
        mlflow.log_param("variantes_comparadas", len(resumen))
        mlflow.log_metric("candidatos_comparados", len(resumen))
        for nombre in ("resumen_validacion", "metricas_por_ventana", "decision", "contrato_api"):
            mlflow.log_artifact(str(FUENTES[nombre]), artifact_path="linaje")
        for ruta in CODIGO_FUENTE:
            if not ruta.is_file():
                raise FileNotFoundError(f"Falta el código de linaje: {ruta}")
            mlflow.log_artifact(str(ruta), artifact_path="codigo_fuente")
        mlflow.log_artifact(str(Path(__file__).resolve()), artifact_path="reproduccion")

        for _, candidato in resumen.iterrows():
            variante = str(candidato["variante"])
            detalle = metricas[metricas["variante"].eq(variante)].sort_values("particion")
            if len(detalle) != 3:
                raise ValueError(f"La variante '{variante}' no tiene tres ventanas históricas.")
            es_campeona = variante == VARIANTE_CAMPEONA
            parametros = {
                "algoritmo": "Ridge",
                "variante": variante,
                "numero_entradas": int(candidato["entradas"]),
                "alpha": 100.0,
                "historia_objetivo": "no",
                "datos_nuevos": "no",
                "candidata_seleccionada": str(es_campeona).lower(),
            }
            with mlflow.start_run(
                run_name=f"candidato_{int(candidato['entradas'])}entradas_{str(candidato['variante']).replace(' ', '_')}",
                nested=True,
                tags={
                    "registro_id": ID_REGISTRO,
                    "tipo_registro": "validacion_historica",
                    "candidata_seleccionada": str(es_campeona).lower(),
                    "validacion_independiente": "false",
                },
            ) as run_candidato:
                mlflow.log_params(parametros)
                metricas_run = {
                    "mae_validacion_medio": float(candidato["MAE_medio"]),
                    "mae_validacion_peor_ventana": float(candidato["peor_MAE_diario"]),
                    "wape_validacion_agregado_pct": float(candidato["WAPE_agregado"]),
                    "cambio_mae_pct_vs_15_actuales": float(candidato["cambio_MAE_pct_vs15"]),
                    "rmse_validacion_medio": float(detalle["RMSE"].mean()),
                    "r2_validacion_medio": float(detalle["R2"].mean()),
                    "sesgo_validacion_medio": float(detalle["sesgo"].mean()),
                }
                for i, (_, ventana) in enumerate(detalle.iterrows(), start=1):
                    metricas_run[f"mae_validacion_{i}"] = float(ventana["MAE"])
                    metricas_run[f"rmse_validacion_{i}"] = float(ventana["RMSE"])
                mlflow.log_metrics(metricas_run)
                run_ids.append(run_candidato.info.run_id)

                if es_campeona:
                    campos = joblib.load(FUENTES["modelo_ajustado"])["columnas"]
                    firma = ModelSignature(
                        inputs=Schema([ColSpec(DataType.double, name=nombre) for nombre in campos]),
                        outputs=Schema([ColSpec(DataType.double)]),
                    )
                    mlflow.sklearn.log_model(
                        sk_model=modelo,
                        name="sensor_virtual",
                        registered_model_name=NOMBRE_MODELO,
                        signature=firma,
                        pip_requirements=[
                            f"mlflow=={mlflow.__version__}",
                            "numpy==2.2.3",
                            "pandas==3.0.3",
                            "scikit-learn==1.6.1",
                        ],
                        metadata={
                            "version_fuente": contrato["version"],
                            "estado": "candidato_historico_no_produccion",
                            "registro": "retrospectivo_sin_reentrenamiento",
                        },
                        skops_trusted_types=["numpy.dtype"],
                    )
                    mlflow.log_artifact(str(FUENTES["modelo_ajustado"]), artifact_path="fuente")
                    mlflow.log_artifact(str(FUENTES["contrato_api"]), artifact_path="contrato")
                    corridas_version = cliente.search_model_versions(f"name = '{NOMBRE_MODELO}'")
                    version = next(
                        (v for v in corridas_version if v.run_id == run_candidato.info.run_id),
                        None,
                    )
                    if version is None:
                        raise RuntimeError("MLflow no devolvió la versión registrada del Ridge.")
                    version_registrada = int(version.version)
                    cliente.set_model_version_tag(
                        NOMBRE_MODELO,
                        str(version_registrada),
                        "estado",
                        "candidato_historico_no_produccion",
                    )
                    cliente.update_model_version(
                        NOMBRE_MODELO,
                        str(version_registrada),
                        description=(
                            "Registro retrospectivo del Ridge de 17 entradas ajustado con cuatro días. "
                            "Validación histórica reutilizada; no hay evaluación independiente ni "
                            "monitoreo en producción."
                        ),
                    )

        cliente.set_tag(run_comparacion.info.run_id, "registro_finalizado", "true")

    resultado = {
        "estado": "registrado",
        "mlflow_version": mlflow.__version__,
        "tracking_uri": uri_db,
        "experiment_id": experimento_id,
        "run_comparacion": run_comparacion.info.run_id,
        "runs_candidatos": run_ids,
        "cantidad_runs_candidatos": len(run_ids),
        "modelo_registrado": NOMBRE_MODELO,
        "version_modelo": version_registrada,
        "registro_id": ID_REGISTRO,
        "fuentes_sha256": {nombre: _sha256(ruta) for nombre, ruta in FUENTES.items()},
        "datos_crudos_subidos": False,
    }
    (DIR_SALIDA / "registro.json").write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return resultado


def main() -> None:
    resultado = _registrar()
    print(json.dumps(resultado, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
