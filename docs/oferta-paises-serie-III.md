# Respuesta anual de oferta al precio: Guatemala y países pares

## Hallazgo

Entre los cinco pares que fijo antes del cálculo, solo Viet Nam muestra coeficientes positivos para ambos rezagos de precio (uno y dos años) en área cosechada y producción, con los cuatro signos positivos en ambos bloques de tiempo y al omitir cualquier año. Los demás países varían según objetivo, rezago o periodo. Guatemala presenta asociación positiva del área con el precio de uno y dos años atrás en la muestra completa, pero el coeficiente de un año cambia de signo por bloque; producción es débil y sensible. El resultado apoya usar escenarios de precios e incentivos de competidores como contexto, no una regla local de expansión.

World mantiene una asociación positiva a dos años para ambos objetivos. Es un agregado, no un país ni una observación independiente. No estimo causalidad, elasticidad causal ni un plazo agronómico. El rezago representa años calendario frente a cotización nominal mundial; no identifica la fecha de decisión de siembra.

## Evaluación gerencial

**Significado.** La asociación con precio no es homogénea entre Guatemala y sus pares. La señal persistente de Viet Nam puede orientar escenarios de reacción competitiva internacional. Las señales de Guatemala no sostienen por sí solas una respuesta predecible: el área es positiva en la muestra larga, aunque la respuesta de un año cambia entre bloques, y producción no conserva un patrón comparable. Una señal ausente o inestable tampoco demuestra ausencia de incentivos.

**Decisión recomendada.** Incluir escenarios de precio e incentivos competitivos al evaluar margen y capacidad. No usar estas regresiones para decidir expansión o superficie. Antes de una inversión, incorporar precio neto esperado en la fecha real de decisión, costos y usos alternativos de tierra, clima/agua y calendario de siembra, cosecha y renovación.

**Impacto medido.** En la evaluación retrospectiva 2014–2023, el error absoluto medio del modelo con historia propia y precio frente a la referencia de la media se redujo 26.6 % en producción y 32.3 % en área de Viet Nam. También bajó en World (47.4 % y 21.1 %). En los otros cinco países comparados, incluido Guatemala, aumentó entre 7.1 % y 53.8 %, según objetivo y país. Es comparación retrospectiva de datos finales, no impacto económico ni desempeño operativo.

**Riesgo y certeza.** Certeza exploratoria y baja para decisiones locales. Solo hay veinte años comunes por ecuación; todos comparten el mismo precio mundial; faltan factores relevantes; FAOSTAT final no certifica qué dato se conocía en cada año. El precio es nominal y no representa margen esperado. No calculo p-valores iid ni intervalos causales. La ausencia de señal no prueba que los productores no respondan a incentivos.

## Diseño y método

Elijo Guatemala y todos los pares de la segmentación III.1: Indonesia, Bolivia (Plurinational State of), Viet Nam, Nepal y Kenya. Son los tres pares estructurales principales y dos referencias secundarias. No agrego países según las correlaciones observadas. Conservo World aparte como contexto agregado.

Modelo área cosechada, ha, y producción, t, por separado. Conservo el rendimiento, kg/ha, como descomposición física, no como tercera medida independiente de oferta. El archivo contiene área cosechada; no infiero superficie sembrada.

El precio anual es el promedio de cierres diarios de los doce meses completos de 2001–2023, en centavos nominales de USD por libra. Contrasto niveles logarítmicos y cambios logarítmicos con precio en 0, 1 y 2 años de rezago. Los modelos OLS que fijo antes del cálculo comparan media, cambio propio previo, precio previo en 1/2 años y cambio propio más precio previo en 1/2 años. El rezago cero es contemporáneo y no representa información disponible antes de producir. Los coeficientes son asociaciones descriptivas de cambios logarítmicos, no estimadores causales.

Cada país usa los mismos años 2004–2023, veinte observaciones por objetivo y especificación. Las ecuaciones quedan separadas para no tratar el mismo precio mundial como varias réplicas independientes. Reviso bloques 2004–2013 y 2014–2023, omisión de un año y sensibilidad a medias mensuales equiponderadas y cierres marcados por OHLC/volumen apartados. Las marcas justifican revisión, no prueban error.

## Resultados

Correlación entre cambios logarítmicos de oferta y cambio logarítmico del precio. Rezago 0 es el mismo año; 1 y 2 son años anteriores.

| País o agregado | Área 0 | Área 1 | Área 2 | Producción 0 | Producción 1 | Producción 2 |
|---|---:|---:|---:|---:|---:|---:|
| Guatemala | −0.39 | 0.22 | 0.31 | −0.39 | −0.21 | 0.00 |
| Indonesia | 0.07 | 0.20 | 0.17 | 0.17 | −0.11 | −0.20 |
| Bolivia (Plurinational State of) | −0.16 | −0.22 | 0.37 | −0.05 | 0.03 | 0.02 |
| Viet Nam | −0.15 | 0.53 | 0.38 | −0.12 | 0.51 | 0.45 |
| Nepal | 0.02 | −0.15 | 0.39 | 0.12 | −0.22 | 0.26 |
| Kenya | 0.01 | 0.18 | −0.15 | −0.10 | −0.06 | −0.18 |
| World, contexto | −0.18 | 0.06 | 0.72 | −0.21 | 0.10 | 0.78 |

