# Respuestas directas a la prueba técnica

Reúno aquí las respuestas de cada serie para leerlas sin rastrearlas entre README, notebooks y resultados. Las Series I y II tienen respuestas analíticas. La Serie III desarrolla sus cuatro incisos, con continuidad de precios parcialmente verificada, respuesta de oferta comparada entre Guatemala y cinco pares —World como contexto— y sin identificación causal. Las Series IV–V permanecen pendientes.

## Estado general

| Serie | Enfoque | Estado |
|---|---|---|
| I. Campo, variedades y renovación | Cuatro preguntas de Gerencia Agrícola respondidas con datos, modelos y límites. | Análisis completado. |
| II. Fábrica, caldera | Cinco preguntas respondidas con la serie de sensores externa del enunciado. | Análisis completado; para decisiones de planta se requieren comprobaciones adicionales. |
| III. Mercado, producción y precio | Países, pares, riesgo, pronósticos y relación de oferta/precio con rezagos. | Desarrollo analítico de cuatro incisos; continuidad parcialmente verificada y oferta contrastada entre Guatemala y cinco pares, sin efecto causal identificado. |
| IV. Modelo en producción | API, empaquetado Docker y pruebas de API. | Pendiente; no desarrollada. |
| V. Presentación ejecutiva | Síntesis para las gerencias y defensa del análisis. | Pendiente; no elaborada. |

## Serie I: campo, variedades y renovación

### 1. ¿Qué tres variedades ampliar y cuántas cosechas mantener?

Recomiendo **HoCP14-885, L01-299 y Ho12-615**, con rotaciones iniciales de **tres, cuatro y cuatro cosechas totales** respectivamente. Bajo el precio central de US$0.20 por libra, sus aportes parciales esperados son US$727.58, US$632.66 y US$629.21 por acre/año. No son utilidades netas completas: siguen los supuestos del ejercicio sobre costos, una cosecha por año, renovación inmediata, precios y ausencia de descuento.

La recomendación de Ho12-615 depende del ajuste ambiental aditivo; con promedios directos, L01-283 supera a Ho12-615. La sensibilidad de precio usa US$0.15, US$0.20 y US$0.25 por libra y mantiene las duraciones, pero los aportes cambian sustancialmente. La falta de una sexta cosecha no demuestra que se haya renovado la parcela: faltan identificador de parcela/cohorte y motivo de retiro. Las duraciones son recomendaciones iniciales en el horizonte cubierto, no un máximo económico probado.

El [remuestreo del ranking completo](certeza-ranking-serie-I.md), con 500 réplicas de años completos y cobertura recalculada, sitúa a L01-299 entre las tres primeras en 500/500. HoCP14-885 es elegible en 202/500 y queda primera en esas 202; su frecuencia total de 40.4 % refleja cobertura limitada, no aporte cero. Ho12-615 aparece en el top 3 en 419/500 (83.8 % total; 95.7 % cuando es elegible). Sin ajuste ambiental su frecuencia baja a 37.4 %, frente a 43.0 % de L01-283. Son frecuencias condicionadas al procedimiento y a doce años observados, no probabilidades de superioridad futura. El [notebook 21](../notebooks/21_certeza_ranking_serie1.ipynb) conserva elegibilidad, aportes, rangos y escenarios de precio por réplica.

HoCP09-804 merece evaluación como alternativa adicional: es elegible en 499/500 réplicas y entra en el top 3 en 271/500 (54.2 %), con aporte mediano de US$598.63/acre/año. De esas entradas, 264 ocurren cuando HoCP14-885 pierde cobertura; cuando esta última sí es elegible, HoCP09-804 solo entra en 7/202. Su frecuencia global supera a la de L01-283, pero describe sobre todo esa sustitución contingente y no una superioridad económica demostrada. L01-283 sigue siendo relevante por el contraste sin ajuste. El ensayo local debe resolver estas alternativas antes de ampliar superficie.

### 2. ¿Qué modelo estima azúcar por acre para planificar la siguiente zafra?

