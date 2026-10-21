# Bitácora de decisiones y verificación

Registro de decisiones técnicas, supuestos e hipótesis descartadas. La cronología detallada del trabajo vive en Git; esta bitácora conserva las decisiones que afectan la lectura de los resultados.

## 2026-10-19 — Fuente y unidad de Serie I

- **Unidad de `T_SPACRE`.** Adopté libras de azúcar por acre, definición de la ficha USDA-ARS, en lugar de toneladas por acre como indica el PDF. La decisión hace compatible el precio de US$0.20/lb del ejercicio. `TCA` queda en toneladas de caña por acre y `TRS_TON` en libras de azúcar por tonelada de caña.
- **Procedencia.** El CSV oficial y la copia Kaggle son idénticos byte por byte; el descargador valida SHA-256. Conservo el archivo fuente intacto.
- **Prefijo de `TRS_TON`.** Conservo completas las celdas con dos componentes en `TRS_TON_raw`; el prefijo queda como texto sin interpretar y el componente numérico final en `TRS_TON`. No encontré documentación que defina el prefijo y no lo uso como variable agronómica.
- **Copias exactas.** Excluí 126 copias adicionales del conjunto analítico y las conservé en un archivo con motivo por fila. El ETL pasa de 29,529 registros de origen a 29,403 analíticos. Mantengo 224 filas en 112 grupos de clave repetida con mediciones distintas y 23 alertas dimensionales; no las promedio ni las elimino sin evidencia.

## 2026-10-19 — Serie I: renovación, ranking y modelo

- **Aporte económico.** Comparo el aporte esperado de políticas de renovación con una cosecha por año, renovación inmediata, costos constantes y sin descuento ni descanso. No es utilidad neta ni flujo observado de una misma parcela. La renovación se carga una vez por rotación y se divide por su duración.
- **Políticas iniciales.** HoCP14-885 a tres cosechas, L01-299 y Ho12-615 a cuatro. A US$0.20/lb, los aportes parciales son US$727.58, US$632.66 y US$629.21 por acre/año. El tercer puesto depende del ajuste ambiental aditivo: con promedios directos, L01-283 supera a Ho12-615. No hay máximo económico de renovación demostrado.
- **Ranking completo.** Uso 500 réplicas de años completos y recalculo cobertura, política y top 3. L01-299 aparece en 500/500; HoCP14-885 es elegible en 202/500 y primera en esas réplicas; Ho12-615 entra en 419/500; HoCP09-804 entra en 271/500, de las cuales 264 ocurren cuando falta HoCP14-885. Son frecuencias condicionadas al procedimiento y a doce años, no probabilidades de superioridad futura.
- **Modelo supervisado.** Ridge, árbol y bosque con validación temporal 2019–2020 y evaluación reservada 2021. Ridge obtiene MAE 2,144.55 lb/acre y R² 0.25 en 2021. El error es moderado y variable por ambiente; en MAGNOLIA/etapa 5, el MAE y el sesgo positivo son 3,498.54 lb/acre con 72 observaciones. No afirmo causalidad ni precisión parcelaria.
- **Segmentación.** Dos perfiles de 5 y 12 variedades, elegidos por interpretación y parsimonia. La conservación entre cortes es un proxy de longevidad, sin cohorte; los grupos no son clases naturales. La propuesta de captura y ensayos está diseñada, no ejecutada.

## 2026-10-20 — Serie II: campeona, regímenes y anomalías

- **Campeona.** Ridge con diecisiete entradas de quince sensores: quince señales actuales y las presiones PTCA_8322A/PTCA_8324 treinta segundos antes. MAE 0.356026 y WAPE 0.598068 % en tres validaciones históricas. El ajuste usa 34,464 filas de los primeros cuatro días, con recorte inicial común de 660 segundos y separación final de cinco minutos. No evalúo el quinto día para esta versión.
- **Límites de la campeona.** Las validaciones son reutilizadas y el linaje del caudal compensado, las unidades y las latencias no están confirmados. El pipeline recibe las diecisiete columnas históricas ya preparadas; no construye la memoria por sí mismo. Los resultados son evidencia histórica exploratoria, no una garantía ante falla del caudalímetro.
- **Regímenes.** K-means con dieciséis sensores en once dimensiones y dos perfiles que ocupan 37.60 % y 62.40 % del tiempo. Describen estados térmicos y de aire; no certifican eficiencia ni modos oficiales.
- **Anomalías.** Isolation Forest con 200 árboles y reglas de persistencia. Genera 28 avisos multivariables, dos interrupciones de datos y 85 avisos térmicos. El complemento de corriente y retornos produce 384 tramos de marcas y dos avisos sostenidos; 372 tramos corresponden a una sola lectura. Sin etiquetas de avería no estimo precisión, falsas alarmas reales ni anticipación.
- **Revisión térmica.** Conservo cuatro episodios y 696 filas con marca; no excluyo por rareza ni por superar un umbral. La prioridad operativa es revisar la coordinación térmica/atemperación con consigna, modo, posición real de válvula y temperaturas locales.

