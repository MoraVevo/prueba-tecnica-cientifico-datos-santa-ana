# Serie III: producción mundial y precio del azúcar

## Lectura económica y decisiones

**Guatemala tiene una posición favorable de productividad de la tierra dentro de las referencias estudiadas, en un mercado con riesgo de precio relevante y ajustes de oferta diferidos. La recomendación es proteger el margen de la base productiva y evaluar expansión por rentabilidad esperada de varias zafras, sin extrapolar un precio favorable puntual.** Esta es una conclusión de decisión apoyada en datos y teoría económica; no exige haber identificado la elasticidad causal de cada país.

La interpretación distingue tres niveles: el hallazgo medido, el mecanismo económico que lo explica de forma plausible y la recomendación bajo supuestos explícitos. La evidencia me permite escoger una hipótesis de trabajo y una política de planificación; los límites precisan su alcance.

| Inciso | Hallazgo | Interpretación económica | Decisión recomendada |
|---|---|---|---|
| 1. Posición productiva | Guatemala supera la referencia mediana de rendimiento de sus cinco pares en aproximadamente 67.9 %; la expansión de superficie histórica es más pronunciada que la mejora de rendimiento. | Hay una fortaleza de productividad territorial y una trayectoria de crecimiento con componente extensivo importante. Rendimiento alto puede favorecer ingreso por ha, si calidad recuperable y precio neto son comparables; también puede requerir más insumos. | Tratar la productividad existente como un activo que debe conservarse; revisar su caída reciente y comparar mejoras de rendimiento con nueva superficie por margen incremental y recursos utilizados. |
| 2. Riesgo de mercado | La volatilidad anualizada restringida sigue cerca de 31.10 %, frente a 33.36 % observada. | El riesgo de precio permanece material después del tratamiento de observaciones sospechosas; no depende únicamente de los mayores saltos del archivo. | Incluir un escenario de precio desfavorable en presupuestos y revisar exposición de ventas y compromisos de costos; proteger margen es una prioridad de gestión, sin fijar todavía instrumentos o proporciones de cobertura. |
| 3. Pronóstico | Extra Trees mejora MAE de evaluación a un mes 6.12 % y Ridge histórico a tres meses 1.35 %. El último cierre gana la comparación de selección. | La propuesta se apoya en evaluación observada; la mejora depende del periodo y horizonte. | Proponer Extra Trees a un mes y Ridge histórico a tres, con bandas y baseline; validación a ciegas pendiente de datos no utilizados, sin afirmar un bloque ya reservado. |
| 4. Oferta y rezagos | A dos años, correlaciones de crecimientos mundiales de 0.718/0.776 para superficie/producción; el precio reduce error retrospectivo agregado. En Guatemala no supera la media histórica. | Los resultados respaldan parcialmente la hipótesis de oferta que reacciona de forma diferida a incentivos esperados. El plazo de dos años es una aproximación empírica en la malla estudiada, no una ley agronómica. | Incorporar respuesta futura de competidores al evaluar expansión. Exigir que el proyecto soporte precios menos favorables y contrastar alternativas por margen esperado de varias zafras, en lugar de activar expansión por un repunte aislado. |

