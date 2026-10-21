# Registro retrospectivo con MLflow

Este extra organiza en MLflow evidencia ya producida para la selección del sensor virtual de Serie II. No reentrena el modelo ni incorpora datos de entrenamiento. Se registran una corrida de comparación y seis corridas de candidatos, junto con las métricas por ventana, los archivos de linaje y el Ridge ajustado que ya usaba la API.

## Resultado registrado

La variante elegida usa 15 señales actuales y la historia de las dos presiones (17 entradas), con Ridge y `alpha=100`. En las tres validaciones temporales históricas obtuvo MAE medio de **0.356 lb/acre**, WAPE agregado de **0.598068%** (0.60%) y MAE de **0.400635 lb/acre** en su peor ventana. WAPE se expresa como porcentaje: el cálculo es `100 × suma(error absoluto) / suma(observado absoluto)`. La elección es retrospectiva y comparativa; no representa una evaluación independiente ni el desempeño de producción.

El registro ejecutado con MLflow 3.17.1 contiene **7 corridas** (1 padre y 6 candidatas) en un experimento SQLite y **1 versión** del modelo `serie2_sensor_virtual_ridge_17`. La versión se marca `candidato_historico_no_produccion`. Se volvió a ejecutar el registro y el script informó `ya_registrado`, conservando el mismo conteo y la versión 1. La carga de `models:/serie2_sensor_virtual_ridge_17/1` produjo 59.33003888712712 para un vector de prueba determinista basado en medianas del imputador, igual al modelo ajustado de origen. Esta comprobación valida carga e identidad de predicción en ese vector, no la calidad predictiva general.

El modelo fuente es un `joblib` con un pipeline ya ajustado y sus 17 nombres de columna; no contiene filas de entrenamiento. Su SHA-256 coincide con el contrato de la API. Los CSV incluidos en `mlflow/fuentes/` contienen únicamente el resumen de comparación (6 filas) y las métricas agregadas por ventana (18 filas), no observaciones crudas.

## Reconstruir el registro local

Desde la raíz del proyecto, con Python 3.10 o posterior:

```powershell
python -m venv .venv-mlflow
.\.venv-mlflow\Scripts\Activate.ps1
python -m pip install -r requirements-mlflow.txt
python scripts/registrar_mlflow_serie2.py
```

El script valida hashes, configuración, entradas, seis variantes y tres ventanas por candidata antes de registrar. La base SQLite y sus artefactos se escriben bajo `outputs/mlflow_entrega_validada/`, que está ignorada por Git. Para inspeccionar el registro se puede iniciar la interfaz local:

```powershell
mlflow ui --backend-store-uri sqlite:///outputs/mlflow_entrega_validada/mlflow.db --host 127.0.0.1 --port 5000
```

La base contiene rutas absolutas del equipo en sus ubicaciones de artefactos; por eso no se distribuye y no debe suponerse que funcionará tras moverla a otra ruta. Al ejecutar el script en otro equipo se reconstruye una base nueva a partir de los archivos versionables de `mlflow/fuentes/` y del código de linaje incluido en el proyecto.

## Límites y siguiente comprobación

El Registry conserva una versión histórica candidata; no se promovió a producción ni se implementó despliegue. Tampoco hay monitoreo automático. Como siguiente comprobación operativa, cuando existan predicciones con resultado observado, se pueden calcular MAE, WAPE y sesgo por turno o día, y revisar cobertura y rangos de las 17 entradas. Los umbrales y la respuesta ante alertas requieren definición del proceso; este registro no los fija.
