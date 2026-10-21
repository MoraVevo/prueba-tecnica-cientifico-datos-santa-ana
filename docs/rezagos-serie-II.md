# Serie II, inciso 3: señales anteriores que explican el caudal actual

La síntesis del resto de respuestas de la prueba está en [respuestas directas a todas las series](respuestas-prueba.md).

## Qué encontré y qué decisión propongo

Sí hay información temporal útil: la historia de las presiones `PTCA_8322A` y `PTCA_8324`, treinta segundos antes, mejora la estimación del caudal actual en las tres ventanas históricas. La campeona conserva las quince señales actuales de cada entrenamiento y añade esas dos lecturas anteriores: **diecisiete entradas procedentes de quince sensores**, sin usar caudal pasado.

**Modelo seleccionado:** Ridge con diecisiete entradas, ajustado con los primeros cuatro días. Su artefacto es `outputs/campeona_serie2/sensor_virtual.joblib`. MAE de validación 0.356026 y WAPE agregado 0.598068 %. Las validaciones reutilizadas describen desempeño histórico, sin confirmación independiente ni identificación de un tiempo físico exacto.

## Pregunta y diseño

El inciso 3 pide identificar variables y rezagos explicativos. Hasta este estudio se había comparado el valor actual de las señales; un buen resultado contemporáneo no demostraba que el pasado fuera irrelevante.

Trabajo sobre la misma fase de diez segundos del modelo original, porque el objetivo repite cada pareja de lecturas de cinco segundos. El significado de un rezago positivo es **X(t−k) para estimar caudal(t)**. No se utilizan caudal pasado, entradas futuras, interpolación hacia atrás ni ventanas centradas.

La malla prefijada es 0, 10, 30, 60, 120, 300 y 600 segundos. Es una exploración acotada por criterio práctico, no un rango físico certificado; no resuelve retrasos menores de diez segundos ni mayores de diez minutos. En cada entrenamiento se calculan correlaciones de niveles y de cambios hacia atrás de diez/sesenta segundos. Los niveles pueden compartir movimientos lentos; por eso la selección de candidatos usa los cambios de diez segundos. Para cada sensor se elige el rezago positivo con mayor correlación absoluta, únicamente en entrenamiento. El cero se conserva como referencia: elegir un candidato positivo no demuestra que supere al valor actual ni que su asociación sea significativa.

Se mantienen las tres particiones originales: un día de entrenamiento para el siguiente, dos para el tercero y tres para el cuarto, con separación de cinco minutos. El quinto día queda fuera. Las quince variables de cada ventana son las ya seleccionadas mediante RFE en su entrenamiento original; no son una lista final seleccionada con días posteriores. El selector pudo usar las primeras lecturas de su propio entrenamiento, lo que es temporalmente admisible.

Todos los modelos comparados usan exactamente las mismas filas: se retiran del ajuste los primeros 660 segundos para disponer de 600 segundos de historia y 60 de diferencia. Quedan 8,544/17,184/25,824 lecturas de entrenamiento y 8,640 de evaluación por ventana. Medianas y escalas se ajustan solo en entrenamiento; Ridge mantiene alpha=100. El control contemporáneo se vuelve a ajustar sobre esas mismas filas.

La historia de una entrada de validación puede proceder del intervalo de separación o de lecturas anteriores de la propia validación. Es información de sensores que ya estaría disponible al estimar el caudal actual. No se alimenta con objetivos de validación ni se afirma anticipar el caudal futuro. La separación no necesita prohibir esas lecturas pasadas para este uso contemporáneo; la latencia instrumental real sigue pendiente de confirmar.

## Qué rezagos tienen respaldo y cuáles son débiles

Las dos presiones seleccionan **30 segundos en los tres entrenamientos crecientes**. Con el rezago del primer día congelado, las correlaciones entre cambios de la presión anterior y cambios del caudal en cada día posterior son:

| Señal anterior | Día 2 | Día 3 | Día 4 |
|---|---:|---:|---:|
| PTCA_8322A, 30 s antes | +0.150 | +0.128 | +0.133 |
| PTCA_8324, 30 s antes | +0.212 | +0.175 | +0.176 |

Son asociaciones moderadas o pequeñas, pero con signo repetido y utilidad conjunta en Ridge. La correlación marginal no equivale a importancia condicional. En particular, PTCA_8324 tiene en el primer entrenamiento correlación contemporánea de cambios −0.299 y a 30 s +0.188: no corresponde afirmar que su valor retrasado es la relación absoluta más fuerte entre todas las alternativas.

La escala de medición importa. Al comparar cambios de sesenta segundos en el primer entrenamiento, el mayor |r| positivo aparece a 30 s para PTCA_8322A y a 60 s para PTCA_8324. Por eso interpreto la zona de decenas de segundos como evidencia temporal; **30 s es el candidato de la malla bajo una regla concreta**, sin precisión física demostrada.

Hay otros candidatos repetidos: temperatura de aire secundario a 120 s, temperatura del hogar a 30 s y presión diferencial ZCLCCY a 60 s. Su repetición no basta para declararlos dinámicas identificadas: sus asociaciones de cambios con el caudal son débiles, algunas cambian de signo en los días siguientes, y la historia conjunta de los otros trece sensores casi no mejora el error. Aire, oxígeno, agua y varias presiones muestran candidatos cambiantes; no adjudico un tiempo de respuesta confiable a cada señal solo porque el algoritmo siempre devuelva un máximo.

Las ventanas de entrenamiento se solapan; tres selecciones coincidentes no son tres experimentos independientes. Las correlaciones de los días siguientes usan observaciones distintas, aunque autocorrelacionadas. No se calculan valores p ni se presentan las 25,920 lecturas como réplicas independientes.

## ¿La historia mejora el sensor virtual?

La comparación incluye modelos con señales actuales y con rezagos, además de contrastes que separan la historia de las dos presiones dominantes de la de los otros trece sensores. Es un análisis exploratorio con validaciones reutilizadas; no equivale a confirmación independiente.

| Variante | Entradas | MAE medio | WAPE agregado | Cambio MAE frente al control de quince |
|---|---:|---:|---:|---:|
| Quince señales actuales, control comparable | 15 | 0.457744 | 0.768939 % | Referencia |
| Quince actuales + historia de las dos presiones | 17 | **0.356026** | **0.598068 %** | **−22.22 %** |
| Quince actuales + historia de los otros trece | 28 | 0.455611 | 0.765356 % | −0.47 % |
| Quince actuales + un rezago de cada una | 30 | 0.352814 | 0.592672 % | −22.92 % |
| Veintinueve actuales | 29 | 0.462198 | 0.776422 % | +0.97 % |
| Veintinueve actuales + un rezago de cada una | 58 | 0.358308 | 0.601902 % | −21.72 % |

WAPE es suma de errores absolutos dividida por suma de caudales absolutos, por cien. El cambio relativo del MAE no es una reducción de puntos porcentuales de WAPE. La referencia original de quince, sin retirar el inicio, se reproduce por separado: MAE 0.457279 y WAPE 0.768159 %. La pequeña diferencia del control nuevo se debe a las filas de ajuste comunes, ambas cifras corresponden al control contemporáneo de la comparación.

| Ventana | MAE control de quince | MAE con las dos presiones anteriores | WAPE con las dos anteriores |
|---|---:|---:|---:|
| Día 2 | 0.515565 | 0.400635 | 0.666973 % |
| Día 3 | 0.486150 | 0.377115 | 0.634154 % |
| Día 4 | 0.371517 | 0.290328 | 0.491640 % |

El resultado mejora los tres días y 71 de los 72 bloques horarios, sin suponer que sean independientes. En el bloque restante el MAE aumenta 0.007022 unidades. Se guardan errores pareados por hora para localizar ese empeoramiento. Añadir los otros trece rezagos aporta poco en conjunto y empeora el primer día; los datos no justifican ampliar indiscriminadamente la memoria.

