# Serie I: respuestas a Gerencia

Estado: los cuatro apartados de Serie I están completos y revisados en su alcance analítico. Se reconstruyeron las políticas económicas, las métricas y particiones supervisadas y las cuatro dimensiones y 17 pertenencias de la segmentación. Las 13 pruebas unitarias y 8 de integración verifican implementación y trazabilidad; la validación temporal informa desempeño. Las limitaciones y supuestos que siguen se conservan al interpretar y defender las decisiones.

## 1. Tres variedades, renovación y certeza

Recomendaría ampliar las siguientes variedades dentro del ejercicio:

| Variedad | Renovación propuesta | Aporte parcial esperado por acre/año, US$0.20/lb | Certeza de la recomendación |
| --- | --- | ---: | --- |
| HoCP14-885 | Después de 3 cosechas: plantía + 2 socas | US$727.58 | Media-baja para duración: fuerte desempeño, pero solo dos años en el último corte admitido; la tercera soca tiene un año y queda como sensibilidad. |
| L01-299 | Después de 4 cosechas: plantía + 3 socas | US$632.66 | Media: cada corte recomendado tiene al menos diez años y doce localidades; el horizonte de cinco cosechas tiene datos de una localidad y merece seguimiento. |
| Ho12-615 | Después de 4 cosechas: plantía + 3 socas | US$629.21 | Media-baja: queda tercera si se aplica el ajuste ambiental aditivo; con promedios directos, L01-283 la supera. |

La duración maximiza el aporte promedio anual de repetir una rotación: sumar ingresos y costos esperados de sus cortes, descontar renovación una sola vez y dividir por el número de cosechas. Se supone una cosecha por año, renovación inmediata, costos constantes y sin descuento ni año de descanso. El aporte incluye US$14/ton de caña, US$350/acre/año y US$1,100/acre por renovación; no es una utilidad neta completa.

