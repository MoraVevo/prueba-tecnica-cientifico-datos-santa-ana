# Respuestas directas a la prueba técnica

Este es el punto de entrada para leer las respuestas de cada serie sin rastrearlas entre README, notebooks y resultados. Las Series I y II tienen respuestas analíticas. La Serie III tiene respuestas a sus cuatro incisos, con verificación parcial de continuidad de precios y sin identificación causal de oferta. Las Series IV–V permanecen pendientes.

## Estado general

| Serie | Enfoque | Estado |
|---|---|---|
| I. Campo, variedades y renovación | Cuatro peticiones a Gerencia Agrícola respondidas con datos, modelos y límites. | Análisis completado. |
| II. Fábrica, caldera | Cinco peticiones respondidas con la serie de sensores externa del enunciado. | Análisis completado; para decisiones de planta se requieren comprobaciones adicionales. |
| III. Mercado, producción y precio | Países, pares, riesgo, pronósticos y relación de oferta/precio con rezagos. | Cuatro incisos respondidos como análisis, con continuidad parcialmente verificada y sin efecto causal identificado. |
| IV. Modelo en producción | API, empaquetado Docker y pruebas de API. | Pendiente; no desarrollada. |
| V. Presentación ejecutiva | Síntesis para las gerencias y defensa del análisis. | Pendiente; no elaborada. |

## Serie I: campo, variedades y renovación

### 1. ¿Qué tres variedades ampliar y cuántas cosechas mantener?

Recomiendo **HoCP14-885, L01-299 y Ho12-615**, con rotaciones iniciales de **tres, cuatro y cuatro cosechas totales** respectivamente. Bajo el precio central de US$0.20 por libra, sus aportes parciales esperados son US$727.58, US$632.66 y US$629.21 por acre/año. No son utilidades netas completas: siguen los supuestos del ejercicio sobre costos, una cosecha por año, renovación inmediata, precios y ausencia de descuento.

La recomendación de Ho12-615 depende del ajuste ambiental aditivo; con promedios directos, L01-283 supera a Ho12-615. La sensibilidad de precio usa US$0.15, US$0.20 y US$0.25 por libra y mantiene las duraciones, pero los aportes cambian sustancialmente. La falta de una sexta cosecha no demuestra que se haya renovado la parcela: faltan identificador de parcela/cohorte y motivo de retiro. Las duraciones son recomendaciones iniciales en el horizonte cubierto, no un máximo económico probado.

### 2. ¿Qué modelo estima azúcar por acre para planificar la siguiente zafra?

Se compararon Ridge, árbol de decisión y bosque aleatorio, usando información histórica estrictamente anterior a la zafra. Ridge ganó las dos validaciones temporales de selección: MAE medio de 2,405.64 lb/acre frente a 2,787.95 y 2,882.48. Se reservó 2021 para evaluar la decisión: MAE 2,144.55 lb/acre, RMSE 2,770.97 y R² 0.25. Es una precisión moderada, útil para comparar y presupuestar con cautela; no para comprometer el rendimiento exacto de una parcela.

Las entradas incluyen variedad, localidad, etapa, corte planificado, año y promedios históricos por clon/localidad y clon/corte. No se usan TCA ni TRS_TON de la cosecha pronosticada, porque revelarían el resultado. La validación muestra errores y sesgos distintos por zafra y localidad; en 2021 MAGNOLIA, etapa 5, el MAE es 3,498.54 lb/acre en 72 observaciones. El detalle recomienda reportar errores por ambiente y revisar sesgo antes de utilizar el pronóstico.

### 3. ¿Qué grupos de variedades aparecen y qué significan?

Se segmentaron **17 variedades elegibles** de etapa 5 según productividad de azúcar, TRS, conservación en segunda soca y variabilidad entre localidades/años. El resto quedó listado aparte por cobertura insuficiente. Se escogieron dos perfiles por parsimonia e interpretación:

- **Perfil 1, cinco variedades:** menor productividad/conservación promedio y más variabilidad. Conviene revisar la continuidad de las socas variedad por variedad.
- **Perfil 2, doce variedades:** mayor productividad y conservación promedio, con menor variabilidad. Permite priorizar seguimiento de socas, pero no aplicar una regla uniforme de renovación.