## 2026-10-20 — II.5: combustión a carga semejante

- **Diseño fijado antes de ver O2/gases.** Bloques no solapados de cinco minutos, terciles diarios de aire secundario y emparejamiento 1:1 por vapor y presión del mismo día. El criterio principal usa rango intrabloque ≤1.0 y caliper 0.20; la sensibilidad predefinida usa rango ≤2.0 y caliper 0.20. No uso O2 ni gases para definir la exposición.
- **Resultado principal.** De 1,440 bloques, 65 cumplen estabilidad y cobertura; 46 quedan sin pareja y 19 corresponden al tercil medio. El criterio principal produce **cero pares**. La sensibilidad de 2.0/0.20 produce 46 pares en seis fechas de calendario, con 92 bloques y 5,520 filas fuente. El caliper 0.25 produce 59 pares.
- **Lectura.** Las diferencias medianas de O2 y gases tienen rangos intercuartílicos que cruzan cero y signos mixtos. No sostienen una diferencia persistente, exceso de aire, ajuste óptimo ni ahorro. El resultado principal no prueba buen o mal funcionamiento; solo indica que no hay comparación controlada bajo el criterio estricto.
- **Conservación.** Las 86,400 filas y los 1,440 bloques quedan clasificados con motivo. En la sensibilidad, 5,520 filas están en bloques pareados y 80,880 quedan fuera con campos crudos, IDs y motivos. No elimino ni imputo lecturas.
- **Siguiente prueba.** Un ajuste requeriría combustible y poder calorífico, CO e inquemados, temperatura real de chimenea y energía eléctrica. El contraste no autoriza reducir aire ni fijar un oxígeno objetivo.

## 2026-10-20 — Serie III: países, precios, pronóstico y oferta

- **Países y pares.** FAOSTAT conserva 27,648 celdas anuales de caña y 144 áreas. La segmentación usa 112 países/territorios y 21,168 celdas en 1961–2023; 38 áreas quedan fuera con 7,182 celdas y motivos. Elijo 74 áreas elegibles y dos perfiles de 18 y 56. Guatemala pertenece al perfil de mayor escala/rendimiento, con 107.5206 t/ha de rendimiento reciente mediano, segunda entre las 74 elegibles. Los pares se eligen solo por nivel, tendencia y variabilidad de superficie: Indonesia, Bolivia, Nepal, Kenia y Vietnam. El cociente de productividad es 1.679. No llamo ventaja comparativa económica a la productividad territorial ni infiero igualdad de recursos.
- **Precios y continuidad.** `Sugar_data.csv` tiene 6,097 filas OHLCV entre 2000-03-01 y 2024-06-24, sin faltantes ni fechas duplicadas; conserva 93 volúmenes cero y 11 inconsistencias OHLC. La volatilidad anualizada es 33.36 % observada y 31.10 % restringida. El contraste con USDA ERS cubre 291 meses completos: mediana de diferencia porcentual absoluta 0.00543 %, con 14 meses por encima de 1 %. Tres cotizaciones de Mar-11 coinciden al centavo. No certifico contrato diario, liquidación ni regla de enlace; no fabrico un ajuste de roll.
- **Pronóstico.** La comparación usa 19 configuraciones con hasta 24 rasgos OHLCV/históricos. La propuesta de entrega usa Extra Trees a un mes y Ridge histórico a tres meses. Extra Trees reduce el MAE de evaluación de 0.694164 a 0.651709 (6.12 %) y el WAPE de 3.945331 % a 3.704038 %. Ridge histórico reduce el MAE a tres meses de 1.652727 a 1.630385 (1.35 %). El ingenuo del último cierre gana la comparación de selección y permanece como baseline. La elección es exploratoria porque la evaluación no es un periodo ciego; no hay test ciego reservado.
- **Oferta.** Guatemala y cinco pares estructurales comparten veinte años (2004–2023), con ecuaciones separadas; World queda como contexto. Viet Nam conserva la señal positiva más estable de los dos rezagos. En la retrospectiva propia+precio, mejora frente a la media en ese país y empeora en los otros cinco. El contraste describe heterogeneidad; no identifica causalidad ni un plazo agrícola exacto. FAOSTAT usa versiones finales y no acredita fechas de publicación históricas.