El incentivo relevante es **el margen esperado respecto del mejor uso alternativo de los recursos**, no el precio bruto por sí solo. Una mejora esperada y persistente de ese margen favorece invertir, renovar o ampliar; la ejecución agrícola e industrial necesita tiempo. La rigidez inicial y la inversión de largo plazo están descritas por [FAO](https://www.fao.org/4/y4343e/y4343e05.htm), en *Economic and institutional structure*. El carácter perenne, la menor sustitución inmediata del cultivo y los retornos relativos frente a alternativas se desarrollan en [OECD/FAO, Sugar, apartados 5.2 y 5.4](https://www.oecd.org/en/publications/2019/07/oecd-fao-agricultural-outlook-2019-2028_g1g9f52f/full-report/component-9.html). Uso sus mecanismos económicos, no sus proyecciones históricas como pronóstico actual.

Como inferencia propia, si mejores márgenes inducen inversión de varios productores, la oferta adicional posterior puede moderar el precio, **si demanda, existencias, clima, política y otros usos no contrarrestan el efecto**. Mi análisis no estima esa trayectoria de precio ni demuestra un ciclo de duración fija. Sí justifica evaluar una expansión con precios que no mantengan indefinidamente el nivel favorable que motivó la decisión.

La falta de relación local estable con el futuro internacional no demuestra que Guatemala sea insensible a los incentivos. Puede haber una transmisión distinta al precio recibido, restricciones de tierra/capacidad, contratos o variaciones de rendimiento que no mide este contraste. La conclusión operativa es evaluar el margen local y el calendario de inversión, sin trasladar automáticamente los coeficientes mundiales. Una rentabilidad específica, superficie óptima o instrumento de cobertura requieren datos para parametrizar la decisión; su ausencia no impide recomendar estos criterios económicos.

**Mensaje ejecutivo de Serie III:** la ventaja física observada debe convertirse en margen sostenible. Recomiendo defender productividad, presupuestar el riesgo y crecer con disciplina frente a una oferta mundial que puede responder con retraso. El impacto cuantificado permanece en las métricas históricas de los apartados; no presento la orientación de gestión como un ahorro calculado ni ejecutado.

## 1. Segmentación de países productores

**Guatemala pertenece al perfil de mayor escala y rendimiento entre las áreas comparables de la muestra. Indonesia, Bolivia y Vietnam forman el núcleo de referencias más persistente por estructura de superficie; Nepal y Kenia son referencias secundarias.** La productividad publicada de Guatemala por hectárea es alta frente a esas referencias, pero no demuestra ventaja comparativa económica ni eficiencia de todos los recursos.

Este apartado responde al primer inciso del PDF: evolución de rendimiento, superficie y producción en 1961–2023, ubicación de Guatemala, pares, diferencias y calidad. Los apartados 2–4 desarrollan riesgo, pronósticos y asociación entre precio y oferta con rezagos. Los cuatro incisos tienen respuesta analítica, condicionada a calidad, continuidad de precios solo parcialmente verificada y límites de identificación causal.

### Perfiles productivos

K-means identifica dos perfiles amplios sobre 74 países/territorios con cobertura histórica suficiente:

| Perfil | Áreas | Superficie reciente mediana | Rendimiento reciente mediano | Producción reciente mediana | Tendencia de superficie | Tendencia de rendimiento |
|---|---:|---:|---:|---:|---:|---:|
| 1. Menor escala y rendimiento | 18 | 4,743.5 ha | 26.96 t/ha | 0.123 millones t | +0.44 % anual equivalente | −0.27 % |
| 2. Mayor escala y rendimiento | 56 | 74,064.5 ha | 66.17 t/ha | 5.713 millones t | +1.45 % | +0.68 % |

Los niveles recientes son medianas de 2019–2023 por país y después medianas del grupo. Las tendencias describen la relación ajustada a medianas de bloques históricos; no afirman crecimiento constante ni pronostican el futuro. La producción caracteriza los perfiles sin añadir peso redundante a la distancia.

Guatemala está en el **Perfil 2**. Su rendimiento mediano reciente es **107.52 t/ha**, segundo entre las 74 áreas elegibles; no es un ranking mundial irrestricto. Su superficie mediana es 241,000 ha y su producción mediana 25.85 millones de toneladas. El perfil es amplio y contiene países muy distintos: compartir grupo no basta para declararlos pares cercanos.

Los perfiles se solapan. La silueta es 0.281 para K=2, frente a 0.201 para K=3 y 0.187 para K=4. La solución de dos grupos es la más parsimoniosa bajo la regla definida. No son dos clases naturales ni categorías de eficiencia.

### Pares por estructura territorial

La referencia para comparar productividad utiliza **solo superficie reciente, tendencia y variabilidad de superficie**. Rendimiento y producción no intervienen en esta selección, para no elegir pares por el resultado que después se pretende evaluar.

El criterio base admite superficie entre un cuarto y cuatro veces la de Guatemala y elige cinco vecinos por distancia estandarizada. Es una tolerancia de comparación, no prueba de igualdad de recursos. Contrasto también con un límite más estrecho de la mitad al doble.

| País | Superficie mediana 2019–2023 | Rendimiento mediano | Tendencia de superficie | Lectura de comparabilidad |
|---|---:|---:|---:|---|
| Guatemala | 241,000 ha | 107.52 t/ha | +4.03 % anual equivalente | País de referencia. |
| Indonesia | 449,008 ha | 69.93 t/ha | +3.74 % | Mayor superficie; trayectoria territorial cercana. |
| Bolivia | 180,065 ha | 54.75 t/ha | +3.10 % | Escala y expansión relativamente cercanas. |
| Vietnam | 174,816 ha | 65.44 t/ha | +4.01 % | Expansión histórica cercana, con mayor variabilidad de superficie. |
| Nepal | 64,354 ha | 49.67 t/ha | +4.07 % | Menor superficie; depende de admitir una diferencia de escala amplia. |
| Kenia | 89,800 ha | 74.60 t/ha | +2.66 % | Menor escala y expansión; referencia secundaria. |

**Indonesia, Bolivia y Vietnam permanecen en las variantes de cinco vecinos** al cambiar cobertura, ventana reciente, inclusión de variabilidad y tolerancia de superficie. Nepal/Kenia dejan la referencia cuando se exige una superficie entre la mitad y el doble de la de Guatemala. Si uso solo tres vecinos, la referencia base contiene Indonesia, Bolivia y Nepal; la pertenencia también depende de cuántos elija.

Estos países son pares por estructura de superficie observada. La fuente no demuestra semejanza de clima, suelo, riego, disponibilidad de agua, trabajo, capital o tecnología. Una superficie parecida es tierra asignada a caña, no una medición de recursos potenciales equivalentes.

### Productividad relativa

En cada año divido el rendimiento de Guatemala por la mediana de los rendimientos de sus cinco pares, sin incluir a Guatemala en el denominador. La síntesis reciente es la mediana de esos cinco cocientes anuales, no una comparación entre años diferentes.

| Referencia anual | Mediana del cociente de Guatemala, 2019–2023 | Interpretación descriptiva |
|---|---:|---|
| Mediana de cinco pares | 1.679 | Rendimiento aproximadamente 67.9 % superior. |
| Percentil 75 de cinco pares | 1.534 | Rendimiento aproximadamente 53.4 % superior. |

Al variar los criterios manteniendo cinco referencias, el primer cociente se sitúa entre **1.642 y 1.679**. Al utilizar tres u ocho vecinos, pasa a **1.964 y 1.624**, respectivamente. La superioridad descriptiva permanece en los escenarios probados, pero su magnitud depende de la definición de referencia. No es un intervalo de confianza ni una eficiencia económica universal.

Las trayectorias explican parte de las diferencias: la superficie de Guatemala y de sus referencias crece históricamente, mientras el rendimiento de Indonesia desciende en la serie y los otros países muestran trayectorias distintas. La producción combina ambos componentes; una producción mayor puede proceder de más superficie aunque el rendimiento por hectárea sea menor.

En Guatemala la tendencia ajustada es +4.03 % anual equivalente para superficie y +0.81 % para rendimiento. La expansión territorial es, por tanto, más pronunciada que la mejora de rendimiento en esa representación histórica. No interpreto la mayor producción íntegramente como una ganancia de productividad ni como causalidad estimada.

La serie de Guatemala registra 99.47 t/ha en 2023 frente a 107.69 en 2022: un descenso aproximado de **7.63 %**, ambos con flag A. Su posición relativa alta no implica ausencia de margen de mejora ni estabilidad garantizada. Estos datos no identifican la causa de ese descenso.

### Calidad y certeza

Las principales restricciones son:

- **Guatemala 2019–2021:** rendimiento con flag E y superficie I; producción A. En 2022–2023 los tres indicadores son A. La comparación reciente depende parcialmente de estimaciones/imputaciones, no de cinco años homogéneos de datos oficiales.
- **Calidad desigual entre referencias:** Indonesia tiene solo 10 de 63 rendimientos históricos con flag A, frente a 63 de 63 en Bolivia. Los flags describen procedencia/metodología declarada, no una medición directa del error; esta diferencia limita la interpretación de trayectorias y comparaciones.
- **Sensibilidad solo A:** Guatemala no cumple el mínimo de cuatro años recientes, por lo que no puede reconstruirse íntegra la segmentación principal usando solo esa bandera. El contraste parcial de productividad en 2022/2023, con cuatro referencias A, produce cocientes 1.812 y 1.576. Es respaldo descriptivo parcial, con otro denominador, no validación completa del periodo.
- **Perfil 1:** la mediana de proporción histórica de producción oficial por país es 28.6 %, frente a 93.7 % en el Perfil 2. Sus trayectorias más suaves pueden reflejar procedimientos de estimación. No interpreto automáticamente menor variabilidad como mayor resiliencia productiva.
- **Cobertura:** 38 áreas están sin segmento por cobertura insuficiente en los bloques o en años recientes. Entre ellas hay productores actuales como Zambia, Sudán y Malawi; no los considero países improductivos ni datos erróneos. Conservo sus filas y motivos.
- **Calidad aritmética y extremos:** las 63 marcas del EDA son compatibles con redondeo del área bajo un supuesto explícito. Conservo los extremos y flags E/I/X; no hay prueba de error que justifique su borrado automático.

Las semillas ensayadas dan la misma partición. La coincidencia con Ward es ARI 0.715; al omitir variabilidad baja a 0.438. La ventana 2014–2018 produce ARI 0.886 y la cobertura alternativa 50 % da 0.942. La certeza de los grupos es **exploratoria y dependiente de la representación**; la repetición entre semillas no demuestra que los perfiles sean categorías físicas verdaderas. Los escenarios no son réplicas independientes.

La certeza es moderada para describir la productividad publicada y el núcleo de pares bajo las variables disponibles; limitada para atribuir las diferencias a gestión, tecnología o condiciones naturales. Sin costos de oportunidad no puedo estimar ventaja comparativa económica. Sin otros insumos no puedo medir eficiencia total de recursos.

### Decisión gerencial

Guatemala destaca por productividad territorial en esta muestra: es una fortaleza física que debe conservarse y contrastarse en términos de margen por hectárea. Recomiendo revisar la caída reciente de rendimiento y comparar mejoras en la base existente con expansión territorial según margen incremental, recursos y riesgo. Indonesia, Bolivia y Vietnam son el núcleo de contraste de superficie/expansión; Nepal/Kenia son referencias secundarias. Los pares ayudan a estructurar esa comparación, sin determinar qué tecnología o inversión resultará rentable.

El impacto observado es una referencia cuantificada para interpretar posición y trayectoria, no un aumento de producción alcanzable por intervención. Para evaluar eficiencia económica harían falta costos, precios y alternativas de uso de recursos; para comparar condiciones físicas harían falta agua, clima, suelo e insumos. La posición alta tampoco sustituye investigar el descenso reciente de rendimiento de Guatemala.

### Método y reproducción

Uso las 112 áreas del EDA sin agregados, China agregado ni predecesores empalmados. La cobertura exige tripletas positivas de área/rendimiento/producción en al menos seis de diez años de cada bloque hasta 2010, ocho de trece en 2011–2023 y cuatro de cinco en 2019–2023. No imputo ausencias ni transformo ceros en rendimientos inventados. Las 74 áreas admitidas conservan sus observaciones originales; separo las 7,182 celdas de las 38 áreas excluidas de esta segmentación, con su motivo.

Los seis rasgos son logaritmos de los niveles recientes de superficie/rendimiento, tendencias ajustadas sobre medianas de seis bloques y variabilidad robusta de sus cambios logarítmicos en años consecutivos. Los estandarizo antes de K-means. La producción no entra como tercera dimensión independiente por su identidad con área y rendimiento; describo su evolución y nivel en los resultados.

Para K examino 2/3/4, con un mínimo de cinco áreas por grupo; prefiero el menor K a no más de 0.02 de la mejor silueta admisible. No uso la posición de Guatemala para elegirlo. Los pares tienen una distancia distinta basada solo en superficie y los comparo en años coincidentes. Es agrupación descriptiva del periodo, no un modelo de pronóstico con un test futuro.

Evidencia reproducible: [notebook 14](../notebooks/14_segmentacion_paises_serie3.ipynb) y [preparación del análisis](../scripts/segmentar_paises_serie3.py). Tablas, modelo, figuras y exclusiones en `outputs/serie3_segmentacion/`, fuera de Git. El archivo de entrada del EDA conserva su hash.

```powershell
python -m nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=600 notebooks/14_segmentacion_paises_serie3.ipynb
python -m pytest tests/unitarias/test_segmentacion_serie3.py tests/integracion/test_segmentacion_serie3_resultados.py -q
```

Las pruebas reconstruyen conservación, rasgos, distancias, referencias y orientación de la comparación mediante otra ruta de cálculo. Verifican también que cambiar arbitrariamente el rendimiento no altera los pares seleccionados por estructura. No certifican la exactitud de las cifras nacionales ni causalidad.

## 2. Volatilidad, regímenes y extremos del azúcar No. 11

**El precio muestra periodos de riesgo elevado que permanecen al apartar retornos sospechosos. La volatilidad histórica anualizada es 33.36 % en la serie completa y 31.10 % en la sensibilidad restringida. La continuidad no está certificada: hay evidencia de problemas de enlace/reporte y una caída extrema corroborada puntualmente, pero faltan contratos y reglas de ajuste para certificar todos los movimientos.**

### Fuente y confiabilidad

`Sugar_data.csv` contiene 6,097 filas OHLCV, del 01-03-2000 al 24-06-2024, ordenadas sin fechas repetidas, celdas ausentes ni precios no positivos. La [ficha del autor en Kaggle](https://www.kaggle.com/datasets/guillemservera/agricultural-futures), versión 188, declara Yahoo Finance como origen. No proporciona un contrato por fecha ni documenta su enlace, ajuste o definición de cierre frente a liquidación.

[ICE especifica](https://www.ice.com/products/23/) cotización en centavos de USD/libra, contrato de 112,000 lb y entregas actuales en marzo, mayo, julio y octubre, con último día de negociación en el mes anterior. La historia no es idéntica al calendario vigente: un [aviso de ICE de 2009](https://www.ice.com/publicdocs/futures_us/exchange_notices/exnot100109S11Jan.pdf) documenta un contrato de enero de 2010 con último día excepcional el 22 de diciembre de 2009.

Hay **93 volúmenes cero y 11 inconsistencias OHLC**. Las once aparecen en la última sesión observada de febrero, abril, junio o septiembre. Esto es compatible con problemas de enlace o reporte, pero no identifica su mecanismo exacto. Un volumen cero puede reflejar falta de reporte y no demuestra que no hubiera negociación. Los huecos de fechas tampoco se equiparan automáticamente con registros perdidos: incluyen fines de semana y cierres del mercado.

Un cambio de vencimiento puede mezclar variación temporal con diferencias entre contratos. La [documentación de TradingView sobre ajustes](https://www.tradingview.com/support/solutions/43000685266-how-can-i-enable-backadjustment-for-continuous-futures/) explica esa mecánica general; no demuestra qué hizo Yahoo. Sin precios simultáneos de ambos vencimientos no invento una corrección.

### Tratamiento y sensibilidad

Conservo íntegros los datos y la serie observada. La sensibilidad principal aparta retornos en la última/primera sesión observada alrededor de aquellas cuatro fronteras mensuales, o con OHLC inconsistente/volumen cero en cualquiera de sus dos extremos. La ventana de calendario es un **proxy de revisión**, no un calendario de roll certificado. Solo marco fronteras rodeadas de datos: el último registro, 24-06-2024, no lo convierto artificialmente en el fin de junio.

| Vista | Retornos | Volatilidad anualizada | P1 del retorno simple | P99 del retorno simple |
|---|---:|---:|---:|---:|
| Serie observada | 6,096 | 33.36 % | −5.43 % | +5.38 % |
| Sensibilidad principal restringida | 5,748 | 31.10 % | −4.97 % | +5.03 % |
| Ventana ampliada a dos sesiones por lado | 5,582 | 30.86 % | −4.95 % | +5.01 % |
| Sensibilidad adicional de diciembre histórico | 5,678 | 31.09 % | −4.96 % | +5.02 % |

Calculo el retorno **antes** de aplicar las máscaras, entre dos cierres consecutivos originales. No empalmo fechas separadas tras excluir filas. Aparto 348 retornos en la sensibilidad principal y, con la primera fila sin cierre anterior, conservo **349 filas con ambos extremos y motivo**. Ninguna marca equivale a error demostrado.

Las ventanas principales de calendario incluyen 194 retornos: 3.18 % de los observados, con 15.69 % de su suma de cuadrados. Es concentración descriptiva en fechas sospechosas; no estima qué fracción del riesgo fue causada por el enlace. La sensibilidad puede apartar movimientos reales y dejar enlaces no detectados, por lo que 31.10 % tampoco es una volatilidad certificada ni una cota estadística de la verdadera.

Uso desviación muestral de `ln(cierre_t/cierre_anterior)`, multiplicada por √252 y por cien. La anualización es una convención sobre sesiones cotizadas, sin supuesto de riesgo constante ni intervalo de confianza. Las variaciones de precio de las tablas de extremos se expresan como retornos simples.

### Regímenes descriptivos de riesgo

La volatilidad móvil restringida utiliza **63 sesiones**, con al menos 50 retornos admitidos y ventana temporal completa. Los cuartiles de toda la historia definen tres estados interpretables:

| Estado | Volatilidad anualizada móvil | Mediana dentro del estado |
|---|---|---:|
| Baja | Hasta 24.35 % | 21.38 % |
| Intermedia | Más de 24.35 % y hasta 34.35 % | 28.61 % |
| Alta | Más de 34.35 % | 39.11 % |

La proporción aproximada 25/50/25 % se debe a esa definición. No demuestra tres regímenes naturales ni constituye una señal de negociación validada. Uso los límites para describir retrospectivamente, no como calibración evaluada en un test futuro. Las ventanas solapadas también inducen persistencia.

El tramo de estado alto más largo va del 10-09-2009 al 16-11-2011, con 552 sesiones; no implica un solo choque económico de esa duración. Las volatilidades anuales restringidas permiten contrastar episodios sin depender únicamente de la etiqueta móvil:

| Año | Volatilidad anualizada restringida |
|---|---:|
| 2008 | 44.85 % |
| 2010 | 49.02 % |
| 2011 | 40.17 % |
| 2020 | 30.27 % |
| 2022 | 21.07 % |
| 2023 | 28.38 % |

Cambiar a una ventana de 21 sesiones modifica 30.89 % de los estados comparables, cada horizonte con sus cuartiles; comparar la serie completa/restringida con los mismos límites de 63 sesiones modifica 13.71 %. La lectura del régimen depende del horizonte y del tratamiento de continuidad. La correlación de retornos restringidos a una sesión es 0.0014, y la de sus magnitudes 0.0971: evidencia descriptiva modesta de concentración del riesgo, sin prueba de significancia, causalidad o capacidad comercial de anticipación.

### Extremos y contraste con mercado

El P99 de la magnitud del log-retorno observado es 6.654 %, con **61 marcas**; 27 están apartadas por la sensibilidad principal. No las declaro incorrectas. La sensibilidad tiene otro umbral, 5.881 %, con 58 marcas; son criterios de rareza estadística, no fallas confirmadas ni probabilidades de crisis.

| Fecha o tramo | Variación simple del CSV | Interpretación y evidencia |
|---|---:|---|
| 28-04 / 01-05-2000 | −16.50 % / +26.55 % | Frontera contractual y volumen cero el primer día. No es defendible presentar íntegramente el rebote como movimiento económico del mismo contrato. |
| 30-06 / 01-07-2008 | Cierre fuera del OHLC / +13.95 % | Otra frontera contractual; posible mezcla o problema de reporte, sin reparación exacta demostrada. |
| 12-11-2010 | −11.63 % | Permanece en la sensibilidad; cotejo puntual compatible con caída entre cierres de un mismo vencimiento. |
| 23-02-2016 | +11.02 % | Permanece; una noticia contemporánea respalda el repunte, con vencimiento y hora distintos al cierre no identificado del CSV. |

Para noviembre de 2010, la [tabla de FNB, página 8](fuentes-precios/fuentes/f005_fnb_12nov2010.pdf), publica **26.21 centavos/libra para Mar-11 el día 12**. Una [noticia de Bloomberg](https://economictimes.indiatimes.com/markets/commodities/white-sugar-drops-most-in-a-year-on-exports-from-europe/articleshow/6916921.cms) permite reconstruir el cierre previo de ese contrato: 27.98 tras caer 1.68 equivale a **29.66**. Ambos coinciden con el CSV a menos de medio tick; el descenso entre esos valores es aproximadamente 11.63 %. Es corroboración puntual mediante publicaciones contemporáneas, no una auditoría completa contra liquidaciones oficiales.

Para febrero de 2016, [Reuters documenta un repunte y revisiones del déficit](https://www.brecorder.com/news/280393/sugar-soars-over-7pc-as-supply-concerns-take-hold), pero su cotización es mayo e intradía. Respalda el contexto de mercado y no confirma exactamente el cierre 14.00 ni la variación de 11.02 %. Tampoco identifica una causa mediante un modelo causal.

La falta de marca de calendario o calidad no prueba que los demás retornos correspondan al mismo contrato. Para certificarlo faltan identificador diario, liquidaciones por vencimiento, precios simultáneos al cambio, calendario histórico y metodología de enlace/ajuste/cierre.

### Decisión gerencial y certeza

El riesgo de precio persiste en las distintas vistas: no se explica únicamente por los saltos sospechosos. Recomiendo incorporar escenarios adversos de precio al presupuesto y revisar la exposición de ventas frente a compromisos de costos. Es una prioridad económica respaldada por la magnitud observada, aunque no haya elegido un instrumento de protección. Para fijar límites comerciales numéricos o estimar rentabilidad de una cobertura debo completar la continuidad por contrato; no atribuyo automáticamente cada extremo a clima, oferta, demanda o especulación.

### Contraste mensual y por vencimiento

El [contraste de continuidad](continuidad-precios-serie-III.md) compara 291 meses completos con USDA ERS: la mediana de diferencia porcentual absoluta es 0.00543 %, pero 14 meses difieren más de 1 %. Conservo junio de 2024 separado por ser parcial. Tres cotizaciones publicadas para Mar-11 coinciden al centavo con el CSV; los cambios entre ellas son semanales. Las medias de 2008 son próximas a USDA, pero no identifican el contrato de cada salto diario. La evidencia refuerza niveles mensuales y cotejos puntuales; la continuidad contractual completa está pendiente. No ajusto ni sustituyo la serie. El [notebook 19](../notebooks/19_continuidad_precios_serie3.ipynb) y el [registro de fuentes](fuentes-continuidad-serie-III/indice.md) documentan el contraste y sus divergencias.

La escala económica es relevante: **un centavo por libra equivale a USD 1,120 por contrato de 112,000 lb**. La caída puntual corroborada de aproximadamente 3.45 centavos representa un cambio bruto de USD 3,864 para una posición larga de un contrato. Es ilustrativo; no incorpora costos, diferencial físico, moneda ni calendario comercial y no estima una pérdida de Santa Ana ni prescribe una cobertura.

La certeza es alta sobre fórmulas, conservación y marcas internas; parcial sobre continuidad y movimientos del mercado. La sensibilidad no entrega una serie certificada. El inciso tiene respuesta analítica con esa limitación explícita; la verificación completa de continuidad está pendiente, sin presentarla como resuelta. El apartado 3 presenta el pronóstico condicionado a esa fuente; el 4 examina oferta y rezagos.

### Evidencia y reproducción

[Notebook 15](../notebooks/15_precios_azucar_serie3.ipynb), [módulo de cálculo](../scripts/analizar_precios_serie3.py) y [fuentes de verificación registradas](fuentes-precios/indice.md). Un PDF público descargado de forma segura, con su tabla inspeccionada visualmente. La fuente cruda conserva SHA-256 `944471f40adce9a236bc992e3824f8c07f8f87b0f1aa7a5e50c47c888dcd52d1`. Tablas, figuras, datos/marcas, extremos, contraste externo y exclusiones están bajo `outputs/serie3_precios/`, ignorado por Git.

```powershell
python -m nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=600 notebooks/15_precios_azucar_serie3.ipynb
python -m pytest tests/unitarias/test_precios_serie3.py tests/integracion/test_precios_serie3_resultados.py -q
```

Las cinco pruebas específicas verifican conservación, motivos, ausencia de puentes entre retornos, frontera truncada, ventana sin futuro, volatilidad y estados mediante ecuaciones NumPy. Contrastan los precios externos registrados, sin convertir esa coincidencia en certificación del resto de la fuente.

## 3. Pronóstico a uno y tres meses con incertidumbre

**Propongo Extra Trees a un mes y Ridge histórico a tres meses como modelos entrenados para escenarios, con bandas y comparación contra el ingenuo. La elección es exploratoria porque la evaluación no es un periodo ciego: sus mejoras de MAE son 6.12 % y 1.35 %, respectivamente. El último cierre gana la comparación de selección entre 19 configuraciones; conservo ese resultado. No hay un test ciego reservado en los datos actuales: la confirmación independiente requiere datos realmente no utilizados. La falta de certificación de continuidad limita el uso comercial.**

### Qué se pronostica

El objetivo es el **promedio de los cierres diarios observados del mes calendario futuro**, en centavos de USD/libra, a +1 y +3 meses desde el cierre del mes de emisión. Es una referencia mensual del CSV publicado; no equivale a liquidación de un vencimiento identificado ni al precio físico recibido por Santa Ana.

Considero 291 meses, de marzo de 2000 a mayo de 2024, calculados con 6,082 filas diarias. Las 15 filas de junio de 2024 permanecen aparte con motivo de mes incompleto; no uso su promedio parcial como objetivo mensual completo. No imputo días ni invento ajustes entre contratos. Las marcas originales de calidad permanecen disponibles.

Genero el último pronóstico **con información al cierre de mayo de 2024**, para junio y agosto de 2024. Es un ejercicio histórico con la fuente del enunciado y no una predicción de precios actuales.

### Selección, calibración y evaluación

La validación utiliza orígenes móviles y horizonte explícito, conforme al criterio de [Hyndman y Athanasopoulos, capítulo 5](https://otexts.com/fpp3/toolbox.html#time-series-cross-validation). Fijo las particiones y candidatos antes de comparar errores de este experimento:

| Uso | Orígenes de emisión | Observaciones por horizonte |
|---|---|---:|
| Historia inicial | Marzo 2000–enero 2005 | Disponible para entrenamiento. |
| Selección de método/penalización | Febrero 2005–septiembre 2013 | 104 a cada horizonte. |
| Separación temporal | Octubre–diciembre 2013 | Esperar la maduración de objetivos a tres meses. |
| Calibración de bandas | Enero 2014–septiembre 2018 | 57 errores fuera de muestra a cada horizonte. |
| Separación temporal | Octubre–diciembre 2018 | Esperar los objetivos de calibración. |
| Evaluación posterior | Desde enero 2019 | 64 a un mes y 62 a tres, con objetivos hasta mayo 2024. |

En cada emisión reentreno con historia creciente. Una fila originada en j entra al entrenamiento solo cuando **j+h ≤ origen actual**: su objetivo mensual ya se conoce. Ajusto la estandarización y Ridge dentro de ese entrenamiento. No uso las etiquetas de regímenes calculadas sobre toda la historia como predictores.

Elijo el ganador de la comparación temporal exclusivamente con los errores de selección. Registro por separado la propuesta de entrega de modelos aprendidos y la declaro exploratoria: la evaluación no es un periodo ciego. Calculo los cuantiles de las bandas exclusivamente en calibración y los congelo antes de evaluar. Los entrenamientos posteriores incorporan meses ya observados, como ocurriría en uso secuencial; no incorporan objetivos futuros. La serie completa está observada en el EDA; esta evaluación está separada de la selección/calibración, pero no la declaro un periodo nuevo ciego.

Los errores comparten historia y, especialmente a tres meses, ventanas de información. No los trato como réplicas independientes ni presento pruebas de significancia basadas en esa suposición.

### Referencias y modelo de tres rasgos

- **Ingenuo del cierre:** repite el último cierre diario disponible del mes de emisión para ambos horizontes.
- **Ingenuo del promedio:** repite el promedio del mes de emisión. Sirve para distinguir la información del cierre más reciente del efecto de promediar precios.
- **Ridge directo:** predice el cambio logarítmico entre el cierre conocido y el promedio futuro. Usa tres rasgos: diferencia cierre/promedio actual y cambios del promedio en uno y tres meses, todos logarítmicos. Comparo penalizaciones 1, 10 y 100.

Prefiero el método de menor complejidad a no más de 2 % del menor MAE de selección: ingenuo cierre, ingenuo promedio y luego Ridge con mayor penalización. **Selecciono el ingenuo cierre en ambos horizontes antes de calibrar y evaluar**. Ridge-100 es el representante con menor MAE de selección dentro de Ridge; la comparación de evaluación no cambia los candidatos.

| Método | MAE a 1 mes | WAPE a 1 mes | MAE a 3 meses | WAPE a 3 meses |
|---|---:|---:|---:|---:|
| Ingenuo último cierre, elegido | 0.694 | 3.95 % | 1.653 | 9.31 % |
| Ingenuo promedio mensual | 0.859 | 4.88 % | 1.710 | 9.63 % |
| Ridge-100 | 0.703 | 3.99 % | 1.649 | 9.29 % |

MAE en centavos de USD/libra. WAPE es la suma de errores absolutos dividida por la suma de precios observados; no equivale al error porcentual de cada mes. Ridge-100 de tres rasgos reduce apenas aproximadamente 0.25 % del MAE de evaluación a tres meses, mientras empeora a un mes y no supera al ingenuo en selección. La conclusión se limita a esa especificación. El contraste de otras variables y familias se desarrolla a continuación.

Las métricas varían por año. En el ingenuo a tres meses, WAPE es 16.01 % en 2020 y 10.48 % en 2023; para los cinco objetivos de 2024 disponibles es 14.53 %. El agregado de 9.31 % no describe todos los periodos por igual. El desglose completo permanece en los resultados.

### Comparación de familias y variables

El [notebook 18](../notebooks/18_pronostico_ampliado_serie3.ipynb) compara **19 configuraciones predefinidas** con los datos del enunciado. Incluye cuatro familias aprendidas: Ridge, SVR con kernel radial, Extra Trees e HistGradientBoosting; referencias del último cierre y media, deriva logarítmica y suavizado exponencial simple. La autorregresión directa con doce cambios mensuales es una especificación de la familia Ridge. No son diecinueve algoritmos distintos.

Los conjuntos alternativos contienen **3 rasgos originales, 13 autorregresivos, 17 de historia, 22 al añadir información OHLC diaria y 24 con volumen**. Incluyen cambios de medias/cierres a 1/3/6/12 meses, rezagos, distancia a tendencia, volatilidad mensual, mes cíclico, rango/cuerpo diarios, volatilidad y riesgo bajista diarios, cambio de cinco sesiones y volumen relativo a tres/doce meses. La historia y la autorregresión son conjuntos alternativos. La malla compara dos regularizaciones/hiperparámetros por especificación ampliada, sin búsqueda abierta posterior.

Rango y cuerpo omiten del cálculo los once días OHLC incoherentes; volumen omite cero como actividad no confirmada. No borro filas: `dias_y_uso_rasgos.csv` conserva las 6,097 originales con indicadores de uso y motivos por señal. En meses completos hay 6,082 días; 6,071 utilizables para OHLC, 5,990 para volumen y 5,734 retornos para volatilidad diaria restringida. Los restantes de cada uso incluyen el mes parcial. La frontera del mes completo se conoce al cierre sin exigir observar el siguiente; calculo los retornos antes de enmascarar, sin puentes. Cierres/cambios largos siguen sujetos a continuidad no certificada. Conservo las doce observaciones mensuales iniciales sin rasgos completos como antecedentes y en archivo separado; no las imputo ni las descarto silenciosamente.

Todos los modelos directos de esta comparación usan el mismo inicio de ajuste, después de doce meses de historia, con etiquetas maduras `j+h<=origen`. Por ello `ridge_original` es la especificación de tres variables con ese inicio común; no tiene exactamente la muestra del Ridge del notebook 16. Evalúo los rasgos de rango/volumen incrementalmente en Ridge con iguales filas, sin atribuir causalidad ni extrapolar su aporte a todos los algoritmos. No introduzco FAOSTAT anual como predictor: faltan fechas de publicación y revisiones históricas; tampoco agrego datasets externos. La información disponible permite ampliar la comparación dentro del alcance.

Conservo la separación selección/calibración/evaluación y la regla de parsimonia de 2 %. En selección ensayo todas las configuraciones sobre 104 orígenes por horizonte; congelo el método elegido y un representante por familia/conjunto antes de calcular los otros periodos. **Toda la comparación ampliada es exploratoria:** la evaluación 2019–2024 no es un periodo ciego. No modifico la selección con sus errores ni afirmo un nuevo test independiente.

| Representante | MAE selección +1 | MAE evaluación +1 | MAE selección +3 | MAE evaluación +3 |
|---|---:|---:|---:|---:|
| Último cierre, seleccionado | **0.8964** | 0.6942 | **2.5993** | 1.6527 |
| Ridge autorregresivo, alpha 100 | 0.9083 | 0.7169 | 2.7170 | 1.6675 |
| Ridge historia, alpha 100 | 0.9149 | 0.6785 | 2.8057 | **1.6304** |
| Ridge historia + OHLC, alpha 100 | 0.9292 | 0.6824 | 2.8600 | 1.6316 |
| Ridge completo, alpha 100 | 0.9420 | 0.6735 | 2.8524 | 1.6359 |
| SVR, C 0.1 | 0.9742 | 0.7558 | 2.6846 | 1.6529 |
| Extra Trees, hoja mínima 10 | 0.9137 | **0.6517** | 2.6387 | 1.7196 |
| Boosting, hoja mínima 10 | 0.9874 | 0.6588 | 2.8539 | 1.7758 |

Errores en centavos USD/libra. Los dos horizontes y fases usan los mismos casos dentro de cada comparación. Extra Trees reduce MAE de evaluación a un mes **6.12 %**, con WAPE **3.70 %** frente a 3.95 %. Mejora en los años objetivo 2019–2021, 2023 y los cinco meses de 2024 disponibles, pero empeora en 2022. En la sensibilidad de calidad, 47 casos, reduce MAE de 0.5898 a 0.5479 y WAPE de 3.42 % a 3.18 %. Esta sensibilidad solo considera marcas de emisión/objetivo; no certifica todos los antecedentes usados al ajustar.

A tres meses, Extra Trees empeora al ingenuo; Ridge histórico reduce MAE de evaluación apenas **1.35 %**, con mejoras en 2019/2020/2024 y deterioros en 2021–2023. Añadir OHLC y volumen a Ridge no mejora consistentemente ambos horizontes y periodos. La propuesta utiliza Extra Trees a un mes y Ridge histórico a tres; la evaluación es exploratoria porque no es un periodo ciego. Es una elección de prototipos para confirmación, sin convertirlos en ganadores de un test independiente ni invalidar la selección congelada.

La malla está acotada por las 291 observaciones mensuales disponibles; más configuraciones sobre los mismos errores aumentarían el riesgo de selección oportunista. No ensayo todas las arquitecturas ni descarto que ARIMA, otras ventanas, datos diarios o fundamentales bien fechados aporten información. Su conveniencia requeriría un diseño adicional y confirmación prospectiva, no perseguir el menor error del periodo ya observado.

Extra Trees a un mes dispone también de incertidumbre reproducible: su banda nominal 80 % cubre **56/64 casos (87.50 %)** con amplitud media **2.53 centavos**, frente a 52/64 y 2.26 del ingenuo. Al 95 %, ambos cubren 62/64; la amplitud de Extra Trees es 4.83 frente a 5.29. Winkler medio es 3.43/5.59 para Extra Trees y 3.55/5.80 para el ingenuo a 80/95 %. Es evidencia exploratoria de la evaluación; mayor cobertura del 80 % viene acompañada de mayor anchura. Con información hasta mayo de 2024, Extra Trees estima junio en **18.25**, bandas 80 % **16.98–19.61** y 95 % **15.91–20.93**, en centavos USD/libra. No es un pronóstico actual ni una decisión comercial validada.

### Intervalos de incertidumbre

Para cada método y horizonte tomo los 57 errores de calibración `|ln(observado/predicho)|`. Para cobertura nominal c uso el valor ordenado en posición `ceil((n+1)×c)` y la banda `[p×exp(−q), p×exp(q)]`. No extrapolo la incertidumbre a tres meses aplicando automáticamente una raíz del tiempo ni impongo normalidad. Las bandas mantienen precios positivos.

Son **bandas empíricas de predicción**, no intervalos de confianza del precio medio estimado ni garantías de cobertura futura. La dependencia temporal, muestra pequeña y cambios de distribución limitan la interpretación nominal. Evalúo conjuntamente cobertura, amplitud y Winkler, que penaliza anchura e incumplimientos; menor Winkler es mejor.

| Horizonte | Cobertura nominal | Casos cubiertos | Cobertura observada | Amplitud media | Winkler medio |
|---|---:|---:|---:|---:|---:|
| 1 mes | 80 % | 52/64 | 81.25 % | 2.26 | 3.55 |
| 1 mes | 95 % | 62/64 | 96.88 % | 5.29 | 5.80 |
| 3 meses | 80 % | 60/62 | 96.77 % | 6.59 | 7.14 |
| 3 meses | 95 % | 60/62 | 96.77 % | 8.39 | 9.82 |

Amplitud y Winkler en centavos de USD/libra. A tres meses, la banda del 80 % es conservadora y ancha. Sus dos incumplimientos, también fuera del 95 %, corresponden a los objetivos de abril/mayo de 2020; no son fallas independientes. No interpreto la cobertura alta como precisión alta. No estrecho las bandas después de observar la evaluación para aparentar mejor calibración.

### Pronóstico del último origen completo

El último cierre de mayo de 2024 es 18.30 centavos de USD/libra. La persistencia produce el mismo punto a ambos horizontes, con distintas bandas:

| Objetivo desde mayo 2024 | Pronóstico | Banda nominal 80 % | Banda nominal 95 % |
|---|---:|---|---|
| Junio 2024, +1 mes | 18.30 | 17.16–19.52 | 15.75–21.27 |
| Agosto 2024, +3 meses | 18.30 | 15.16–22.08 | 14.42–23.23 |

Todas las cifras en centavos de USD/libra. Mantengo aparte el junio parcial disponible en la fuente; no evalúo ese promedio de 15 días como si fuera el mes completo. No hay pronóstico intermedio inventado para julio.

Los **modelos propuestos** conservan sus propios puntos e intervalos, calculados con información hasta ese mismo origen:

| Objetivo | Modelo propuesto | Punto | Banda nominal 80 % | Banda nominal 95 % |
|---|---|---:|---|---|
| Junio 2024, +1 mes | Extra Trees, hoja mínima 10 | 18.25 | 16.98–19.61 | 15.91–20.93 |
| Agosto 2024, +3 meses | Ridge historia, alpha 100 | 18.85 | 16.01–22.19 | 14.45–24.59 |

Extra Trees tiene cobertura posterior 87.50/96.88 % a niveles nominales 80/95 %. Para Ridge histórico a tres meses es 85.48/96.77 %, con amplitudes medias 5.68/9.32 centavos. Calculo las bandas por candidato con los errores de calibración anteriores; la cobertura observada del candidato propuesto no es una garantía independiente.

### Calidad, utilidad comercial y certeza

La sensibilidad de evaluación conserva únicamente emisiones/objetivos sin marcas directas de OHLC inconsistente o volumen cero en sus meses, manteniendo las mismas predicciones y sin reentrenar para mejorar la cifra. Hay 47 casos a un mes y 42 a tres: WAPE ingenuo 3.42 % y 8.11 %. Ridge-100 tampoco lo mejora en esa vista. Conservo los casos apartados con motivo. La ausencia de esas marcas no certifica continuidad ni todos los días de cada mes.

Recomiendo **Extra Trees a un mes y Ridge histórico a tres como modelos propuestos**, con especificaciones fijadas, incertidumbre y comparación explícita con el último cierre. La mejora de Ridge a tres meses es pequeña y la de Extra Trees depende del periodo: la elección utiliza evaluación observada, por lo que la declaro exploratoria. Los artefactos no acreditan aún generalización independiente. No existe un bloque reservado a ciegas dentro de esta fuente; esa comprobación permanece pendiente de datos no utilizados. Las bandas favorecen escenarios de planificación resistentes a precios distintos. El beneficio cuantificado es precisión histórica, no ahorro o rentabilidad comercial.

Para uso comercial faltan linaje por contrato, liquidaciones y método de enlace/ajuste, además del diferencial físico, moneda, volumen y calendario de exposición de Santa Ana. La agregación mensual puede suavizar algunos extremos diarios, pero no resuelve la mezcla de vencimientos. Los resultados no aseguran comportamiento posterior ni constituyen una recomendación para operar hoy.

La certeza es alta respecto de reproducción y separación computacional comprobada; limitada respecto del precio negociable representado, precisión futura y cobertura de nuevos regímenes. El inciso 3 tiene respuesta analítica condicionada a esas limitaciones; el apartado siguiente examina la relación de precio y oferta anual.

### Evidencia y reproducción

[Notebook 16](../notebooks/16_pronostico_azucar_serie3.ipynb), [módulo](../scripts/pronosticar_azucar_serie3.py) y [fuentes metodológicas](fuentes-precios/indice.md). En `outputs/serie3_pronostico/` conservo meses, filas del junio parcial, papeles de todos los orígenes, predicciones por fase, parámetros de cada ajuste, métricas por año/calidad, cuantiles, bandas evaluadas, pronósticos finales y artefacto seleccionado; fuera de Git. La fuente conserva su huella original.

```powershell
python -m nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=600 notebooks/16_pronostico_azucar_serie3.ipynb
python -m pytest tests/unitarias/test_pronostico_serie3.py tests/integracion/test_pronostico_serie3_resultados.py -q
```

Seis pruebas específicas reconstruyen agregación, pronósticos por solución matricial, etiquetas maduras, elección, cuantiles, cobertura y Winkler. Las pruebas de perturbación futura y de selección separada protegen contra usar información posterior; no certifican los precios ni una cobertura probabilística futura.

Para reproducir la comparación de familias, ejecutar el notebook 18 o `python -m scripts.ampliar_pronostico_serie3`; conserva los resultados del experimento de tres rasgos. Sus salidas están en `outputs/serie3_pronostico_ampliado/`: diseño, configuraciones/conjuntos, conservación diaria/mensual, predicciones, representantes/selección congelados, métricas por fase/año/calidad, bandas y pipelines. Las pruebas adicionales están en `tests/unitarias/test_pronostico_ampliado_serie3.py` y `tests/integracion/test_pronostico_ampliado_serie3_resultados.py`; contrastan disponibilidad incluso al truncar el futuro, conservación, rasgos desde crudo, soluciones matriciales Ridge, rutas de árboles/kernels y errores/bandas/artefactos.

Guardo la propuesta de entrega separada de la selección congelada: `decision_propuesta.json`, `pronosticos_propuestos.csv`, `intervalos_propuestos.csv` y `modelos_propuestos.joblib`, en el mismo directorio de outputs. El artefacto contiene dos pipelines entrenados, columnas, configuración y cuantiles. Su generación extrae los candidatos calculados, sin reentrenar ni cambiar el experimento. La decisión declara evaluación reutilizada y test ciego no reservado/no ejecutado.

## 4. Respuesta de superficie y producción al precio

**El agregado mundial presenta una asociación positiva entre cambios de precio de dos años antes y cambios de superficie/producción. En Guatemala la evidencia es mucho más débil y añadir precio no supera la referencia más sencilla. No se demuestra causalidad ni un rezago agronómico exacto.**

### Datos y alcance temporal

Cruzo el promedio anual de cierres diarios del No. 11 con superficie cosechada, producción de caña y rendimiento FAOSTAT de **Guatemala y World**, por año calendario. World es el agregado publicado; no una suma de países con cobertura seleccionada ni un segundo país independiente. El precio es nominal en centavos USD/libra, el área en ha, la producción en toneladas de caña y el rendimiento en kg/ha. No estimo producción de azúcar comercial.

La [comparación entre países](oferta-paises-serie-III.md), reproducida en el [notebook 20](../notebooks/20_oferta_paises_serie3.ipynb), añade los cinco pares de Guatemala fijados en III.1: Indonesia, Bolivia, Viet Nam, Nepal y Kenya. Todos usan 2004–2023 y las mismas especificaciones por país, sin panel que replique artificialmente el precio mundial. World sigue siendo solo contexto agregado. La selección de pares antecede al resultado de oferta; no elijo países por correlación.

Hay **23 años completos de precios, 2001–2023**, con presencia de doce meses; no certifica que estén todas las sesiones esperadas. De 6,097 días incluyo 5,766 y conservo aparte 331 de 2000 parcial/2024 parcial y fuera del ámbito del PDF, con datos originales y motivo. Las 138 celdas FAOSTAT seleccionadas forman 46 años-ámbito. Las otras 27,510 celdas permanecen con motivos geográficos/temporales. No declaro errores.

Calculo cambios logarítmicos `gX_t = ln(X_t/X_{t−1})` y luego rezagos, antes de seleccionar. Exigir la misma historia para todos produce **20 ecuaciones por ámbito, 2004–2023**; conservo aparte los seis años-ámbito iniciales. No imputo valores ni elimino extremos. Los flags permanecen: Guatemala tiene A en los tres indicadores en 14 de estos veinte años; seis incluyen estimación/imputación. Un A del agregado World no certifica calidad oficial homogénea de sus componentes.

Producción ≈ área × rendimiento / 1,000; el residuo máximo en log de esa identidad es 0.000002482 en el panel. Rendimiento permite examinar el componente de producción distinto de superficie; no es una tercera causa independiente.

### Relación contemporánea y rezagos

Examino los rezagos predefinidos 0, 1 y 2 sobre las mismas veinte filas, tanto en log de niveles como en cambios. El contemporáneo es descriptivo; no lo uso para anticipar una decisión que ocurre antes de conocer todo el precio del año.

| Ámbito/objetivo | Correlación de cambios, mismo año | Un año antes | Dos años antes | Correlación de niveles log, dos años antes |
|---|---:|---:|---:|---:|
| Guatemala, superficie | −0.391 | 0.223 | 0.310 | 0.845 |
| Guatemala, producción | −0.391 | −0.211 | 0.001 | 0.664 |
| Mundo, superficie | −0.181 | 0.063 | 0.718 | 0.871 |
| Mundo, producción | −0.207 | 0.097 | 0.776 | 0.839 |

La correlación alta de niveles de Guatemala no persiste al comparar crecimientos. En el mundo sí aparece una asociación diferida en cambios, más clara a dos años entre los rezagos probados. No amplío la búsqueda para maximizar la correlación. Diferenciar reduce el riesgo de tendencias compartidas, pero no prueba estacionariedad ni descarta cointegración o una relación de largo plazo. Las advertencias sobre tendencias, rezagos y causalidad se apoyan en [Hyndman y Athanasopoulos, capítulo 7](https://otexts.com/fpp3/regression.html), secciones 7.3, 7.4 y 7.8; el diseño concreto es propio.

### Ecuación y estabilidad

Contrasto cuatro especificaciones fijas: media histórica del cambio; crecimiento propio anterior; dos crecimientos previos del precio; y ambos conjuntos. La última es:

`gX_t = α + φ·gX_{t−1} + β1·gP_{t−1} + β2·gP_{t−2} + error_t`.

Son cuatro parámetros para veinte años. Sus coeficientes son asociaciones condicionales entre cambios logarítmicos, sin interpretación de elasticidad causal o de largo plazo. R² es ajuste interno. No reporto p-valores que supongan ecuaciones independientes.

En el mundo, β2 es **0.0986 para superficie y 0.1318 para producción**. Al omitir una ecuación anual cada vez, sus rangos son **0.0863–0.1061 y 0.1188–0.1387**. Sigue positivo en ambos bloques: superficie 0.1231/0.0641 y producción 0.1421/0.1312 en 2004–2013/2014–2023. Son sensibilidades de muestra pequeña, no intervalos de confianza; retirar una ecuación conserva ese año como antecedente de las otras.

En Guatemala, superficie tiene β1/β2 = 0.0609/0.0496 en el conjunto. Ambos siguen positivos al omitir una ecuación, pero β1 cambia de +0.0690 a −0.0337 entre bloques. Producción tiene −0.1186/−0.0064 y β2 cambia de signo al omitir años. La falta de señal productiva local no prueba ausencia de incentivos económicos; puede reflejar variables omitidas, medición, agregación o una respuesta diferente.

Promediar primero por mes y luego equiponderar meses da coeficientes próximos. Apartar únicamente los 99 días completos con OHLC inconsistente o volumen cero tampoco cambia la lectura; sus observaciones y motivos permanecen en archivo separado. Conservo el análisis principal con todos los cierres. Ninguna sensibilidad certifica continuidad ni corrige contractualmente los precios.

### Comprobación temporal y magnitud de utilidad

Entreno en 2004–2013 para estimar 2014; después añado cada año anterior y repito hasta 2023. Hay **diez evaluaciones por serie y método**. Los predictores de precio terminan en t−1 y las etiquetas de ajuste también; no utilizo precio contemporáneo ni futuro. No elijo un nuevo candidato a partir de estos errores.

| Ámbito/objetivo | Media histórica | Crecimiento propio | Precio, dos rezagos | Propio + precio |
|---|---:|---:|---:|---:|
| Guatemala, superficie | 4.249 | 4.760 | 4.540 | 4.654 |
| Guatemala, producción | 9.838 | 9.939 | 10.339 | 11.225 |
| Mundo, superficie | 2.241 | 1.882 | 1.874 | 1.767 |
| Mundo, producción | 3.201 | 3.035 | 1.425 | 1.685 |

MAE en **puntos logarítmicos**, `100 × media(|g observado − g estimado|)`; menor es mejor. No es WAPE ni porcentaje del volumen en toneladas. Un punto log aproxima un punto porcentual de crecimiento solo para variaciones pequeñas.

En el mundo, precio solo reduce el MAE frente a la media **16.36 % en superficie y 55.46 % en producción**. Al añadirlo al crecimiento propio, la reducción es 6.10 % y 44.50 %, respectivamente. En Guatemala, precio solo empeora la media 6.86 %/5.10 %; añadirlo al crecimiento propio mejora apenas 2.21 % superficie, aún peor que la media, y empeora 12.94 % producción. No justifica una regla local de expansión.

La evaluación utiliza las **versiones finales publicadas**, sin reconstruir revisiones o fechas de disponibilidad de FAOSTAT. No está comprobado que la cosecha t−1 se conociera al inicio de t. Es un diagnóstico temporal retrospectivo condicional, no un backtest operativo ni una evaluación nueva ciega. Los diez errores pueden depender entre sí. Las mejoras mundiales no garantizan precisión futura.

### Heterogeneidad entre países productores

Guatemala y cinco pares muestran diferencias descriptivas de asociación, con veinte años por país y objetivo. Viet Nam es el único de esos seis países que conserva positivos los coeficientes de precio a uno y dos años para área cosechada y producción en ambos bloques y al omitir cada año. En el modelo con historia propia y precio, sus coeficientes completos p1/p2 son 0.211/0.057 para área y 0.234/0.117 para producción. Las variaciones de signo en otros países impiden trasladar el patrón mundial como regla nacional uniforme.

En la retrospectiva 2014–2023, propia+precio reduce el MAE frente a media histórica 32.3 % en área y 26.6 % en producción de Viet Nam. En Guatemala empeora 9.5/14.1 %, y también empeora en Indonesia, Bolivia, Nepal y Kenya; entre esos países, el deterioro se sitúa entre 7.1 y 53.8 % según objetivo. Son puntos logarítmicos de error del crecimiento comparados relativamente, no ahorro ni volumen producido. No hay prueba de diferencias causales entre ecuaciones ni de disponibilidad histórica de FAOSTAT.

La rejilla de resultados conserva 420 celdas (seis países y World, veinte años, tres elementos), 54 con flags no A que mantengo con revisión, sin excluir por flag. Las 27,648 originales y sus unidades/flags son trazables; conservo las 21 filas 2001–2003 del panel como antecedentes fuera de muestra. La recomendación es considerar heterogeneidad de competidores en escenarios de margen, sin usar los coeficientes como elasticidad causal, plazo agronómico o regla local de expansión. Método, estabilidad, sensibilidad y pruebas independientes están en el [informe entre países](oferta-paises-serie-III.md).

### Causalidad, decisión y evaluación gerencial

Un incentivo de precio podría acompañar siembra, renovación, insumos o ampliación de capacidad, con cosecha posterior. El [caso histórico de Tailandia descrito por FAO](https://www.fao.org/4/x0513e/x0513e24.htm), apartado Production, muestra que calendario, socas, políticas, capacidad y clima acompañan esos ajustes. Motiva examinar rezagos; no demuestra que Guatemala responda a dos años.

La precedencia temporal no identifica causa: el futuro puede anticipar oferta esperada, la oferta puede afectar precio y factores persistentes pueden relacionarse con ambos. No hay shock exógeno identificado, experimento, instrumento validado ni contrafactual que separe esos canales. No presento una prueba Granger como prueba causal. El área es cosechada, no nueva siembra; el año publicado no fija cuándo se tomó la decisión. El futuro nominal no es el precio neto recibido por el productor, y faltan inflación/moneda, costos, márgenes de cultivos alternativos y expectativas. La agregación mundial puede ocultar respuestas nacionales opuestas.

**Conclusión económica:** la señal mundial respalda parcialmente un ajuste de oferta diferido ante incentivos, coherente con cultivo perenne e inversión que necesita tiempo. La correlación y la mejora predictiva aportan evidencia al mecanismo; no bastan para fijar su elasticidad causal o afirmar que cada país responde igual. El precio internacional puede ser un indicador incompleto del margen local, por lo que la debilidad de la señal de Guatemala no prueba ausencia de respuesta económica.

**Recomendación:** evaluar expansión según margen esperado de varias zafras y costo de oportunidad, incorporando el escenario de que competidores aumenten oferta después de un periodo favorable. Un repunte puntual no basta para asumir ingresos elevados durante toda la inversión. La hipótesis de moderación posterior del precio es condicional a demanda y demás determinantes; no es un pronóstico calculado. Para Guatemala, los coeficientes mundiales no fijan la cantidad de superficie que conviene ampliar. La utilidad cuantificada sigue siendo reducción retrospectiva de error agregado; no hay ahorro, ingreso ni beneficio causal de Santa Ana estimado.

Para una decisión propia se necesitan fechas de siembra/renovación/cosecha por parcela, precio esperado al decidir y precio neto recibido, costos/márgenes alternativos, clima/agua y capacidad. Esa captura permitiría contrastar un mecanismo y buscar variación exógena; añadir controles por sí solo no asegura causalidad. La continuidad de contratos está pendiente de certificación.

Certeza alta sobre trazabilidad y orientación computacional comprobadas; moderada y condicionada para la asociación mundial, insuficiente para una regla local o un efecto causal. El inciso está respondido con esos límites; los cuatro incisos de Serie III tienen desarrollo analítico.

### Evidencia y reproducción

[Notebook 17](../notebooks/17_oferta_precio_serie3.ipynb), [módulo](../scripts/analizar_oferta_serie3.py), [pruebas unitarias](../tests/unitarias/test_oferta_serie3.py), [contraste independiente](../tests/integracion/test_oferta_serie3_resultados.py) y [fuentes](fuentes-precios/indice.md). Requiere la vista auditada del notebook 13 y `Sugar_data.csv`. En `outputs/serie3_oferta/` conservo promedios, panel/flags, exclusiones con motivos, todas las correlaciones, ajustes, omisiones, predicciones, métricas y figuras; fuera de Git. Conservo las huellas de entrada.

```powershell
python -m nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=600 notebooks/17_oferta_precio_serie3.ipynb
python -m pytest tests/unitarias/test_oferta_serie3.py tests/integracion/test_oferta_serie3_resultados.py -q
```

Cinco pruebas específicas contrastan conservación, crudos, unidades y flags, orientación de rezagos, coeficientes conocidos, invariancia a objetivos futuros y reconstrucción QR de todos los ajustes/predicciones y errores. Verifican implementación, sin convertir asociación en identificación causal.
