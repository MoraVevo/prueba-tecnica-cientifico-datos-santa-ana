# Respuestas directas a la prueba técnica

Este es el punto de entrada para leer las respuestas de cada serie sin rastrearlas entre README, notebooks y resultados. Resume las decisiones y hallazgos confirmados, muestra el estado de cada petición y enlaza el análisis detallado. Las Series I y II tienen respuestas analíticas; las III, IV y V siguen pendientes y no se presentan como resueltas.

## Estado general

| Serie | Enfoque | Estado |
|---|---|---|
| I. Campo, variedades y renovación | Cuatro peticiones a Gerencia Agrícola respondidas con datos, modelos y límites. | Análisis completado. |
| II. Fábrica, caldera | Cinco peticiones respondidas con la serie de sensores externa del enunciado. | Análisis completado; para decisiones de planta se requieren comprobaciones adicionales. |
| III. Mercado, producción y precio | EDA de FAOSTAT revisado y verificado; fuente de precios descargada. | Lista la preparación para segmentación; cuatro respuestas finales pendientes. |
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

## Series III, IV y V: pendientes

- **Serie III, mercado:** el [EDA y comprobaciones](../notebooks/13_eda_faostat_serie3.ipynb) deja preparada una vista de 112 países/territorios en 1961–2023, con exclusiones trazadas y sin eliminar extremos como errores. Ya se puede avanzar a representación y segmentación para ubicar Guatemala; esa respuesta final aún no se ha construido. `Sugar_data.csv` está descargado, pero falta auditar construcción/ajustes de contratos y analizar volatilidad, pronósticos y respuesta de oferta al precio.
- **Serie IV, producción:** falta decidir si desarrollar API para exponer un modelo, validación de entradas, OpenAPI, Docker Compose y pruebas. La prueba condiciona estos entregables a que se desarrolle la serie.
- **Serie V, presentación:** falta crear la presentación ejecutiva de 15–20 minutos para las tres gerencias y preparar la demostración de API solo si se desarrolla la Serie IV.

Las respuestas disponibles se concentran en este documento. Los informes temáticos y notebooks contienen el detalle técnico, las limitaciones y la reproducción de sus resultados.