Los grupos no son categorías naturales certificadas ni deciden por sí solos qué variedad renovar. Su composición cambia según cómo se representen los ambientes; se conserva la cautela para casos individuales.

### 4. ¿Qué datos propios capturar y cómo diseñar ensayos?

Propongo seguir cada parcela desde plantía y durante las socas con identificador persistente de parcela, bloque y cohorte; ubicación/suelo, variedad y semilla; área útil y unidades; fechas y corte planeado/real; rendimiento pesado y protocolo de laboratorio; clima, lluvia, riego y manejo; costos desglosados; y motivos de retiro, resiembra, pérdida o renovación. Esto permitiría distinguir cosechas de una misma parcela, calcular costos reales y no confundir cero, faltante y abandono.

Como estructura inicial, evaluar las tres variedades recomendadas junto con la referencia operativa, en tres sitios y tres bloques comparables, con asignación aleatoria: **36 parcelas** ilustrativas. Seguir cada parcela por varias socas y dimensionar repeticiones con la variabilidad observada y una diferencia económicamente relevante. Para probar políticas de renovación, una segunda fase debe comparar parcelas asignadas a renovar después de dos, tres o cuatro cosechas en un horizonte común. Es una propuesta de diseño; no se ha ejecutado un ensayo de campo.

**Desarrollo completo:** [conclusiones de Serie I](conclusiones-serie-I.md), [recomendación económica](../notebooks/03_analisis_economico_serie1.ipynb), [modelo supervisado](../notebooks/04_modelo_supervisado_serie1.ipynb), [segmentación](../notebooks/05_segmentacion_variedades_serie1.ipynb). El diseño de captura y ensayos está desarrollado en las conclusiones de Serie I.

## Serie II: fábrica, caldera

El análisis usa cinco días de una caldera de carbón de otra instalación. Las relaciones describen el archivo y no se transfieren sin validación a una caldera de bagazo de Santa Ana.

### 1. ¿Son confiables los treinta sensores y archivos?

La auditoría encontró **30 celdas faltantes** en la señal de agua de atemperación, concentradas en dos episodios; cinco señales, incluido el objetivo, repiten cada par de lecturas. Se contrastaron archivos, tiempos, repeticiones, rangos, faltantes y señales mantenidas. Se conservaron los datos originales y los extremos revisados: la evidencia disponible no alcanzó para llamarlos errores instrumentales. Faltan rangos certificados, calibración, unidades y trazabilidad del sistema de adquisición para certificar la salud de cada instrumento.

**Desarrollo:** [notebook 06](../notebooks/06_eda_caldera_serie2.ipynb), [revisión térmica del notebook 11](../notebooks/11_revision_extremos_termicos_serie2.ipynb).

### 2. ¿Qué regímenes de operación se distinguen?

K-means identifica **dos perfiles amplios** usando siete familias de señales. Uno ocupa 37.60 % del tiempo y presenta menor estado térmico/aire secundario; el otro ocupa 62.40 % y muestra medianas mayores en esas señales. Ambos reaparecen en los cinco bloques analizados, con solapamiento y mezcla temporal cambiante. Son perfiles exploratorios, no estados eficientes/ineficientes certificados ni fallas.

**Desarrollo:** [notebook 09](../notebooks/09_regimenes_operacion_serie2.ipynb), con pruebas de persistencia y sensibilidad.

### 3. ¿Qué variables y rezagos explican el caudal de vapor?

La campeona es **Ridge con diecisiete entradas procedentes de quince sensores**: sus quince mediciones actuales y las presiones `PTCA_8322A` y `PTCA_8324` medidas **30 segundos antes**. Estima el caudal actual con un **MAE medio de 0.3560 y WAPE agregado de 0.5981 %** en las tres validaciones temporales. La historia de esas dos presiones permite distinguir trayectorias recientes que las mediciones actuales no describen por completo.

Se eligió por sus resultados y parsimonia: incorpora solo dos lecturas históricas y conserva la interpretación aditiva de Ridge. Selección, imputación y escalado se ajustan dentro del entrenamiento, sin usar el propio caudal como entrada. Treinta segundos es el rezago elegido de la malla explorada; no demuestra un tiempo físico exacto. Las validaciones son históricas y reutilizadas; falta confirmación en un periodo nuevo y del linaje del caudal compensado y las latencias instrumentales.