Para la recomendación económica se utilizan los ensayos outfield, correspondientes a `STAGE=5`, porque su diseño documentado tiene parcelas más largas, tres repeticiones y evaluación en múltiples localidades. Así se evita mezclar directamente etapas con distintos diseños y procedimientos de medición. Esta delimitación no convierte las etapas anteriores en datos incorrectos: se conservan y el modelo supervisado las utiliza. [Fuente: Shahi et al., sección 2.1](https://acsess.onlinelibrary.wiley.com/doi/10.1002/tpg2.20545).

Se promedian repeticiones por clon/corte/año/localidad y se ajusta cada variedad por su diferencia respecto a L01-299 en ambientes compartidos. Se exige plantía y dos socas con al menos dos años y dos localidades por corte; la tercera soca se admite si alcanza esa cobertura. La falta de llave de cohorte limita la interpretación como flujo realizado, pero permite comparar políticas esperadas bajo estos supuestos. No se atribuye causalidad a la edad por esta comparación.

### Precio volátil

| Variedad | US$0.15/lb | US$0.20/lb | US$0.25/lb |
| --- | ---: | ---: | ---: |
| HoCP14-885 | US$251.45 | US$727.58 | US$1,203.71 |
| L01-299 | US$208.94 | US$632.66 | US$1,056.38 |
| Ho12-615 | US$204.42 | US$629.21 | US$1,054.01 |

Son escenarios ilustrativos de caída/subida de 25 % alrededor del precio del PDF, sin probabilidades ni datos de mercado añadidos. Las duraciones recomendadas se mantienen en esos escenarios, mientras el aporte cambia sustancialmente. Precios fuera del rango y otros costos pueden cambiar la política.

En 500 remuestras por año, los percentiles 5 y 95 del aporte de la política elegida son aproximadamente US$652–834 para HoCP14-885, US$572–700 para L01-299 y US$570–684 para Ho12-615. La misma duración reaparece en 100 %, 100 % y 98.6 % de las remuestras válidas; esto describe estabilidad dentro de esta muestra y método, no la probabilidad de superioridad real. Hay solo 12 años y no se remuestreó el ranking completo.

La comparación sin ajuste produce US$637.01, US$632.66 y US$601.45 por acre/año para esas mismas políticas; allí L01-283 (US$605.10) ocupa el tercer puesto. Por tanto, recomiendo HO12-615 como tercera opción solo bajo el ajuste ambiental aditivo aplicado; con promedios directos, L01-283 queda por encima y es la alternativa cercana. No asignaría porcentajes de área sin datos de superficie, disponibilidad y restricciones del ejercicio.

Seleccionamos **HOCP14-885, L01-299 y HO12-615** porque presentan los mayores aportes parciales anuales estimados entre las variedades que cumplen el criterio de cobertura definido, bajo los supuestos económicos del ejercicio. Las duraciones propuestas son tres, cuatro y cuatro cosechas totales, respectivamente, como políticas iniciales dentro del horizonte con mayor respaldo. La selección de HO12-615 en tercer lugar está condicionada al ajuste ambiental aditivo; con promedios directos, L01-283 la supera.

Las observaciones disponibles de cosechas posteriores sugieren que prolongar la plantación podría aumentar el aporte anual, aunque su cobertura es menor. Por ello, no interpretamos esas duraciones como un máximo económico demostrado ni la falta de cortes posteriores como evidencia de pérdida de rentabilidad.

El archivo no permite distinguir si la ausencia de una sexta cosecha responde a renovación deliberada, al diseño del seguimiento o a registros no incluidos. La evaluación de extensiones debe conservar esa incertidumbre y comparar su aporte anual con el de renovar, considerando también cambios en el precio del azúcar.

La media de L01-299 y la de Ho12-615 son cercanas y sus rangos P05–P95 del remuestreo se solapan. Al omitir el ajuste ambiental, L01-283 desplaza a Ho12-615 del tercer puesto. No se hizo una prueba formal de diferencias ni se estimó la probabilidad de que cada variedad ocupe el top 3.

Evidencia: `notebooks/03_analisis_economico_serie1.ipynb`; salidas locales de políticas, sensibilidad y remuestreo en `data/processed/`. El notebook incluye gráficas del ranking frente a otras alternativas y del aporte anual por duración, distinguiendo las extensiones con menor cobertura.

### Aclaración sobre cortes no observados y renovación

La ausencia de CROP 5 (sexta cosecha) ya existe en el CSV original. CROP 4 aparece en 2019 y 2020, además del último año 2021; el cierre temporal no permite explicar por sí solo todos los casos. La coexistencia de varios CROP para igual variedad/localidad/año impide interpretar una plantía posterior como renovación de la misma parcela. Sin identificación de parcela/cohorte o motivo de retiro, no se distingue renovación deliberada de un límite de seguimiento o de cobertura del archivo. No se interpreta la falta de observación como rendimiento o aporte cero.

Una futura regresión económica podría estimar el aporte de cosechas adicionales, pero todavía no se ha ajustado. La decisión de prolongar debe comparar el aporte anual de rotaciones completas, incluido el costo de renovación, y revisar su sensibilidad a precio e incertidumbre. Un aporte positivo en una soca adicional no establece por sí solo que prolongar sea la mejor decisión. Una predicción para CROP 5 sería extrapolación sin contraste directo en ese corte.

## 2. Modelo supervisado para la siguiente zafra

Se comparan Ridge, árbol de decisión y bosque aleatorio. Ridge se elige por el menor MAE promedio al entrenar hasta 2018 y validar 2019, y entrenar hasta 2019 y validar 2020. En esos dos cortes su MAE medio es 2,405.64 lb/acre, frente a 2,787.95 del árbol y 2,882.48 del bosque. El año 2021 se reserva para evaluación final y no determina la elección.

| Método | MAE 2021, lb/acre | RMSE 2021, lb/acre | R² 2021 |
| --- | ---: | ---: | ---: |
| Ridge elegido | 2,144.55 | 2,770.97 | 0.25 |
| Árbol de decisión | 2,330.43 | 2,983.90 | 0.13 |
| Bosque aleatorio | 2,261.69 | 2,877.42 | 0.19 |
| Referencia histórica de clon/corte | 2,662.69 | 3,385.62 | -0.12 |
| Referencia de clon/ambiente reciente | 2,270.33 | 2,938.43 | 0.16 |

Las entradas son variedad, localidad, etapa, corte planificado, año y promedios históricos del azúcar por clon, localidad y clon/corte, calculados con años estrictamente anteriores. El código ajusta codificación, imputación y escalado solo con cada entrenamiento. No usa mediciones de la cosecha que pretende anticipar: TCA y TRS_TON casi reconstruyen el objetivo y generarían fuga de información.

Ridge ofrece una explicación aditiva; el árbol aporta reglas y el bosque permite interacciones. Se muestran coeficientes numéricos y reglas en el notebook, con interpretación asociativa. Tras conservar la evaluación de 2021, se reajusta Ridge hasta ese año para ilustrar una predicción de 2022, siguiente zafra disponible en el ejercicio.

La lectura concreta de Ridge es que, manteniendo las demás entradas fijas, el ajuste evaluado en 2021 asocia una unidad adicional de `CROP` con aproximadamente 802 lb/acre menos y un año calendario más con 25 lb/acre menos. Son coeficientes regularizados y condicionados a los otros predictores; no demuestran que cada soca cause una caída constante ni bastan para decidir cuándo renovar. Las medias históricas del clon, la localidad y su combinación con el corte aportan el contexto previo que el modelo utiliza.

La mejora en 2021 es de aproximadamente 19.5 % respecto a la referencia histórica sencilla y 5.5 % respecto a la referencia reciente más exigente. En etapa 5 el MAE es 1,898.11 lb/acre. El error absoluto agregado representa aproximadamente 25.5 % del azúcar observado; la utilidad es moderada para presupuestar y comparar escenarios, y baja para comprometer un rendimiento exacto por parcela. A US$0.20/lb, el MAE global equivale a unos US$428.91/acre de ingreso bruto, sin ser un intervalo de confianza ni error del beneficio total.

El error global no describe por igual cada ambiente: en MAGNOLIA, etapa 5, el MAE de 2021 es 3,498.54 lb/acre en 72 observaciones, con sesgo de +3,498.54 lb/acre. Hay sobreestimación sistemática en esa muestra. Se entrega el desglose por localidad/etapa con su conteo; no se reajusta el modelo usando el test reservado. Las variables disponibles no permiten atribuir ese desvío a una causa específica.

En 2019 todos los algoritmos tienen R² negativo, señal de que las entradas no explican bien esa zafra. El sesgo de Ridge (`predicción − observado`) es +2,148 lb/acre en 2019 —sobreestimación media— y −1,078 en 2020 —subestimación media—. Una explicación plausible es el cambio de nivel entre años: el promedio del objetivo cayó entre 21 % y 27 % por etapa de 2018 a 2019, y subió entre 30 % y 41 % de 2019 a 2020; al usar años anteriores, Ridge puede quedar alto ante una caída y tardar en reflejar un rebote. Esto describe un mecanismo compatible con la validación, no demuestra por qué cambió el rendimiento. Como contexto, se ha relacionado 2019 con la cosecha muy húmeda de 2018 y condiciones meteorológicas adversas; en 2020 se documentaron cambios operativos por COVID y mayores rendimientos estatales de caña frente a 2019. La fuente no permite aislar clima, operación, manejo, cobertura o medición, y las claves coincidentes entre años no identifican parcelas pareadas. La sensibilidad incluyendo alertas de calidad en entrenamiento e historia da MAE cercano a 2,135.10 en las mismas filas limpias de 2021; se conserva el escenario principal más conservador. Las predicciones deben acompañarse de errores por corte/ambiente y monitoreo de sesgo; se requiere calibración específica antes de ofrecer intervalos de predicción.

Evidencia: `notebooks/04_modelo_supervisado_serie1.ipynb`, funciones y pipelines compartidos en `scripts/modelado_serie1.py`, y pruebas en `tests/`. Se guardan predicciones por fila de los cinco métodos en las tres particiones, métricas y errores por localidad/etapa en `data/processed/`. La reorganización para probar el código conservó exactamente las predicciones previas de 2021.

## 3. Segmentación y significado gerencial

Se segmentan 17 variedades de etapa 5 con cobertura de plantía y dos socas, dos años y dos localidades por corte. Las otras 23 quedan en una lista con el motivo de cobertura insuficiente. Cada variedad se representa por productividad de azúcar, calidad TRS, conservación segunda soca/plantía y variabilidad relativa entre localidades/años, centrada por variedad/corte. Productividad y calidad dan igual peso a los tres cortes; la fibra no se completa para forzar su uso.

La conservación se compara dentro de los mismos años y localidades de cada variedad: media de segunda soca dividida entre media de plantía en esos ambientes comunes. Se usan 840 comparaciones, con 18–110 ambientes por variedad, 2–12 años y 11–13 localidades. Los 678 ambientes sin ambos cortes se conservan aparte y siguen aportando a las otras dimensiones. Esto reduce diferencias de composición entre cortes, sin identificar la misma parcela ni demostrar una pérdida causal por edad.

Se mantienen cuatro dimensiones estandarizadas y K-means con **dos perfiles elegidos por parsimonia y lectura gerencial**. Las alternativas K=3 y K=4 dejan una variedad sola; se prefiere revisarla individualmente antes de añadir otro segmento. La silueta queda como diagnóstico secundario (0.254 en K=2, frente a 0.265 en K=4), sin determinar la elección ni demostrar clases naturales.

| Perfil | Variedades | Azúcar medio, lb/acre | TRS, lb/ton | Conservación en segunda soca | Variabilidad del índice relativo |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1: mayor caída y variabilidad medias | 5 | 7,997 | 290 | 75.4 % | 12.1 puntos porcentuales |
| 2: mayor productividad y conservación medias | 12 | 8,376 | 277 | 82.6 % | 9.8 puntos porcentuales |

Perfil 1: HO05-961, HO07-613, HOCP00-950, HOCP96-540 y L03-371. Conviene vigilar el aporte de cada soca y revisar su continuidad individual antes de ampliar. El TRS más alto es una media del grupo: HOCP96-540 tiene aproximadamente 267 lb/ton y la mayor variabilidad relativa de las 17 variedades.

Perfil 2: las otras doce variedades elegibles, incluidas las tres recomendadas económicamente. Respalda evaluar continuidad de socas dentro del horizonte observado y comparar aportes individuales. Las propiedades no son uniformes: HOCP14-885 tiene alrededor de 75 % de conservación en ambientes comunes, pese a la mayor conservación media del grupo. Los perfiles se determinan con las cuatro dimensiones y no fijan un umbral de renovación.

La construcción de las entradas importa más que una mejora de la métrica interna. HO05-961 pasa de 83.6 % de conservación sin emparejar a 76.0 % en ambientes comunes y cambia del Perfil 2 al 1 respecto a la versión anterior; esa comparación tiene solo dos años. Al usar agrupamiento jerárquico Ward, L99-226 cambia de perfil. Ambos casos requieren revisión individual. La omisión de variabilidad es la que más modifica las pertenencias (seis variedades); representa un cambio en la pregunta de negocio y no justifica retirar una dimensión solicitada.

La reconstrucción independiente desde el ETL reprodujo las cuatro entradas y las 17 pertenencias actuales. La certeza sigue siendo exploratoria: productividad y TRS describen coberturas distintas entre variedades; la referencia ambiental de variabilidad también cambia de composición y las dimensiones están parcialmente correlacionadas. El cociente de conservación no sigue cohortes ni observa causas de retiro. La segmentación orienta seguimiento; la ampliación y renovación se resuelven con el análisis económico y la evidencia individual, cuyas tres recomendaciones se mantienen.

Evidencia: `notebooks/05_segmentacion_variedades_serie1.ipynb`; tabla individual con unidades y cobertura, gráfica de las cuatro dimensiones, comparación de alternativas y sensibilidad. Salidas y exclusiones trazables en `data/processed/`.

## 4. Datos propios y diseño de ensayos propuesto

### Qué capturar

| Bloque | Campos prioritarios | Decisión que permite |
| --- | --- | --- |
| Identidad y seguimiento | ID único de ensayo, parcela, bloque y cohorte de plantación; variedad/lote de semilla; ubicación; superficie total de parcela y área útil cosechada, con unidades; fechas de siembra/cosecha; corte planeado/real; cambios de protocolo, cobertura o calendario | Seguir la misma unidad entre socas, interpretar rendimientos según el área medida y separar cambios del ensayo de cambios en el rendimiento. |
| Productividad y calidad | Caña pesada por parcela y área cosechada, azúcar recuperable y protocolo de laboratorio, TRS, fibra cuando se mida, tallos y peso de muestra | Medir rendimientos y explicar el intercambio entre cantidad de caña y recuperación de azúcar. |
| Ambiente y manejo | Suelo y análisis; lluvia, temperatura, humedad, inundaciones y eventos extremos por localidad y fecha, con fuente meteorológica; sistema y fuente de riego (o secano), fechas y volumen aplicado, continuidad o interrupciones del suministro; fertilización, labores, plagas/enfermedades y daños | Explicar variación entre ambientes y años, distinguir condiciones meteorológicas de manejo y evaluar si la disponibilidad de agua acompaña diferencias de productividad y costos. |
| Economía | Preparación, semilla/siembra, mantenimiento desglosado, corte/alce/transporte, área/cantidades/precio de cada insumo, precio efectivo y condiciones de liquidación | Completar el aporte, comparar renovación y someter la política a precio/costos reales. |
| Pérdidas y decisiones | Parcelas sin cosecha, resiembra o abandono y su causa; interrupciones o retrasos operativos y etapa afectada; fecha/motivo de renovación; rendimientos cero confirmados; ausencias y correcciones trazables | Evitar estudiar solo las socas supervivientes y distinguir un cero real, una pérdida o una interrupción de un dato ausente. |

El contraste entre 2019 y 2020 muestra por qué conviene registrar estas variables: en el historial disponible coinciden cambios de clima y de operación del programa, pero faltan datos de parcela y ejecución para separar sus efectos. Un indicador aislado de COVID quedaría confundido con el año y no permitiría atribuir causalidad; conviene llevar un registro de eventos externos con tipo, fechas, localidades/parcelas afectadas y operaciones interrumpidas. Para explicar una zafra, se usarían el clima observado y las incidencias operativas con sus fechas; para pronosticar antes de cosechar, solo clima, agua y manejo conocidos o previstos a la fecha de decisión.

El tamaño de parcela y el régimen de agua también importan para interpretar rendimientos: una parcela irrigada podría diferir de una dependiente de lluvia, pero esa diferencia no demuestra por sí sola un efecto causal del riego. Se registrarían sistema, fuente, continuidad y volumen de agua, y se compararían parcelas considerando suelo, localidad, variedad, manejo y costos. Si tecnología y localidad siempre aparecen juntas, el efecto propio de la tecnología no se podría separar con esos datos.

### Cómo ensayar

Propondría un ensayo de las tres variedades recomendadas más la variedad de referencia operativa de la empresa, en sitios que representen sus ambientes principales. Dentro de cada sitio, formar bloques de suelo/manejo comparable y asignar variedades al azar. Como estructura inicial ilustrativa: tres sitios, tres bloques y cuatro variedades únicas dan 36 parcelas experimentales; las repeticiones definitivas se dimensionan con variación por parcela y diferencia económicamente relevante. No se consideran tallos individuales como réplicas independientes de parcelas.

Si también se quiere estimar el efecto del riego, habría que incluir condiciones irrigadas y de secano comparables dentro del diseño, idealmente en los mismos sitios/bloques cuando sea viable. Comparar fincas distintas donde cada una tenga un único régimen confundiría riego con localidad, suelo y manejo.

Mantener el mismo identificador y seguir cada parcela desde plantía durante al menos tres socas, documentando retiros y manejo. Usar área de medición, protocolo de pesaje y laboratorio consistentes, con orden de muestreo aleatorio cuando corresponda. Capturar fechas reales para calcular duración, descansos y costo de oportunidad, en vez de asumir siempre un año por corte.

Para evaluar directamente la política de renovación, añadir una segunda fase con parcelas asignadas al azar a renovar después de dos, tres o cuatro cosechas y compararlas durante un horizonte común. Así se observa el costo y la producción de reiniciar, además de la soca que se deja de cosechar. La fase y sus recursos se acuerdan con Gerencia; aquí se propone el diseño y no se ejecuta captura adicional.

El análisis separaría efecto de variedad, corte y ambiente, usando la parcela seguida en el tiempo y bloques. Para pronosticar se reservaría una zafra completa y, si se desea ampliar a fincas nuevas, también localidades completas. Cada zafra cerraría con aporte económico, estabilidad del ranking, errores de pronóstico y decisión de mantener/renovar, revisando los supuestos antes de ampliar superficie.