Comparo Ridge, árbol de decisión y bosque aleatorio, usando información histórica estrictamente anterior a la zafra. Ridge gana las dos validaciones temporales de selección: MAE medio de 2,405.64 lb/acre frente a 2,787.95 y 2,882.48. Reservo 2021 para evaluar la decisión: MAE 2,144.55 lb/acre, RMSE 2,770.97 y R² 0.25. Es una precisión moderada, útil para comparar y presupuestar con cautela; no para comprometer el rendimiento exacto de una parcela.

Las entradas incluyen variedad, localidad, etapa, corte planificado, año y promedios históricos por clon/localidad y clon/corte. No uso TCA ni TRS_TON de la cosecha pronosticada, porque revelarían el resultado. La validación muestra errores y sesgos distintos por zafra y localidad; en 2021 MAGNOLIA, etapa 5, el MAE es 3,498.54 lb/acre en 72 observaciones. El detalle recomienda reportar errores por ambiente y revisar sesgo antes de utilizar el pronóstico.

### 3. ¿Qué grupos de variedades aparecen y qué significan?

Agrupo **17 variedades elegibles** de etapa 5 según productividad de azúcar, TRS, conservación en segunda soca y variabilidad entre localidades/años. Dejo el resto listado aparte por cobertura insuficiente. Escojo dos perfiles por parsimonia e interpretación:

- **Perfil 1, cinco variedades:** menor productividad/conservación promedio y más variabilidad. Conviene revisar la continuidad de las socas variedad por variedad.
- **Perfil 2, doce variedades:** mayor productividad y conservación promedio, con menor variabilidad. Permite priorizar seguimiento de socas, pero no aplicar una regla uniforme de renovación.

Los grupos no son categorías naturales certificadas ni deciden por sí solos qué variedad renovar. Su composición cambia según cómo se representen los ambientes; conservo la cautela para casos individuales.

### 4. ¿Qué datos propios capturar y cómo diseñar ensayos?

Propongo seguir cada parcela desde plantía y durante las socas con identificador persistente de parcela, bloque y cohorte; ubicación/suelo, variedad y semilla; área útil y unidades; fechas y corte planeado/real; rendimiento pesado y protocolo de laboratorio; clima, lluvia, riego y manejo; costos desglosados; y motivos de retiro, resiembra, pérdida o renovación. Esto permitiría distinguir cosechas de una misma parcela, calcular costos reales y no confundir cero, faltante y abandono.

Como estructura inicial, evaluar las tres variedades recomendadas junto con la referencia operativa, en tres sitios y tres bloques comparables, con asignación aleatoria: **36 parcelas** ilustrativas. Seguir cada parcela por varias socas y dimensionar repeticiones con la variabilidad observada y una diferencia económicamente relevante. Para probar políticas de renovación, una segunda fase debe comparar parcelas asignadas a renovar después de dos, tres o cuatro cosechas en un horizonte común. Es una propuesta de diseño; no he ejecutado un ensayo de campo.

**Desarrollo completo:** [conclusiones de Serie I](conclusiones-serie-I.md), [recomendación económica](../notebooks/03_analisis_economico_serie1.ipynb), [modelo supervisado](../notebooks/04_modelo_supervisado_serie1.ipynb), [segmentación](../notebooks/05_segmentacion_variedades_serie1.ipynb). El diseño de captura y ensayos está desarrollado en las conclusiones de Serie I.

## Serie II: fábrica, caldera