La variante de diecisiete queda a aproximadamente 0.91 % del menor MAE de las seis comparaciones, con peor día ligeramente mejor que la de treinta. Satisface las tolerancias de parsimonia de 1 % en MAE y 5 % en peor día, por lo que es el modelo seleccionado.

## Interpretación física y límites

El Ridge contemporáneo ya utiliza las dos presiones con signos opuestos. Incorporar sus valores anteriores permite distinguir situaciones con valores actuales similares pero trayectorias recientes diferentes. El modelo obtiene información del estado y de su evolución sin necesitar el objetivo como entrada. Es una interpretación de la estructura predictiva, no una intervención causal.

No se identifica si el patrón procede de dinámica del proceso, regulación, compensación, filtrado o diferencias de actualización del DCS. Faltan fórmula y linaje del caudal compensado, ubicación/unidades instrumentales y latencias por tag. Una buena predicción con señales de la misma cadena tampoco garantiza que la campeona funcione cuando falle el medidor principal. No interpreto estas asociaciones como prueba de exceso de aire, eficiencia energética o ahorros.

La certeza es moderada para utilidad predictiva histórica y baja para atribuir un tiempo físico o garantizar generalización. La campeona de diecisiete debe contrastarse congelada en un periodo nuevo, verificando instrumentación. Requiere treinta segundos de historia de dos señales y confirmar cómo manejar interrupciones y disponibilidad. El ajuste final usa 34,464 filas entre 2022-03-27 14:39:54 y 2022-03-31 14:23:44, con mismas quince señales actuales de la selección original y dos rezagos fijos; no se usa el quinto día. El ajuste y sus exclusiones se exportan mediante `scripts/entrenar_campeona_serie2.py`.

## Uso operativo razonado

Presión y evolución reciente son indicadores físicamente plausibles de la dinámica entre generación, demanda y regulación. La mejora histórica respalda conservar las dos lecturas anteriores, aunque treinta segundos sea una escala empírica y no un retardo físico identificado. Recomiendo utilizar primero la campeona como estimador consultivo en paralelo: su discrepancia con el medidor puede orientar revisión junto con carga, estado térmico y calidad de adquisición. Esa propuesta tiene utilidad antes de certificar respaldo independiente; no declara disponibilidad frente a fallas compartidas ni convierte el residuo en alarma de avería. La [interpretación física integrada](conclusiones-serie-II.md#interpretación-física-y-decisiones) amplía fundamento y prioridades.

## Trazabilidad y reproducción

El crudo conserva sus 86,400 filas. El estudio usa 34,494 como elegibles; las 51,906 fuera se conservan en archivo separado con todas las mediciones y motivo: 34,560 de segunda fase dentro de los cuatro días, 17,280 del quinto día y 66 sin historia común. Son exclusiones del experimento, sin declaración de invalidez. La separación temporal y los papeles por pliegue se registran aparte; las cinco señales duplicadas no se cuentan como nueva información de cinco segundos.

Ejecutar [notebook 12](../notebooks/12_rezagos_serie2.ipynb) después del 07:

```powershell
python -m nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=600 notebooks/12_rezagos_serie2.ipynb
python -m pytest tests/unitarias/test_rezagos.py tests/integracion/test_rezagos_resultados.py -q
```

La preparación está en [experimentos/rezagos_serie2.py](../experimentos/rezagos_serie2.py). Tablas, predicciones, papeles por fila, gráficos y huellas quedan en `outputs/rezagos/`, ignorado por Git. Las comprobaciones reconstruyen correlaciones con NumPy, historia por timestamps exactos y las dieciocho predicciones por la ecuación matricial de Ridge; incluyen orientación del rezago e invariancia de su selección ante alteraciones futuras. Las huellas protegen fuente, notebook/módulo y salidas originales del sensor virtual.

Con este análisis queda respondido el pendiente de rezagos del inciso 3, con sus límites. La confirmación instrumental y la validación externa siguen pendientes para uso en planta.