## 2026-10-21 — Serie IV: API y empaquetado

- **Modelo expuesto.** Expongo la campeona Ridge de Serie II, no la de Serie I. El artefacto `models/serie2_sensor_virtual.json` contiene 17 entradas, coeficientes, medias, escalas, medianas, rangos, percentiles, métricas y el SHA-256 del `joblib`. La inferencia es Python puro; la API no carga scikit-learn ni los datos crudos.
- **Contrato de entrada.** La API recibe las 17 columnas ya preparadas, incluidas las dos presiones treinta segundos antes. No calcula el rezago, no imputa y no acepta faltantes: una solicitud incompleta devuelve 422. Los rangos son mínimo/máximo observados, no límites de seguridad. La mediana de `YJJWSLL.AV_0#` se publica para trazabilidad, pero no se aplica en tiempo de ejecución.
- **Endpoints.** `GET /health`, `GET /model`, `POST /predict`, Swagger en `/docs` y OpenAPI en `/openapi.json`. La respuesta incluye modelo, versión, objetivo, unidad no certificada y advertencia. No invento intervalos de incertidumbre.
- **Dependencias y pruebas.** Fijo FastAPI 0.156.4, Pydantic 2.14.1 y Uvicorn 0.54.0 en `requirements-api.txt`; pytest 8.4.2 y httpx2 2.15.1 en `requirements-dev.txt`. Las 13 pruebas de API y las 4 de integración comparan la ecuación JSON con el pipeline original, incluidas las 15 filas imputadas. La API también pasa en un entorno virtual limpio con solo `requirements-api.txt`, pytest y httpx2.
- **Docker.** Incluyo `Dockerfile`, `docker-compose.yml` y `.dockerignore`. La imagen usa solo `requirements-api.txt`, copia `api/` y `models/`, ejecuta sin privilegios y define un `HEALTHCHECK`. La sintaxis YAML se validó. Revisé que `python:3.13-slim` incluye `useradd` y `chown`, que las dependencias tienen ruedas Linux cp313 y que una copia aislada con solo `api/`, `models/` y `requirements-api.txt` responde `/health`, `/docs`, `/model` y `/predict`. **No ejecuté `docker compose up --build`** porque este equipo no tiene Docker CLI ni distribución WSL instalada; la verificación de extremo a extremo queda pendiente en una máquina con Docker.
- **Alcance.** La Serie IV es opcional según el PDF. La presento como demostración técnica con contrato, pruebas y empaquetado, no como certificación de producción, independencia instrumental o uso en control automático.

## 2026-10-20 — Criterio editorial

- **Resultados actuales.** README, conclusiones e informes describen el resultado actual, el método, la evidencia y los límites. Son documentos de resultado, no de incidencias.
- **Primera persona.** El texto expositivo usa primera persona singular para las decisiones y acciones del autor. Evito la voz impersonal cuando oculta quién decide.
- **Bitácora.** Conserva decisiones, supuestos e hipótesis descartadas. No es un mapa cronológico de trabajo; para eso está Git.
- **Estado interno.** `docs/estado.md` es una instantánea operativa, no una acumulación de secciones fechadas. Las notas internas permanecen locales e ignoradas por Git.

## 2026-10-20 — Verificación

- La suite completa contiene 124 pruebas: 57 unitarias, 54 de integración y 13 de API. La ejecución completa aprueba las 124.
- La comprobación de enlaces locales no encuentra destinos faltantes.
- El notebook 22 tiene 11 celdas, 6 de código y ejecución sin errores.
- Las pruebas verifican implementación, conservación y trazabilidad; no certifican instrumentación, continuidad contractual, causalidad ni generalización futura.
- Actualicé las huellas protegidas de los notebooks 07, 09 y 10 después de cambios exclusivamente markdown; código, ejecución y outputs no cambiaron.
- Git: rama `main`; el historial local incluye las unidades de Serie I–IV y se publica en `origin/main` como parte de esta entrega. El PDF confidencial, los datasets, `outputs/` y las notas internas quedan fuera de Git. El estado exacto de HEAD se consulta con `git log -1`.

## Hipótesis descartadas

- Que el criterio principal de II.5 demostrara buen o mal funcionamiento: no; solo muestra ausencia de parejas comparables bajo ese estándar.
- Que la continuidad mensual con USDA ERS certificara los saltos diarios y la serie completa: no; faltan contrato, liquidación y regla de enlace.
- Que las frecuencias del ranking completo fueran probabilidades de superioridad futura: no; están condicionadas al procedimiento y a doce años.
- Que el ajuste de aire a carga semejante produjera un ahorro demostrado: no; el contraste es descriptivo y no estima combustible ni dinero.
- Que el pronóstico ampliado tuviera un test ciego reservado: no; la evaluación ya estaba observada y la confirmación requiere datos no utilizados.
- Que la productividad territorial de Guatemala probara ventaja comparativa o eficiencia económica: no; la fuente no contiene costos de oportunidad, agua, suelo, trabajo ni capital.