El análisis usa cinco días de una caldera de carbón de otra instalación. **La interpretación prioritaria es una operación con compensación térmica y transitorios del conjunto proceso–control: conviene revisar primero coordinación térmica/atemperación; el contraste de aire a carga comparable no muestra una diferencia persistente.** Los balances y principios de control sí son transferibles a bagazo; consignas, márgenes y coeficientes corresponden a cada unidad. La [lectura física y decisiones por inciso](conclusiones-serie-II.md#interpretación-física-y-decisiones) reúne inferencias, alternativas y comprobaciones.

### 1. ¿Son confiables los treinta sensores y archivos?

La auditoría encontró **30 celdas faltantes** en la señal de agua de atemperación, concentradas en dos episodios; cinco señales, incluido el objetivo, repiten cada par de lecturas. Contrasto archivos, tiempos, repeticiones, rangos, faltantes y señales mantenidas. Conservo los datos originales y los extremos revisados: la evidencia disponible no alcanza para llamarlos errores instrumentales. Faltan rangos certificados, calibración, unidades y trazabilidad del sistema de adquisición para certificar la salud de cada instrumento.

**Conclusión operativa:** el archivo es utilizable para este análisis con faltantes y cadencias explícitas. No deben contarse los pares retenidos como información independiente nueva cada cinco segundos. Los extremos térmicos graduales y concordantes merecen revisión de proceso y control, en lugar de borrarse como picos aislados.

**Desarrollo:** [notebook 06](../notebooks/06_eda_caldera_serie2.ipynb), [revisión térmica del notebook 11](../notebooks/11_revision_extremos_termicos_serie2.ipynb).

### 2. ¿Qué regímenes de operación se distinguen?

K-means identifica **dos perfiles amplios** usando siete familias de señales. Uno ocupa 37.60 % del tiempo y presenta menor estado térmico/aire secundario; el otro ocupa 62.40 % y muestra medianas mayores en esas señales. Ambos reaparecen en los cinco bloques analizados, con solapamiento y mezcla temporal cambiante. Son perfiles exploratorios, no estados eficientes/ineficientes certificados ni fallas.

**Interpretación física:** el perfil con más caudal y gases más calientes también tiene mayores señales de válvula/agua, mientras la temperatura final es semejante: 537.44/537.88 °C. Es compatible con compensación de una salida regulada. Conviene comparar carga, estado térmico y señales de actuación conjuntamente; poca variación de la temperatura final no implica irrelevancia física de las otras variables. Son medianas agregadas, sin comparación a igual carga.

**Desarrollo:** [notebook 09](../notebooks/09_regimenes_operacion_serie2.ipynb), con pruebas de persistencia y sensibilidad.

### 3. ¿Qué variables y rezagos explican el caudal de vapor?

La campeona es **Ridge con diecisiete entradas procedentes de quince sensores**: sus quince mediciones actuales y las presiones `PTCA_8322A` y `PTCA_8324` medidas **30 segundos antes**. Estima el caudal actual con un **MAE medio de 0.3560 y WAPE agregado de 0.5981 %** en las tres validaciones temporales. La historia de esas dos presiones permite distinguir trayectorias recientes que las mediciones actuales no describen por completo.

La elijo por sus resultados y parsimonia: incorpora solo dos lecturas históricas y conserva la interpretación aditiva de Ridge. Ajusto selección, imputación y escalado dentro del entrenamiento, sin usar el propio caudal como entrada. Treinta segundos es el rezago elegido de la malla explorada; no demuestra un tiempo físico exacto. Las validaciones son históricas y reutilizadas; falta confirmación en un periodo nuevo y del linaje del caudal compensado y las latencias instrumentales.

**Uso recomendado:** estimador consultivo en paralelo y referencia de consistencia con el medidor, interpretando discrepancias junto con carga, estado térmico y adquisición. La memoria de presión tiene sentido como representación de dinámica del circuito; no se requiere identificar su mecanismo exacto para aprovechar la mejora histórica. El respaldo independiente ante falla del caudalímetro sigue condicionado al linaje de las señales.

**Desarrollo:** [informe y elección de la campeona](rezagos-serie-II.md), [notebook 12 con ajuste final](../notebooks/12_rezagos_serie2.ipynb), [comparación de algoritmos](../notebooks/07_sensor_virtual_serie2.ipynb) y [controles del procedimiento](../scripts/auditar_leakage_serie2.py). Artefacto vigente: `outputs/campeona_serie2/sensor_virtual.joblib`.

### 4. ¿Cómo detectar anomalías y proponer avisos al jefe de calderas?

Aplico Isolation Forest y lo complemento con reglas basadas en persistencia y desviaciones específicas de algunas señales. El análisis produjo 28 avisos multivariables; no son 28 fallas confirmadas. La regla de temperatura y las marcas robustas de corriente/retornos permiten revisar episodios que el detector general omite, pero todavía no puedo medir anticipación, precisión de fallas ni falsas alarmas reales porque no hay etiquetas de averías.

Para distinguir equipo, sensor y proceso, un aviso debe contrastarse con instrumentos independientes, señales de la misma familia, carga, mandos y bitácora/calibración. Una señal aislada no basta para atribuir causa. Las reglas son propuestas analíticas; requieren revisión y aprobación de operación antes de uso en planta.

**Inferencia y prioridad:** una excursión concordante de seis presiones favorece revisar cambio común de tiro/proceso o adquisición antes que seis averías independientes. El pico de corriente 51.28 coincide con aumentos de ambas vibraciones: merece revisar un transitorio electromecánico, sin diagnosticar daño. FT_8306A/B son aire de cámaras de retorno, no condensado. Combinar rareza multivariable con persistencia y reglas específicas cubre perspectivas distintas; un evento breve no se elimina por su duración.

**Desarrollo:** [notebook 10](../notebooks/10_anomalias_serie2.ipynb), episodios térmicos del [notebook 11](../notebooks/11_revision_extremos_termicos_serie2.ipynb).

### 5. ¿Qué dos oportunidades de mejora se identificaron?

1. **Revisar el suministro y reparto del aire de combustión según carga**, comparando aire primario/secundario, oxígeno, gases y presión/caudal en condiciones comparables. Aire suficiente favorece combustión completa; exceso de gases puede elevar pérdidas. Más aire secundario con oxígeno mediano algo menor en el perfil de más caudal no permite diagnosticar exceso de aire. **El contraste no forma parejas con el criterio principal; la sensibilidad predefinida forma 46 pares y no muestra una diferencia persistente de O2 o gases.** La acción es diseñar una prueba supervisada, no reducir aire por una correlación. Para valorar combustible/dinero faltan consumo y poder calorífico, CO/inquemados, calibración, temperatura real de chimenea y energía eléctrica.
2. **Revisar la estabilidad de temperatura y su coordinación con la atemperación.** El 8.14 % de lecturas está fuera de una banda bibliográfica, no de un límite de seguridad. Los cuatro episodios mayores son graduales y coherentes entre familias: la hipótesis de transitorios del proceso y regulación tiene más respaldo que picos aislados de temperatura. En los casos revisados, la evolución del agua y del estado térmico justifica reconstruir consigna → mando/posición → agua → temperatura local/final. Así se puede decidir si conviene mejorar coordinación o respuesta; no identifico aún un controlador defectuoso. Menor agua no equivale por sí sola a mayor eficiencia.

Priorizaría la revisión térmica con esos cuatro casos. El contraste de aire a carga semejante no muestra una diferencia persistente; para pasar de la exploración a una decisión operativa haría falta una prueba supervisada con las mediciones indicadas. El beneficio buscado es mayor estabilidad y mejor supervisión; su magnitud evitable y el ahorro energético requieren contraste operativo. Esta secuencia es una recomendación concreta, no un ajuste ni un ahorro ejecutados.

**Desarrollo:** [conclusiones de Serie II](conclusiones-serie-II.md), [contraste de combustión](combustion-carga-serie-II.md) y evidencia enlazada a los notebooks 06, 09, 10, 11 y 22.

## Serie III: mercado, producción mundial y precio

**Conclusión económica para gerencia:** Guatemala presenta una fortaleza de productividad territorial frente a sus referencias, en un mercado con riesgo de precio relevante y ajustes diferidos de oferta mundial. Recomiendo conservar esa base productiva, presupuestar escenarios adversos y evaluar crecimiento por margen esperado de varias zafras y costo de oportunidad. La teoría y los datos permiten recomendar esa disciplina sin haber identificado una elasticidad causal exacta. El [fundamento económico y las decisiones por inciso](conclusiones-serie-III.md#lectura-económica-y-decisiones) distinguen hallazgos, interpretación y supuestos.

### 1. ¿Qué perfiles aparecen, dónde está Guatemala y cuáles son sus pares?

La segmentación de **74 países/territorios** con cobertura histórica suficiente identifica dos perfiles amplios de menor y mayor escala/rendimiento. Guatemala está en el segundo, de 56 áreas, y tiene rendimiento mediano 2019–2023 de **107.52 t/ha**, segundo entre las áreas elegibles. Los perfiles se solapan y dependen de la representación: no son categorías de eficiencia certificada.

Una comparación separada por superficie, expansión y variabilidad —sin elegir por rendimiento— señala a **Indonesia, Bolivia y Vietnam como núcleo de pares estructurales** al variar los criterios manteniendo cinco vecinos. Nepal y Kenia son referencias secundarias que dependen de admitir diferencias amplias de superficie. Estos pares describen estructura territorial, sin equivalencia demostrada de agua, clima, suelo, capital o tecnología.

Frente a cinco referencias y en años coincidentes, la mediana del cociente de rendimiento de Guatemala es **1.679**: aproximadamente **67.9 % superior** a la mediana de sus pares. Al variar criterios con cinco referencias, queda entre 1.642 y 1.679; usar tres u ocho vecinos modifica la magnitud a 1.964 y 1.624. Es productividad de la tierra publicada, no ventaja comparativa económica ni eficiencia total de recursos.

La certeza está limitada por calidad y cobertura. El rendimiento de Guatemala de 2019–2021 es estimado y su superficie imputada; 2022–2023 tienen bandera oficial. El perfil de menor variabilidad incluye mayor proporción de estimaciones, que pueden suavizar trayectorias. Las 38 áreas sin cobertura suficiente permanecen fuera de la segmentación, conservadas con motivo. No elimino extremos ni flags E/I/X como errores automáticos. Guatemala también registra un descenso de rendimiento de 7.63 % entre 2022 y 2023, sin causa identificada.

**Decisión:** conservar la productividad de la base existente, revisar su descenso reciente y comparar mejoras de rendimiento con expansión por margen incremental y recursos. Usar los pares para estructurar ese contraste; el rendimiento alto por sí solo no determina la inversión rentable. **Desarrollo:** [conclusiones de Serie III](conclusiones-serie-III.md), [notebook 14](../notebooks/14_segmentacion_paises_serie3.ipynb) y [EDA del notebook 13](../notebooks/13_eda_faostat_serie3.ipynb).

### 2. ¿Qué volatilidad, regímenes y extremos muestra el precio? ¿Son movimientos reales?

La volatilidad histórica anualizada del azúcar No. 11 es **33.36 % observada y 31.10 % en la sensibilidad restringida**. Conservo las 6,097 filas originales; de 6,096 retornos, 5,748 se admiten en esa sensibilidad. Aparto los restantes con motivo por ventanas de posible enlace o por OHLC inconsistente/volumen cero en alguno de sus extremos, sin recalcular retornos sobre filas comprimidas ni declararlos errores demostrados.

Hay **11 inconsistencias OHLC, todas en fronteras mensuales compatibles con cambios de contrato**, y 93 volúmenes cero. La ficha declara Yahoo Finance como origen, pero no documenta contrato diario ni enlace/ajuste/cierre frente a liquidación. La verificación de movimientos reales es **parcial**: una caída de −11.63 % el 12-11-2010 tiene cotejo puntual de precios del mismo vencimiento en publicaciones contemporáneas; el rebote de +26.55 % del 01-05-2000 coincide con señales sospechosas y no lo presento íntegramente como variación económica del mismo contrato.

El [contraste de continuidad](continuidad-precios-serie-III.md) compara 291 meses completos con USDA ERS: la mediana de diferencia porcentual absoluta es 0.00543 %, pero 14 meses difieren más de 1 %. Junio de 2024 lo conservo separado por ser parcial. Tres cotizaciones publicadas para Mar-11 coinciden al centavo con el CSV; los cambios entre ellas son semanales. Las medias de 2008 son próximas a USDA, pero no identifican el contrato de cada salto diario. La evidencia refuerza niveles mensuales y cotejos puntuales; la continuidad contractual completa está pendiente. No ajusto ni sustituyo la serie. El [notebook 19](../notebooks/19_continuidad_precios_serie3.ipynb) y el [registro de fuentes](fuentes-continuidad-serie-III/indice.md) documentan el contraste y sus divergencias.

Los estados descriptivos de volatilidad móvil a 63 sesiones son baja hasta **24.35 %**, intermedia hasta **34.35 %** y alta por encima. Son cuartiles históricos, con proporciones determinadas por el criterio; no tres clases naturales ni una señal predictiva evaluada. Los años 2008, 2010 y 2011 conservan volatilidades restringidas de **44.85 %, 49.02 % y 40.17 %**. La clasificación depende de ventana y tratamiento de continuidad; reporto sensibilidad explícita.

**Decisión:** incorporar escenarios adversos de precio al presupuesto y revisar exposición de ventas frente a compromisos de costos. El riesgo persiste tras apartar observaciones sospechosas y justifica priorizar protección del margen. Fijar límites comerciales o evaluar una cobertura concreta requiere completar el linaje contractual. **Desarrollo:** [apartado 2 de conclusiones de Serie III](conclusiones-serie-III.md#2-volatilidad-regímenes-y-extremos-del-azúcar-no-11), [notebook 15](../notebooks/15_precios_azucar_serie3.ipynb) y [fuentes y alcance del contraste](fuentes-precios/indice.md).

### 3. ¿Qué pronóstico se obtiene a uno y tres meses y con qué incertidumbre?

Los modelos propuestos para estimar el promedio mensual son **Extra Trees a un mes y Ridge histórico a tres meses**, con bandas de incertidumbre. La comparación incluye **19 configuraciones**, cuatro familias aprendidas (Ridge, SVR, Extra Trees y boosting), autorregresión directa, deriva, suavizado y dos ingenuos, con conjuntos de hasta **24 variables** de historia, tendencia, volatilidad, calendario, OHLC y volumen. Solo usa los datos entregados. La propuesta es exploratoria: la elijo tras observar la evaluación; **no existe un test a ciegas reservado en esos datos**. La confirmación independiente está pendiente de datos realmente no utilizados.

En la evaluación desde 2019, el ingenuo obtiene **MAE 0.694 centavos de USD/libra y WAPE 3.95 % a un mes**, y **MAE 1.653 centavos y WAPE 9.31 % a tres meses**. Hay 64/62 emisiones evaluadas, con objetivos hasta mayo de 2024. Los errores cambian entre años; no son tasas futuras garantizadas. Los entrenamientos solo usan objetivos ya maduros en cada origen.

**Extra Trees aporta una mejora a un mes:** MAE **0.652** y WAPE **3.70 %**, una reducción de MAE de **6.12 %** frente al ingenuo. Mejora en cinco de los seis años objetivo representados, con 2024 parcial; empeora en 2022 y a tres meses. **Ridge histórico a tres meses obtiene MAE 1.630 y WAPE 9.18 %**, una mejora pequeña de MAE de 1.35 %, variable entre años. El ingenuo ganó la comparación de selección; conservo ese resultado como comparación y no lo reescribo para justificar la propuesta. Ambos modelos propuestos están entrenados y conservan bandas/pipelines reproducibles, sin acreditarse como ganadores de un test independiente.

Emito el último ejercicio **con información al cierre de mayo de 2024**, para junio/agosto; no es un pronóstico actual. Las 15 filas del junio parcial las conservo aparte y no las uso como promedio de mes completo.

| Horizonte/mes objetivo | Modelo propuesto | Punto | Banda nominal 80 % | Banda nominal 95 % |
|---|---|---:|---|---|
| +1, junio 2024 | Extra Trees | 18.25 | 16.98–19.61 | 15.91–20.93 |
| +3, agosto 2024 | Ridge histórico | 18.85 | 16.01–22.19 | 14.45–24.59 |

Todos los valores en centavos de USD/libra. Calibro las bandas de cada candidato con errores de 2014–2018 y las congelo antes de evaluar. En los modelos propuestos, la nominal 80 % cubrió 87.50 % a un mes y 85.48 % a tres; al 95 %, 96.88 % y 96.77 %. La elección posterior de esos candidatos limita la interpretación: no son garantías futuras ni una nueva evaluación independiente. El ingenuo permanece como baseline, punto histórico 18.30 a ambos horizontes y bandas propias en el notebook 16.

**Decisión:** proponer Extra Trees a un mes y Ridge histórico a tres como prototipos para escenarios, conservando la comparación con el ingenuo y la validación independiente como pendiente. Artefacto: `outputs/serie3_pronostico_ampliado/modelos_propuestos.joblib`; decisión y pronósticos en `decision_propuesta.json` y `pronosticos_propuestos.csv`. Evaluar exposición y margen propios; la aplicación a un contrato o precio físico exige su correspondencia y no estimo rentabilidad de cobertura. **Desarrollo:** [apartado 3 de conclusiones](conclusiones-serie-III.md#3-pronóstico-a-uno-y-tres-meses-con-incertidumbre), [referencias del notebook 16](../notebooks/16_pronostico_azucar_serie3.ipynb), [modelos propuestos del notebook 18](../notebooks/18_pronostico_ampliado_serie3.ipynb) y [módulo reproducible](../scripts/ampliar_pronostico_serie3.py).

### 4. ¿La superficie o producción responde al precio y con qué rezago?

**En el agregado mundial aparece una asociación positiva con el cambio de precio de dos años antes; en Guatemala la evidencia es débil.** Para 2004–2023, las correlaciones de crecimientos anuales a dos años son 0.718/0.776 en superficie/producción mundial, frente a 0.310/0.001 en Guatemala. La correlación de niveles de superficie de Guatemala es 0.845, pero no persiste con esa magnitud al comparar cambios: no basta para defender respuesta local.

Con diez evaluaciones temporales retrospectivas de 2014–2023, los dos rezagos de precio reducen el MAE mundial frente a media histórica de 2.241 a 1.874 en superficie y de 3.201 a 1.425 en producción (**16.36 % y 55.46 %**). Son puntos logarítmicos de error del crecimiento, no porcentajes del volumen ni ahorro. En Guatemala el mismo modelo empeora la referencia: 4.249 → 4.540 y 9.838 → 10.339. El contraste adicional con crecimiento propio y las sensibilidades no justifican una regla local de expansión.

**Dos años es una señal asociativa entre los rezagos examinados, no un tiempo físico ni una elasticidad causal demostrados.** Solo hay veinte ecuaciones anuales por ámbito; uso versiones finales de FAOSTAT y la disponibilidad histórica no está comprobada. El futuro puede anticipar cosechas y compartir causas con ellas; faltan calendario de decisiones, precio físico esperado/neto, costos, moneda, clima y variación exógena identificada. La continuidad contractual está parcialmente verificada.

La comparación de Guatemala con sus cinco pares estructurales utiliza los mismos veinte años, sin apilar países como réplicas independientes del precio común. **Viet Nam es el único país comparado que conserva positivos ambos rezagos para área y producción en los dos bloques y al omitir cualquier año.** En retrospectiva, el modelo propia+precio reduce MAE frente a media histórica en Viet Nam 32.3 % para área y 26.6 % para producción; empeora en los otros cinco países. Esto describe heterogeneidad entre pares, sin probar diferencias causales. [Comparación entre países](oferta-paises-serie-III.md) y [notebook 20](../notebooks/20_oferta_paises_serie3.ipynb).

**Interpretación y decisión:** los datos respaldan parcialmente el mecanismo económico de oferta que se ajusta con retraso a los incentivos. Conviene evaluar expansión con márgenes de varias zafras e incluir respuesta futura de competidores, sin extrapolar indefinidamente un repunte de precio. Para Guatemala, falta de señal local estable no equivale a ausencia de incentivos; el margen recibido y las restricciones pueden diferir del futuro internacional. Los coeficientes mundiales no fijan superficie óptima ni beneficio local. **Desarrollo:** [apartado 4 de conclusiones](conclusiones-serie-III.md#4-respuesta-de-superficie-y-producción-al-precio), [notebook 17](../notebooks/17_oferta_precio_serie3.ipynb) y [método reproducible](../scripts/analizar_oferta_serie3.py).

## Series IV y V: pendientes

- **Serie IV, producción:** pendiente la API para exponer un modelo, con validación de entradas, OpenAPI, Docker Compose y pruebas. La prueba condiciona estos entregables a que se desarrolle la serie.
- **Serie V, presentación:** pendiente la presentación ejecutiva de 15–20 minutos para las tres gerencias y la demostración de API, solo si se desarrolla la Serie IV.

Concentro las respuestas disponibles en este documento. Los informes temáticos y notebooks contienen el detalle técnico, las limitaciones y la reproducción de sus resultados.
