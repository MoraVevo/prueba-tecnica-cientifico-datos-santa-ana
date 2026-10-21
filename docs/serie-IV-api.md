# Serie IV: API del sensor virtual de Serie II

## Alcance

La prueba técnica señala la Serie IV como opcional. La desarrollo como extensión de la Serie II para mostrar cómo se expone un modelo ya ajustado, con contrato de entrada, validación, documentación OpenAPI, empaquetado y pruebas. No la presento como certificación de producción ni como validación nueva del modelo.

El modelo expuesto es la campeona Ridge de Serie II: estima `ZZQBCHLL.AV_0#` a partir de quince señales actuales y las presiones `PTCA_8322A` y `PTCA_8324` treinta segundos antes. La API recibe las diecisiete columnas ya preparadas. No construye el rezago ni imputa faltantes en tiempo de ejecución.

## Artefacto del modelo

`models/serie2_sensor_virtual.json` contiene los parámetros necesarios para reproducir la ecuación:

```text
prediccion = intercepto + suma(coeficiente_estandarizado * (x - media_escalado) / escala)
```

El archivo conserva:

- las diecisiete entradas, su nombre original, nombre de campo, descripción y unidad no certificada;
- mediana de imputación, media y escala del ajuste;
- coeficiente estandarizado, mínimo, máximo, percentiles 1 y 99 observados y número de faltantes por entrada;
- intercepto, `alpha`, objetivo y ecuación;
- procedencia del ajuste: 34,464 filas, del 2022-03-27 14:39:54 al 2022-03-31 14:23:44;
- 15 faltantes imputados, todos en `YJJWSLL.AV_0#`;
- métricas históricas de validación y límites;
- SHA-256 del `sensor_virtual.joblib` original.

El JSON se genera con:

```powershell
.\.venv\Scripts\python.exe -m scripts.exportar_modelo_serie2
```

La API no necesita `scikit-learn`, `joblib`, `pandas` ni los datos crudos. Solo carga el JSON y aplica la ecuación en Python puro. El exportador verifica que la ecuación reconstruya las predicciones del pipeline original, incluidas las filas con faltantes imputados.

## Entradas

La API exige exactamente las diecisiete columnas del ajuste. Los rangos son el mínimo y el máximo observados en entrenamiento; no son límites de seguridad, de instrumentación ni de operación.

| Entrada original | Campo Python | Mínimo | Máximo | Mediana |
|---|---|---:|---:|---:|
| `PT_8313C.AV_0#` | `presion_8313c` | -509.12 | 92.03 | -149.67 |
| `PT_8313D.AV_0#` | `presion_8313d` | -501.23 | 201.14 | -114.76 |
| `PT_8313F.AV_0#` | `presion_8313f` | -561.82 | 148.68 | -153.36 |
| `PTCA_8322A.AV_0#` | `presion_ptca_8322a` | 9.42 | 10.09 | 9.77 |
| `PTCA_8324.AV_0#` | `presion_ptca_8324` | 9.06 | 9.77 | 9.45 |
| `TE_8313B.AV_0#` | `temperatura_8313b` | 737.77 | 803.37 | 773.515 |
| `TE_8304.AV_0#` | `temperatura_8304` | 214.05 | 233.16 | 221.59 |
| `TV_8329ZC.AV_0#` | `valvula_8329zc` | 1.64 | 35.48 | 16.11 |
| `FT_8302.AV_0#` | `flujo_aire_8302` | 11446.04 | 28074.45 | 19493.99 |
| `AIR_8301A.AV_0#` | `oxigeno_8301a` | 0.81 | 4.54 | 2.04 |
| `AIR_8301B.AV_0#` | `oxigeno_8301b` | 0.80 | 5.04 | 2.19 |
| `YFJ3_AI.AV_0#` | `corriente_yfj3_ai` | 16.81 | 51.27 | 22.60 |
| `SXLTCYY.AV_0#` | `diferencial_sxltcyy` | -707.31 | -25.51 | -369.51 |
| `ZCLCCY.AV_0#` | `diferencial_zclccy` | 8897.17 | 11819.51 | 10495.275 |
| `YJJWSLL.AV_0#` | `agua_yjjwsll` | 1.60 | 4.30 | 2.75 |
| `PTCA_8322A.AV_0#__pasado_30s` | `presion_ptca_8322a_30s` | 9.42 | 10.09 | 9.77 |
| `PTCA_8324.AV_0#__pasado_30s` | `presion_ptca_8324_30s` | 9.06 | 9.77 | 9.45 |

El cliente debe calcular las dos presiones anteriores con su propia lógica temporal. La API no interpreta tiempos, no consulta una base de datos y no reconstruye la historia. Si el cliente envía una lectura actual en el campo del rezago, la API no puede detectarlo; la validación es de contrato, no de física.