En niveles, la correlación logarítmica entre área y precio rezagado un año es 0.70 en Guatemala e Indonesia, 0.61 en Kenya y 0.72 en World; en cambios baja a 0.22, 0.20, 0.18 y 0.06. Esto muestra que niveles y tendencias comunes pueden inflar una asociación que no aparece en cambios.

Coeficientes de precio rezagado uno y dos años en el modelo con cambio propio previo, muestra completa:

| País o agregado | Área: p1 | Área: p2 | Producción: p1 | Producción: p2 |
|---|---:|---:|---:|---:|
| Guatemala | 0.061 | 0.050 | −0.119 | −0.006 |
| Indonesia | 0.038 | 0.022 | −0.020 | −0.059 |
| Bolivia (Plurinational State of) | −0.058 | 0.127 | 0.007 | 0.009 |
| Viet Nam | 0.211 | 0.057 | 0.234 | 0.117 |
| Nepal | −0.044 | 0.099 | −0.081 | 0.081 |
| Kenya | 0.158 | −0.023 | −0.041 | −0.138 |
| World, contexto | 0.014 | 0.099 | 0.025 | 0.132 |

En Viet Nam, ambos rezagos son positivos en ambos bloques. Al omitir un año, el área mantiene p1 entre 0.178 y 0.252 y p2 entre 0.027 y 0.087; producción mantiene p1 entre 0.194 y 0.278 y p2 entre 0.076 y 0.154. Es el signo más estable entre pares, aunque no demuestra que el precio lo haya causado.

En Guatemala, área p1 es 0.07 en 2004–2013 y −0.03 en 2014–2023, mientras p2 sigue positivo (0.03 y 0.10). Producción p1 es negativo en ambos bloques (−0.11 y −0.41), y p2 pasa de −0.05 a 0.03. Al omitir un año, área conserva p1/p2 positivos, pero producción p1 varía entre −0.19 y −0.04 y p2 entre −0.07 y 0.04. Una asociación agregada de área no se traslada a producción ni a todos los periodos.

Bolivia, Indonesia, Nepal y Kenya cambian de signo según objetivo, rezago o bloque; ninguno comparte la respuesta positiva estable de Viet Nam. World sostiene p2 positivo en ambos bloques (área 0.12/0.06; producción 0.14/0.13), pero no reemplaza la comparación entre países. No someto los coeficientes a pruebas de diferencia entre ecuaciones.

Al cambiar el promedio anual por meses equiponderados o cierres sin marcas, la mayor variación absoluta entre coeficientes p1/p2 fue 0.0021. Esto indica poca dependencia de esas construcciones de precio, pero no certifica el enlace de futuros.

## Conservación y límites

Conservo las 27,648 celdas FAOSTAT en outputs/serie3_oferta_paises/celdas_originales_con_motivos.csv con valores, unidades y flags originales. Las seis áreas y World aportan 1,344 celdas fuente; la rejilla común de resultados, 420 (7 áreas/agregados × 20 años × 3 elementos). Las 27,228 celdas fuera de la rejilla quedan en celdas_fuera_analisis.csv con motivo por fila; conteos en conteos_motivos_fuera_analisis.csv. Los motivos pueden coexistir. Conservo aparte las 21 filas de panel 2001–2003 en panel_fuera_muestra.csv.

De las 420 celdas de resultado, 54 llevan un flag distinto de A (E, I o X). En toda la historia 1961–2023 de las siete áreas/agregados seleccionados, 287 celdas llevan flag distinto de A. Las conservo y marco para revisión; no excluyo ninguna por flag. Área objetivo es Area harvested, ha; producción, t; rendimiento, kg/ha. Verifico la identidad física producción = área × rendimiento / 1,000; el residuo logarítmico absoluto máximo fue 0.000008.

No observo precio neto esperado, margen, moneda local/deflactor, costos alternativos, calendario de cultivo, política, clima o agua. Tampoco verifico la fecha de publicación de cada versión FAOSTAT ni el linaje completo de futuros. La evaluación usa diez pruebas anuales 2014–2023 con datos finales; no acredita disponibilidad histórica ni es un test operativo independiente.

## Reproducción

Desde la raíz del proyecto, en PowerShell, ejecutar:

    .venv/Scripts/python.exe -m scripts.analizar_oferta_paises_serie3
    .venv/Scripts/python.exe -m nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=600 notebooks/20_oferta_paises_serie3.ipynb
    .venv/Scripts/python.exe -m pytest tests/unitarias/test_oferta_paises_serie3.py tests/integracion/test_oferta_paises_serie3_resultados.py -q

El script guarda huellas SHA-256 de las dos entradas. Las pruebas reconstruyen conservación de datos, motivos, muestra, rezagos, correlaciones, coeficientes por QR, omisiones, predicciones y métricas por cálculo independiente. No genero figuras porque tablas comparativas comunican directamente los resultados y no hay visualización que revisar.

La conclusión orienta escenarios competitivos en una evaluación económica posterior. No cuantifica retornos de expansión ni una reacción causal para Santa Ana.
