# Serie II: significado físico y disponibilidad de las señales

Este documento interpreta el diccionario y la documentación de la fuente; la selección del modelo se desarrolla en el notebook 12. El catálogo por sensor, los faltantes y los patrones de actualización se reproducen en el notebook 06. Las relaciones de proceso son explicaciones físicas plausibles, no efectos causales estimados con estos datos.

## Qué proceso representan

La fuente describe una caldera de carbón: el combustible y el aire producen calor en el hogar; los gases ceden calor y salen por el circuito de evacuación; el agua se calienta y vaporiza, y el vapor se sobrecalienta antes de salir. El economizador recupera calor de los gases para precalentar agua. El tiro inducido ayuda a evacuar gases. El atemperador regula la temperatura del vapor mediante agua de enfriamiento. No se presupone una caldera alimentada con bagazo por el contexto de la prueba.

| Familia y tags sin el sufijo `.AV_0#` | Lectura física y posible aporte | Qué no está confirmado |
| --- | --- | --- |
| Presión alta del hogar: `PT_8313A`–`F` | Seis puntos de presión en la zona de combustión. Describen distribución de presión, circulación y cambios comunes o asimetrías. | Referencia absoluta/manométrica, unidades y posición exacta de cada punto. Un valor negativo no demuestra imposibilidad. |
| Presión del recipiente y salida: `PTCA_8322A`, `PTCA_8324` | Condición de presión del circuito de agua/vapor; puede acompañar cambios de carga y demanda. Presión y caudal son magnitudes diferentes: no se deduce uno únicamente del otro. | `Pot` y `Container` no identifican inequívocamente el componente; no se asegura que sea presión del domo sin plano. |
| Temperaturas de gases/hogar: `TE_8319A/B`, `TE_8313B` | Estado térmico de combustión y gases; lados izquierdo/derecho permiten observar asimetrías. La temperatura puede acompañar cambios de calor transferido y generación de vapor. | Unidades por tag y ubicación/tiempo de respuesta exactos. Temperatura alta no equivale automáticamente a mayor eficiencia. |
| Aire: temperaturas `TE_8303/04`, caudales `FT_8301/02`, `FT_8306A/B` | Condiciones del aire primario, secundario y de la cámara de retorno. Describen suministro y reparto de aire; pueden reflejar el régimen de combustión. | Unidades, condiciones de referencia de caudales, recirculación y función exacta de la cámara de retorno. No se calcula masa ni exceso de aire con tags sin unidades. |
| Oxígeno: `AIR_8301A/B` | Oxígeno de gases en dos lados; aporta información sobre aire disponible y combustión. Puede ayudar a distinguir regímenes aun si su relación directa con vapor es baja. | Base seca/húmeda, unidad/escala, calibración y punto exacto. No se convierte el número directamente en exceso de aire ni se fija un óptimo universal. |
| Tiro inducido: `YFJ3_AI`, `YFJ3_ZD1/2` | Corriente del motor como indicador indirecto de esfuerzo operativo; vibración de dos puntos del cojinete como estado mecánico. Las vibraciones pueden ser más útiles para anomalías que para estimar vapor. | Corriente no equivale a potencia sin tensión, factor de potencia y configuración. Vibración requiere unidad, eje y banda para límites mecánicos. |
| Diferenciales: `SXLTCYZ/Y`, `ZCLCCY`, `YCLCCY` | Diferencias de presión entre zonas altas/bajas y capas laterales; describen distribución de presión y cambios en el paso de gases/material. | Tomas de presión, unidades y significado de `layer`. No se identifica automáticamente una obstrucción ni una altura de lecho. |
| Atemperación: `TV_8329ZC`, `YJJWSLL` | Válvula asociada al control de temperatura de salida del atemperador primario y señal de caudal de agua. Pueden reflejar necesidades de enfriamiento y cambios de carga. | Válvula: orden, posición real o salida del controlador; no se afirma porcentaje de apertura. Agua: `flow output` no confirma instrumento independiente ni descarta señal calculada. No es el caudal total de alimentación de la caldera. |
| Temperatura de vapor: `TE_8332A` | Condición térmica a la salida de la caldera. La publicación confirma °C y una banda operativa de 530–545 °C para esta unidad. | No es temperatura local de salida del atemperador primario confirmada. Banda operativa no equivale a rango de validez instrumental. |
| Objetivo: `ZZQBCHLL` | Caudal de vapor principal después de compensación: cantidad de vapor que pasa por unidad de tiempo, no temperatura ni presión. | Unidad del caudal, fórmula y señales usadas para compensarlo. No se asumen toneladas/hora ni independencia respecto de otros tags. |

Las unidades de temperatura de otros tags podrían ser °C, pero no se extiende la confirmación de `TE_8332A` a todos los instrumentos como hecho documentado.

## Disponibilidad para el sensor virtual

**Uso del modelo:** estimar el caudal de vapor del instante `t` con otras señales de proceso recibidas hasta ese momento. Es una estimación contemporánea, no un pronóstico de la siguiente hora. El PDF pide un sensor virtual sin imponer un horizonte futuro.

La publicación describe adquisición mediante un DCS, con acondicionamiento de señales y archivo de marcas temporales. Esto respalda su origen operativo; no prueba latencia cero, relojes perfectamente sincronizados ni disponibilidad independiente de cada tag durante una falla.