**Desarrollo:** [informe y elección de la campeona](rezagos-serie-II.md), [notebook 12 con ajuste final](../notebooks/12_rezagos_serie2.ipynb), [comparación de algoritmos](../notebooks/07_sensor_virtual_serie2.ipynb) y [controles del procedimiento](../scripts/auditar_leakage_serie2.py). Artefacto vigente: `outputs/campeona_serie2/sensor_virtual.joblib`.

### 4. ¿Cómo detectar anomalías y proponer avisos al jefe de calderas?

Se aplicó Isolation Forest, complementado con reglas basadas en persistencia y desviaciones específicas de algunas señales. El análisis produjo 28 avisos multivariables; no son 28 fallas confirmadas. La regla de temperatura y las marcas robustas de corriente/retornos permiten revisar episodios que el detector general omite, pero todavía no se ha medido anticipación, precisión de fallas ni falsas alarmas reales porque no hay etiquetas de averías.

Para distinguir equipo, sensor y proceso, un aviso debe contrastarse con instrumentos independientes, señales de la misma familia, carga, mandos y bitácora/calibración. Una señal aislada no basta para atribuir causa. Las reglas son propuestas analíticas; requieren revisión y aprobación de operación antes de uso en planta.

**Desarrollo:** [notebook 10](../notebooks/10_anomalias_serie2.ipynb), episodios térmicos del [notebook 11](../notebooks/11_revision_extremos_termicos_serie2.ipynb).

### 5. ¿Qué dos oportunidades de mejora se identificaron?

1. **Revisar el suministro y reparto del aire de combustión según carga**, comparando aire primario/secundario, oxígeno, gases y presión/caudal en condiciones comparables. El fundamento físico es claro; el archivo no demuestra exceso de aire, ineficiencia ni ahorro. Para estimar impacto faltan consumo y poder calorífico del combustible, CO/inquemados, calibración, temperatura real de chimenea y energía eléctrica.
2. **Revisar la estabilidad de temperatura y su coordinación con la atemperación.** El 8.14 % de lecturas está fuera de una banda bibliográfica de referencia, no de un límite de seguridad. Se revisaron los cuatro episodios que contienen las desviaciones mayores; no se demostró error de sensor ni causa del control. Para estimar impacto hacen falta consigna/bandas autorizadas, modo de control, posición real de válvula, medidas locales y restricciones de turbina/proceso.

Priorizaría la revisión térmica por contar con episodios directos y magnitud observada. Ninguna de las oportunidades se presenta como ahorro demostrado ni como cambio de consignas ya ejecutado.

**Desarrollo:** [conclusiones de Serie II](conclusiones-serie-II.md), con evidencia enlazada a los notebooks 06, 09, 10 y 11.

## Serie III: mercado, producción mundial y precio

### 1. ¿Qué perfiles aparecen, dónde está Guatemala y cuáles son sus pares?

La segmentación de **74 países/territorios** con cobertura histórica suficiente identifica dos perfiles amplios de menor y mayor escala/rendimiento. Guatemala está en el segundo, de 56 áreas, y tiene rendimiento mediano 2019–2023 de **107.52 t/ha**, segundo entre las áreas elegibles. Los perfiles se solapan y dependen de la representación: no son categorías de eficiencia certificada.

Una comparación separada por superficie, expansión y variabilidad —sin elegir por rendimiento— señala a **Indonesia, Bolivia y Vietnam como núcleo de pares estructurales** al variar los criterios manteniendo cinco vecinos. Nepal y Kenia son referencias secundarias que dependen de admitir diferencias amplias de superficie. Estos pares describen estructura territorial, sin equivalencia demostrada de agua, clima, suelo, capital o tecnología.

Frente a cinco referencias y en años coincidentes, la mediana del cociente de rendimiento de Guatemala es **1.679**: aproximadamente **67.9 % superior** a la mediana de sus pares. Al variar criterios con cinco referencias, queda entre 1.642 y 1.679; usar tres u ocho vecinos modifica la magnitud a 1.964 y 1.624. Es productividad de la tierra publicada, no ventaja comparativa económica ni eficiencia total de recursos.