La API tampoco imputa. Aunque el ajuste usó la mediana para 15 filas de `YJJWSLL.AV_0#`, una solicitud con un campo faltante devuelve 422. Esa decisión evita que una ausencia se convierta en una medición silenciosa. La mediana se publica en `/model` para trazabilidad, no para completar solicitudes.

## Endpoints

| Método | Ruta | Uso |
|---|---|---|
| `GET` | `/health` | Comprueba que el proceso está vivo y el modelo cargado. |
| `GET` | `/model` | Devuelve ficha, entradas, coeficientes, métricas, hash y límites. |
| `GET` | `/template.csv` | Descarga una fila de encabezados originales, sin valores de ejemplo. |
| `POST` | `/predict` | Estima el caudal con las diecisiete entradas. |
| `GET` | `/app` | Interfaz local para probar un escenario sintético o cargar un archivo. |
| `POST` | `/predict/file` | Recibe un CSV de una fila o un objeto JSON y aplica el mismo modelo. |
| `GET` | `/docs` | Documentación interactiva Swagger UI. |
| `GET` | `/openapi.json` | Contrato OpenAPI 3.1. |

`POST /predict` devuelve la estimación puntual, el identificador y versión del modelo, el objetivo, la unidad no certificada y una advertencia. No devuelve intervalos de incertidumbre porque el ejercicio no los validó.

Una solicitud con las medianas del ajuste produce:

```json
{
  "prediccion": 59.33003888712712,
  "modelo": "serie2_sensor_virtual_ridge_17",
  "version": "1.0.0",
  "objetivo": "ZZQBCHLL.AV_0#",
  "unidad": "unidad nativa de ZZQBCHLL.AV_0# (no certificada)",
  "advertencia": "Estimación histórica consultiva; no certifica unidad, independencia instrumental ni uso para control automático."
}
```

La validación rechaza con 422:

- una entrada faltante;
- una entrada extra;
- una cadena, un booleano, `null`, `NaN` o infinito;
- un valor fuera del mínimo o máximo observado.

Acepta enteros y números decimales dentro de rango. El esquema no impone `strict=True` para no rechazar un `-150` entero cuando el modelo espera un número real.

## Interfaz de escenarios

Al iniciar la API, abre `http://127.0.0.1:8000/app`. La página obtiene la ficha desde `/model` y consume `/predict` o `/predict/file`; no necesita instalar un framework de frontend ni guarda los archivos cargados. Los archivos se procesan en memoria y el límite de carga es 100 KB.

La interfaz ofrece dos caminos:

- **Escenario sintético:** envía las medianas del ajuste a `/predict`. Está rotulado como sintético; no es una lectura real ni una recomendación operativa.
- **Archivo preparado:** permite descargar una plantilla CSV desde `/template.csv` con los 17 encabezados exactos (incluidos `#` y el sufijo de rezago), o cargar CSV/JSON. La plantilla no trae números inventados. El CSV debe contener exactamente una fila de datos; el JSON debe ser un solo objeto. Los campos ausentes, extra, duplicados, no numéricos, no finitos o fuera de rango se rechazan. No se descartan filas adicionales silenciosamente.

La API predice `ZZQBCHLL.AV_0#` a partir de quince señales actuales y dos presiones de treinta segundos antes. Ninguna entrada es el objetivo ni una derivación del objetivo, por lo que la solicitud no requiere conocer previamente el caudal que se estima. Las correlaciones entre señales del mismo proceso son esperables; eso no demuestra independencia instrumental ni descarta una fuga por disponibilidad temporal. El archivo necesita que el sistema que lo prepara aporte las dos presiones históricas. La API no calcula rezagos ni verifica timestamps.

La pantalla muestra la predicción en unidad nativa no certificada, el modelo usado y el mínimo/máximo observados de cada entrada, junto con los valores cargados. Esos rangos son barreras empíricas: pueden rechazar una condición futura operacionalmente válida que quede fuera de la muestra de ajuste, y no son límites de seguridad. También pueden aceptar combinaciones dentro de rango que sean físicamente imposibles.

La predicción sirve para contrastar consultivamente el flujo cuando las señales requeridas están disponibles; por sí sola no diagnostica fallas de equipo o sensor, no establece una causa ni cuantifica ahorro de combustible. Conviene revisar la calidad e independencia de las entradas y comparar con una medición confiable antes de interpretar el resultado. El ajuste y validación son históricos, la validación no es independiente y el quinto día no se evaluó.

## Ejecución local

Con el entorno del proyecto:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-api.txt
.\.venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

También se puede crear un entorno solo para la API:

```powershell
python -m venv .venv-api
.\.venv-api\Scripts\python.exe -m pip install -r requirements-api.txt
.\.venv-api\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Comprobación:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/model
```

Ejemplo de predicción con PowerShell:

```powershell
$cuerpo = @{
  'PT_8313C.AV_0#' = -149.67
  'PT_8313D.AV_0#' = -114.76
  'PT_8313F.AV_0#' = -153.36
  'PTCA_8322A.AV_0#' = 9.77
  'PTCA_8324.AV_0#' = 9.45
  'TE_8313B.AV_0#' = 773.515
  'TE_8304.AV_0#' = 221.59
  'TV_8329ZC.AV_0#' = 16.11
  'FT_8302.AV_0#' = 19493.99
  'AIR_8301A.AV_0#' = 2.04
  'AIR_8301B.AV_0#' = 2.19
  'YFJ3_AI.AV_0#' = 22.60
  'SXLTCYY.AV_0#' = -369.51
  'ZCLCCY.AV_0#' = 10495.275
  'YJJWSLL.AV_0#' = 2.75
  'PTCA_8322A.AV_0#__pasado_30s' = 9.77
  'PTCA_8324.AV_0#__pasado_30s' = 9.45
} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/predict -ContentType 'application/json' -Body $cuerpo
```

## Docker Compose

El repositorio incluye `Dockerfile`, `docker-compose.yml` y `.dockerignore`. La imagen instala solo `requirements-api.txt`, copia `api/` y `models/`, ejecuta como usuario sin privilegios y define un `HEALTHCHECK` contra `/health`.

```powershell
docker compose up --build
```

Después:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Start-Process http://127.0.0.1:8000/docs
```

Para detener:

```powershell
docker compose down
```

**Validación local.** Revisé el `Dockerfile`, el Compose y el contexto de build. La imagen base `python:3.13-slim` incluye `useradd` y `chown`; el contenedor instala solo `requirements-api.txt`. La API se ejecutó con el entorno del proyecto; las 28 pruebas verifican rutas y contrato, y el servidor local respondió correctamente en `/health` y `/app`. Intenté instalar `requirements-api.txt` en un venv externo, pero la resolución de paquetes falló por DNS al índice configurado; por tanto, no afirmo un arranque verificado desde una instalación limpia.

**Verificación pendiente.** En este equipo no hay Docker CLI ni una distribución WSL instalada, por lo que no ejecuté `docker compose up --build`. La construcción y el arranque del contenedor deben comprobarse en una máquina con Docker antes de presentar la Serie IV como verificada de extremo a extremo.

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest tests\api -q
.\.venv\Scripts\python.exe -m pytest tests\integracion\test_api_modelo_serie2.py -q
```

Las 28 pruebas de API cubren salud, ficha, plantilla, interfaz servida por HTTP, predicción válida, reproducibilidad, límites, entradas faltantes/extra, tipos incorrectos, booleanos, nulos, valores no finitos y fuera de rango, OpenAPI, Swagger y fallo al cargar un modelo inválido. La prueba de integración reconstruye el ajuste desde el CSV y compara la ecuación JSON con el pipeline `joblib` en 500 filas completas y en las 15 filas imputadas. Con `pytest.ini`, `python -m pytest -q` ejecuta y aprueba 85 pruebas (57 unitarias y 28 de API). Además ejecuté y aprobé las 4 pruebas de integración del modelo; no ejecuté el resto de `tests/integracion` en esta revisión.

La suite de API también verifica que `/app` se sirva por HTTP, que `/template.csv` descargue exactamente los 17 nombres originales, que un CSV con esos encabezados y un objeto JSON produzcan la misma respuesta de `/predict`, que se rechacen columnas faltantes/extra y más de una fila, y que nulos, NaN e infinitos devuelvan 422 serializable. La prueba HTTP confirma el contrato de página, archivo y endpoint; la inspección visual de la interfaz en navegador es una comprobación aparte.

## Límites

- La validación del modelo es histórica y reutilizada; no es un test independiente. El quinto día no se evaluó en la promoción de esta versión.
- La unidad del caudal objetivo y de las entradas no está certificada. La API publica esa limitación en cada respuesta.
- El linaje del caudal compensado, la fórmula de compensación y las latencias instrumentales no están confirmados.
- La API no demuestra independencia instrumental ni funcionamiento ante falla del caudalímetro.
- Los rangos de entrada son empíricos. Un valor dentro de rango puede ser físicamente inválido.
- No hay intervalos de incertidumbre, autenticación, límites de tasa, registro de auditoría ni integración con un sistema de planta.
- El servicio es una demostración técnica. No debe usarse para control automático, alarmas de seguridad ni decisiones contractuales.
- La verificación de Docker Compose queda pendiente en un entorno con Docker.