| Comprobación | Evidencia y decisión |
| --- | --- |
| Existencia histórica | Hay 29 señales candidatas además del objetivo, en 86,400 filas. Son candidatas disponibles en el archivo, no 29 entradas garantizadas en producción. |
| Cobertura | 28 predictoras no tienen faltantes; `YJJWSLL` tiene 30/86,400 = 0.03472 % faltantes, en dos episodios. La imputación usa medianas ajustadas solo con entrenamiento; la ausencia original queda registrada. |
| Actualización | El archivo tiene pasos de cinco segundos. `SXLTCYZ`, `SXLTCYY`, `ZCLCCY`, `YCLCCY` y el objetivo repiten todos los pares consecutivos: compatible con actualización efectiva cada diez segundos o retención, sin mecanismo probado. No equivalen a una medición independiente nueva cada cinco segundos. |
| Estabilidad de válvula | Los niveles mantenidos no implican falta de disponibilidad ni falla; se conserva. Su disponibilidad física real sigue dependiendo de qué representa el tag. |
| Disponibilidad de tiempo real | No hay fecha de recepción, calidad, edad de lectura, latencia por canal ni modo manual/automático. Para usar `x(t)` se deberá declarar el supuesto de que ya se recibió al emitir la estimación; si no, usar la última lectura recibida y su edad. Desplazar una fila por sí solo no verifica ese supuesto. |
| Independencia del objetivo | `ZZQBCHLL(t)` se excluye de las entradas. Para evaluar un reemplazo durante indisponibilidad del caudalímetro, el modelo tampoco depende de sus rezagos: podrían dejar de existir o congelarse. Otro escenario con historial del objetivo requeriría evaluación separada. |
| Caudal compensado | Presión/temperatura pueden intervenir en compensación de densidad de un caudal de vapor, pero no conocemos la fórmula de este equipo ni qué tags usa. Compartir una variable de compensación no demuestra por sí solo fuga; sí obliga a revisar si el predictor depende del caudalímetro averiado o de su misma cadena de adquisición. No se demuestra independencia instrumental con el CSV. |
| Transformaciones | No usar valores futuros ni interpolación apoyada en el futuro. Ajustar imputación, escalado y selección solo dentro de entrenamiento. Estimar vapor con señales contemporáneas permitidas no las convierte en causas ni permite simular qué pasaría al manipularlas. |
| Falla compartida | Tener sensores en columnas diferentes no asegura supervivencia ante una pérdida común de DCS/comunicación. La evaluación histórica del sensor virtual no certifica continuidad ante todos los tipos de falla. |

## Modelo seleccionado y disponibilidad

Ridge utiliza diecisiete entradas de quince sensores: quince señales actuales y las presiones PTCA_8322A/PTCA_8324 a treinta segundos. MAE medio 0.356026 y WAPE agregado 0.598068 % en tres validaciones temporales. La selección de señales, imputación y escalado se ajustan dentro del entrenamiento. La relación temporal no certifica un tiempo de respuesta físico.

El ajuste final usa 34,464 filas de los primeros cuatro días, con recorte inicial común de 660 s y separación final de cinco minutos. Las validaciones son reutilizadas; se necesita un periodo nuevo para evaluar generalización. El artefacto y sus columnas están en outputs/campeona_serie2/. Detalle en el [informe de rezagos](rezagos-serie-II.md).

## Información que resolvería las ambigüedades

Solicitar lista de instrumentos con unidades/rangos y puntos de instalación, diagrama de proceso e instrumentación, fórmula y entradas del caudal compensado, origen medido/calculado de cada tag, tiempos de actualización/recepción, banderas de calidad y modo de control. Para válvula: consigna y posición real separadas. Para el alcance del sensor virtual: confirmar si se busca reemplazo de caudalímetro, contraste de medición o pronóstico, y qué componentes fallan en el escenario evaluado. Esta solicitud es una propuesta futura, no un requisito adicional que bloquee resolver el ejercicio con supuestos explícitos.

## Fuentes

- Diccionario local `data/raw/serie2/columns.csv` y datos originales suministrados por el enlace del PDF.
- [Hu et al. (2025), descripción de la caldera y adquisición DCS](https://doi.org/10.1038/s41597-025-05096-4). Describe el proceso y la procedencia; no resuelve las ambigüedades individuales enumeradas.
- [DOE: eficiencia de combustión](https://www.energy.gov/sites/prod/files/2014/05/f16/steam4_boiler_efficiency.pdf). Apoya el papel de oxígeno y temperatura de gases; no se aplican a esta caldera las cifras de ahorro de su ejemplo de gas natural.
- [Spirax Sarco: teoría de atemperación](https://www.spiraxsarco.com/learn-about-steam/desuperheating/basic-desuperheating-theory?sc_lang=en-GB). Explica enfriamiento y regulación con agua; no identifica el diseño exacto de este tag.
- [Spirax Sarco: instrumentación y compensación de caudal](https://www.spiraxsarco.com/learn-about-steam/flowmetering/instrumentation). Fundamenta revisar dependencias de presión/temperatura, sin atribuir una fórmula no documentada al archivo.