## Uso de IA

Contrasté los resultados con los datos crudos, las salidas reproducibles y las pruebas automatizadas. Mantengo las decisiones y los límites aunque contradigan una lectura más favorable. No acepté afirmaciones de causalidad, ahorro, continuidad certificada, test ciego o superioridad futura que no estuvieran respaldadas por la evidencia. Las auditorías editoriales con apoyo de IA detectaron narración de proceso y afirmaciones vencidas; las cifras se verificaron contra los artefactos del proyecto.

## Registro retrospectivo de experimentos

- Registré la comparación existente de seis variantes de Serie II en MLflow 3.17.1, con una corrida padre y una por candidata. No reentrené ni usé filas crudas nuevas; los resultados importados corresponden a tres validaciones temporales ya calculadas.
- La campeona histórica conserva 17 entradas y Ridge `alpha=100`; su MAE medio es 0.356 lb/acre, WAPE 0.598068% y peor MAE de ventana 0.400635 lb/acre. WAPE está expresado como porcentaje en `modelado_serie2.py` (multiplica por 100), por eso se comunica como 0.60%, no como 59.8%.
- MLflow primero dejó corridas en el experimento predeterminado porque el script no seleccionaba el experimento creado. Corregí esa selección y validé una base limpia con SQLite: 7 corridas asociadas al experimento previsto y una versión Registry. Repetí el script; reconoció `ya_registrado` y conservó esos conteos. También cargué la versión y confirmé igualdad de predicción con el pipeline fuente para un vector determinista.
- El primer intento de registrar el pipeline con `skops` rechazó `numpy.dtype`; restringí la lista confiable a ese tipo concreto y la carga posterior funcionó. El registro es una candidata histórica, no despliegue ni promoción.
- El backend y las rutas de artefactos son absolutos del equipo. No distribuyo la base SQLite; incluyo inputs tabulares resumidos, el pipeline ajustado sin filas de entrenamiento, el contrato y el script para reconstruirla. No implementé monitoreo; documenté solo comprobaciones futuras condicionadas a que existan predicciones con resultado observado.
- `requirements-mlflow.txt` queda separado de `requirements-api.txt`. `pip check` informó que no hay dependencias rotas. `pytest.ini` limita `python -m pytest -q` a `tests/unitarias` y `tests/api`: aprobó 85 pruebas (57 unitarias y 28 API). Las pruebas de integración no están en esa configuración; `python -m pytest tests/integracion/test_api_modelo_serie2.py -q` aprobó las 4 pruebas de integración dirigidas.

## Interfaz local de Serie IV

- Añadí `/app`, una descarga de plantilla de 17 encabezados y carga CSV/JSON de una sola fila. Elegí no presentar un formulario de 17 números: los sensores y rezagos requieren contexto temporal, y la plantilla con solo encabezados evita inventar mediciones. La API sigue siendo la validación fuente final.
- El botón de escenario usa las medianas de ajuste y muestra `59.3300388871` como salida sintética, no como observación validada. La pantalla declara unidad no certificada y que la estimación consultiva no diagnostica fallas ni demuestra ahorros.
- Confirmé que la lista de entradas del modelo no contiene el objetivo `ZZQBCHLL.AV_0#` ni su lag. Las dos entradas `PTCA` históricas requieren historia de 30 s preparada por el cliente; la API no crea el rezago ni verifica timestamps. Correlaciones de señales de proceso no prueban por sí solas fuga, pero la disponibilidad y el linaje instrumental siguen sin confirmarse.
- Las pruebas API (28) cubren predicción y carga por HTTP, plantilla, CSV/JSON, una sola fila, errores de estructura y rechazo de null/NaN/infinito y valores fuera de rango. Las 4 integraciones comparan la ecuación exportada con el pipeline ajustado. La interfaz real respondió y el escenario sintético se observó en navegador; la carga de archivo se comprobó por HTTP, pero no por selector automatizado debido al bloqueo de acceso a archivos de la extensión CUA, sin cambiar permisos.
- Docker no se ejecutó. El intento posterior de instalar `requirements-api.txt` en un venv externo falló por DNS del índice; la validación de API procede del entorno del proyecto y no se presenta como instalación limpia.