La certeza está limitada por calidad y cobertura. El rendimiento de Guatemala de 2019–2021 es estimado y su superficie imputada; 2022–2023 tienen bandera oficial. El perfil de menor variabilidad incluye mayor proporción de estimaciones, que pueden suavizar trayectorias. Las 38 áreas sin cobertura suficiente permanecen fuera de la segmentación, conservadas con motivo. No se eliminan extremos o flags E/I/X como errores automáticos. Guatemala también registra un descenso de rendimiento de 7.63 % entre 2022 y 2023, sin causa identificada.

**Decisión:** usar el núcleo de pares para orientar contraste agronómico y captura de recursos/costos; la comparación no justifica copiar prácticas, prometer aumentos de producción o asignar inversión. **Desarrollo:** [conclusiones de Serie III](conclusiones-serie-III.md), [notebook 14](../notebooks/14_segmentacion_paises_serie3.ipynb) y [EDA del notebook 13](../notebooks/13_eda_faostat_serie3.ipynb).

### 2. ¿Qué volatilidad, regímenes y extremos muestra el precio? ¿Son movimientos reales?

La volatilidad histórica anualizada del azúcar No. 11 es **33.36 % observada y 31.10 % en la sensibilidad restringida**. Se conservan las 6,097 filas originales; de 6,096 retornos, 5,748 se admiten en esa sensibilidad. Los restantes se apartan con motivo por ventanas de posible enlace o por OHLC inconsistente/volumen cero en alguno de sus extremos, sin recalcular retornos sobre filas comprimidas ni declararlos errores demostrados.

Hay **11 inconsistencias OHLC, todas en fronteras mensuales compatibles con cambios de contrato**, y 93 volúmenes cero. La ficha declara Yahoo Finance como origen, pero no documenta contrato diario ni enlace/ajuste/cierre frente a liquidación. La verificación de movimientos reales es **parcial**: una caída de −11.63 % el 12-11-2010 tiene cotejo puntual de precios del mismo vencimiento en publicaciones contemporáneas; el rebote de +26.55 % del 01-05-2000 coincide con señales sospechosas y no se presenta íntegramente como variación económica del mismo contrato.

Los estados descriptivos de volatilidad móvil a 63 sesiones son baja hasta **24.35 %**, intermedia hasta **34.35 %** y alta por encima. Son cuartiles históricos, con proporciones determinadas por el criterio; no tres clases naturales ni una señal predictiva evaluada. Los años 2008, 2010 y 2011 conservan volatilidades restringidas de **44.85 %, 49.02 % y 40.17 %**. La clasificación depende de ventana y tratamiento de continuidad; se reporta sensibilidad explícita.

**Decisión:** usar esta historia para describir riesgo y escenarios, completando el linaje por contrato antes de calibrar límites comerciales o evaluar coberturas. La sensibilidad no es una serie certificada. **Desarrollo:** [apartado 2 de conclusiones de Serie III](conclusiones-serie-III.md#2-volatilidad-regímenes-y-extremos-del-azúcar-no-11), [notebook 15](../notebooks/15_precios_azucar_serie3.ipynb) y [fuentes y alcance del contraste](fuentes-precios/indice.md).

### 3. ¿Qué pronóstico se obtiene a uno y tres meses y con qué incertidumbre?

La solución elegida es **repetir el último cierre diario conocido** para pronosticar el promedio mensual de los cierres publicados a +1 y +3 meses. Se comparó con repetir el promedio mensual y con Ridge de tres rasgos históricos, con selección, calibración de bandas y evaluación posterior separadas. El ingenuo se seleccionó antes de la evaluación; Ridge no muestra una mejora suficiente para justificar complejidad.

En la evaluación desde 2019, el ingenuo obtiene **MAE 0.694 centavos de USD/libra y WAPE 3.95 % a un mes**, y **MAE 1.653 centavos y WAPE 9.31 % a tres meses**. Hay 64/62 emisiones evaluadas, con objetivos hasta mayo de 2024. Los errores cambian entre años; no son tasas futuras garantizadas. Los entrenamientos solo usan objetivos ya maduros en cada origen.

El último ejercicio se emite **con información al cierre de mayo de 2024**, para junio/agosto; no es un pronóstico actual. Las 15 filas del junio parcial se conservan aparte y no se usan como promedio de mes completo.

| Horizonte/mes objetivo | Punto | Banda nominal 80 % | Banda nominal 95 % |
|---|---:|---|---|
| +1, junio 2024 | 18.30 | 17.16–19.52 | 15.75–21.27 |
| +3, agosto 2024 | 18.30 | 15.16–22.08 | 14.42–23.23 |

Todos los valores en centavos de USD/libra. Las bandas se calibran con errores de 2014–2018 y se congelan antes de evaluar. La nominal 80 % cubrió 81.25 % de casos a un mes y 96.77 % a tres: la segunda es amplia y conservadora, con incumplimientos en abril/mayo de 2020. No se interpreta esa cobertura como garantía futura ni como precisión alta.

**Decisión:** conservar el ingenuo como referencia transparente de presupuesto y escenarios. La continuidad no certificada y la diferencia respecto del precio físico/contrato negociable limitan el uso comercial; no se demuestra ahorro ni rentabilidad de cobertura. **Desarrollo:** [apartado 3 de conclusiones](conclusiones-serie-III.md#3-pronóstico-a-uno-y-tres-meses-con-incertidumbre), [notebook 16](../notebooks/16_pronostico_azucar_serie3.ipynb) y [método reproducible](../scripts/pronosticar_azucar_serie3.py).

### 4. ¿La superficie o producción responde al precio y con qué rezago?

**En el agregado mundial aparece una asociación positiva con el cambio de precio de dos años antes; en Guatemala la evidencia es débil.** Para 2004–2023, las correlaciones de crecimientos anuales a dos años son 0.718/0.776 en superficie/producción mundial, frente a 0.310/0.001 en Guatemala. La correlación de niveles de superficie de Guatemala es 0.845, pero no se conserva con esa magnitud al comparar cambios: no basta para defender respuesta local.

Con diez evaluaciones temporales retrospectivas de 2014–2023, los dos rezagos de precio reducen el MAE mundial frente a media histórica de 2.241 a 1.874 en superficie y de 3.201 a 1.425 en producción (**16.36 % y 55.46 %**). Son puntos logarítmicos de error del crecimiento, no porcentajes del volumen ni ahorro. En Guatemala el mismo modelo empeora la referencia: 4.249 → 4.540 y 9.838 → 10.339. El contraste adicional con crecimiento propio y las sensibilidades no justifican una regla local de expansión.

**Dos años es una señal asociativa entre los rezagos examinados, no un tiempo físico ni una elasticidad causal demostrados.** Solo hay veinte ecuaciones anuales por ámbito; se usan versiones finales de FAOSTAT y no se comprobó disponibilidad histórica. El futuro puede anticipar cosechas y compartir causas con ellas; faltan calendario de decisiones, precio físico esperado/neto, costos, moneda, clima y variación exógena identificada. La continuidad contractual sigue parcialmente verificada.

**Decisión:** usar la relación mundial para contexto de escenarios, sin ordenar ampliación de superficie de Guatemala ni prometer producción o beneficio por una subida del precio. **Desarrollo:** [apartado 4 de conclusiones](conclusiones-serie-III.md#4-respuesta-de-superficie-y-producción-al-precio), [notebook 17](../notebooks/17_oferta_precio_serie3.ipynb) y [método reproducible](../scripts/analizar_oferta_serie3.py).

## Series IV y V: pendientes

- **Serie IV, producción:** falta decidir si desarrollar API para exponer un modelo, validación de entradas, OpenAPI, Docker Compose y pruebas. La prueba condiciona estos entregables a que se desarrolle la serie.
- **Serie V, presentación:** falta crear la presentación ejecutiva de 15–20 minutos para las tres gerencias y preparar la demostración de API solo si se desarrolla la Serie IV.

Las respuestas disponibles se concentran en este documento. Los informes temáticos y notebooks contienen el detalle técnico, las limitaciones y la reproducción de sus resultados.
