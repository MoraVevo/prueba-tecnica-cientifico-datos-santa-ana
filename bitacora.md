# Bitácora de decisiones y verificación

## 2026-10-19: inventario inicial de fuentes

- Solicitud del usuario: conocer los datasets, su estructura temporal y si necesitan merges antes de empezar a construir análisis.
- Se revisaron el PDF, metadatos y listas de archivos de las cuatro fuentes públicas de Kaggle. Se leyeron encabezados y primeras filas mediante HTTP Range, hasta 4096 bytes por archivo, de campo, dos archivos de caldera, su diccionario, FAOSTAT completo y Sugar_data.csv. No se cargaron ni auditaron los datasets completos.
- Decisión de trabajo propuesta: conservar las fuentes separadas inicialmente. El cruce principal responde a producción anual por país frente a precios con frecuencia/rezagos compatibles; no hay una clave común de negocio entre fincas de Louisiana, una caldera china y producción nacional.
- Suposiciones evitadas: considerar los dos archivos de caldera como dos plantas o periodos distintos; anexar versiones alternativas de FAOSTAT; confundir ausencia de columna Year con ausencia de tiempo en FAOSTAT; tratar CROP como año calendario; asignar unidades de T_SPACRE sin verificar.
- Uso de IA: el asistente organizó el inventario. Las afirmaciones sobre nombres de columnas se contrastaron con bytes reales de los archivos; las descripciones con las APIs de Kaggle y, para campo, USDA. Se limita expresamente la evidencia a las muestras observadas.
- Discrepancia detectada: PDF expresa T_SPACRE en toneladas/acre, pero Kaggle y USDA lo describen en libras/acre. Queda pendiente resolverlo con documentación y coherencia numérica del archivo completo antes de cualquier cálculo económico.
- Evidencia y pendientes detallados: `docs/inventario-datasets.md`. No hay todavía resultados de modelos, auditorías completas ni decisiones definitivas de algoritmos.

## 2026-10-19: interpretación de las columnas de Serie I

- El usuario pidió una explicación de cada campo y de su lógica económica antes de construir el análisis.
- Explicación guardada en `docs/interpretacion-serie-I.md`: variables de diseño del ensayo, producción y calidad; relación conceptual TCA × TRS; lectura económica de los costos referenciales; y chequeos pendientes.
- Verificación externa inicial: ficha USDA/Data.gov y panel de avance de LSU. En ese momento se mantuvo abierta la discrepancia de unidad, pendiente de auditar el archivo completo; la decisión final quedó registrada en la sección de verificación posterior.
- El diccionario del PDF solo confirma el número de población de tallos; no detalla su denominador/escala, ni la especificación completa del diseño REP. No inferir tallos por acre, randomización/bloques ni unidad experimental hasta inspeccionar el archivo y documentación técnica.
- El análisis económico descrito es una contribución parcial con los supuestos entregados, no una utilidad neta completa; fibra podría afectar extracción y bagazo pero el dataset no contiene las magnitudes para monetizarlo por sí solo.

## 2026-10-19: verificación y decisión de unidad de T_SPACRE

- El usuario autorizó verificar la discrepancia y preparar el README, requirements y elementos necesarios para empezar Serie I. Está de acuerdo en usar USDA si la discrepancia se confirma.
- Contraste completo: descargado el recurso oficial `https://ndownloader.figshare.com/files/49874100` (1,950,511 bytes) y la copia Kaggle del PDF; ambos son byte por byte idénticos con SHA-256 `5e7b13de6bda8aed51479c5fdfc3de4a28e71ccbb45e4761b6688a34b7cff4b0`.
- Ficha oficial Data.gov/USDA dice que `T_SPACRE` es libras de azúcar por acre; PDF dice toneladas por acre. Se adopta la unidad de USDA, explicada al inicio de README. En el valor fuente de `TRS_TON`, 10,485 celdas tienen dos componentes separados por espacios. El análisis usa el componente final en la columna numérica `TRS_TON` y conserva el prefijo aparte; 29,317/29,340 filas positivas completas coinciden con `TCA × TRS_TON` dentro de 1 % (mediana del ratio 0.999975); 23 observaciones quedan para revisar y el prefijo sigue sin explicación.
- El CSV tiene 29,529 registros y 15 campos físicos: 12 variables del ensayo y tres columnas auxiliares sin nombre; la última contiene seis notas sueltas. Se separan de las mediciones en el notebook. El diccionario de las notas tiene un fragmento truncado `T_SPACRE, ons of sugar per acre`; se conserva como detalle de calidad del CSV y se usa la unidad de la ficha oficial USDA.
- Creado `scripts/descargar_serie1.py`, que descarga la versión oficial a `data/raw/` y valida SHA-256. Creado `notebooks/01_revision_fuente_y_unidades.ipynb`, ejecutado completo sin error. README documenta la discrepancia, procedencia y pasos de instalación; `requirements.txt` fija el entorno.
- Reproducibilidad verificada desde un `.venv` limpio con Python 3.13.14: instalación completa desde `requirements.txt`, `pip check` sin dependencias rotas y notebook ejecutado con el kernel local del entorno.

## 2026-10-19: inicio de perfil EDA de Serie I

- Se perfilaron los marcadores faltantes: 175 en `T_SPACRE`, 91 en `TRS_TON`, 166 en `TCA`, 3,533 en `POPN`, 198 en `MSTWT` y 16,861 en `FIBER`. Las columnas auxiliares contienen dos campos completamente vacíos y seis anotaciones en el tercero.
- Se identificaron 126 copias extra de filas idénticas. Una clave candidata `(CLONE, YEAR, STAGE, LOC, CROP, REP)` agrupa 476 filas repetidas; 112 grupos muestran mediciones distintas. No se deduplicó porque la unidad experimental no está confirmada.
- Mediana descriptiva de T_SPACRE por CROP: 10,100.7; 9,236.5; 7,862.5; 6,819.0; 6,772.5 lb/acre para CROP 0–4. El grupo CROP 4 solo tiene 84 observaciones y hay cobertura desigual por etapa; no interpretar como efecto causal.
- Creado y ejecutado `notebooks/02_perfil_eda_inicial_serie1.ipynb`. Se conservó `TRS_TON` crudo y el prefijo de las celdas compuestas no se interpretó.
- Creado `scripts/etl_serie1.py` y ejecutado. Produce `data/processed/serie1_etl_provisional.csv`, `serie1_resumen_calidad.json` y `serie1_filas_revision.csv`, todos locales e ignorados por Git. Mantiene cada valor crudo junto al parseo numérico, clasifica `TRS_TON`, renombra las auxiliares y marca duplicados sin borrarlos ni imputar faltantes. Retiene los 29,529 registros; 10,682 se incluyen además en el subconjunto de revisión y 23 presentan una relación dimensional fuera del 1 %. No hubo errores al parsear las columnas simples. aún no se excluye ninguna fila.
- Primer commit local creado con los archivos de código y documentación del hito `Inicia ETL y EDA de Serie I`. Verificado que los datos y el PDF quedan ignorados.
- El usuario pidió configurar GitHub. Creado el repo privado `https://github.com/MoraVevo/prueba-tecnica-cientifico-datos-santa-ana`, configurado como `origin` y enviado el commit inicial a `main`. Verificada privacidad, rama remota, archivos versionados y árbol de trabajo limpio. No se añadieron colaboradores.
- Creado `.gitignore` para excluir PDF confidencial, datos crudos, entornos, secretos y salidas; inicializado Git en `main`. No se hizo commit ni push.

## 2026-10-19: investigación del prefijo de TRS_TON

- Se comparó el CSV original con el XLSX publicado por USDA (recurso Figshare `49874103`); ambos contienen celdas `TRS_TON` con el patrón de prefijo más valor decimal. El XLSX se descargó solo en `data/raw/`, carpeta ignorada por Git.
- Las 10,485 celdas compuestas tienen dos dígitos en el prefijo y tres decimales en el componente final. Se ubican en 2010–2019 y en diez clones; no aparecen en 2020–2021. Los prefijos recorren `00`–`99` y no muestran asociación lineal relevante con las variables de respuesta ni con año, cultivo, réplica o etapa.
- La ficha USDA y el artículo técnico del programa describen los rasgos y el diseño experimental, pero no definen el token prefijo. `REP` ya es una columna separada y representa la réplica; el token `79` no debe confundirse con ella. El componente final sí reproduce la relación dimensional de `T_SPACRE` para el ejemplo examinado.
- Decisión prudente: significado exacto sigue sin resolver. Se considera posiblemente un código auxiliar o residuo de una estructura histórica/exportación, sin afirmar que sea número de parcela ni una medida biológica. Por decisión analítica, se conserva el valor completo en `TRS_TON_raw`, el prefijo como texto en `TRS_TON_prefijo_sin_interpretar` y el sufijo numérico en `TRS_TON`, para aislarlo de métricas y modelos sin perder información de origen. Evidencia, ejemplo y código reproducible en `docs/interpretacion-serie-I.md`.
- Fuentes consultadas: ficha oficial [USDA/Data.gov](https://catalog.data.gov/dataset/louisiana-sugarcane-yield-data-2010-2021-collected-for-the-louisiana-variety-development-p) y artículo de Shahi et al. (2025), [The Plant Genome](https://acsess.onlinelibrary.wiley.com/doi/10.1002/tpg2.20545). Ninguna fuente pública consultada asigna significado al prefijo.

## 2026-10-19: simplificación y español en el ETL

- Se tradujeron al español los comentarios, docstrings, mensajes y textos del reporte JSON. Se conservaron los nombres originales de columnas de la fuente para no alterar el esquema.
- Se reorganizó `scripts/etl_serie1.py` en pasos legibles: validar/cargar fuente, convertir mediciones, marcar alertas, resumir calidad y guardar resultados. No se añadieron comportamientos para casos hipotéticos; la lógica de faltantes, formatos y alertas corresponde a valores presentes en el archivo.
- Se volvió a ejecutar el ETL: 29,529 filas preparadas, 10,485 celdas `TRS_TON` con dos componentes, 29,317/29,340 relaciones dentro del 1 % y 10,682 filas para revisión. Los CSV provisional y de revisión conservaron exactamente sus hashes previos, confirmando que la reorganización no cambió sus resultados. El JSON ahora presenta claves y decisiones en español.
- Se añadió a la skill `prueba-santa-ana` la preferencia del usuario: código y explicaciones en español, con nombres originales de fuente/API cuando corresponda; priorizar parsimonia y eliminar complejidad para escenarios no presentes.
- Verificación: `py_compile` del ETL, ejecución completa del ETL y `git diff --check` sin errores. La skill también pasó `quick_validate.py` (`Skill is valid!`).

## 2026-10-19: separación analítica del prefijo de TRS_TON

- Decisión de negocio del usuario: mantener el valor fuente completo para trazabilidad, pero evitar que el prefijo sin significado confirmado contamine métricas o modelos. El ETL conserva el texto fuente en `TRS_TON_raw`, el prefijo como texto en `TRS_TON_prefijo_sin_interpretar` y el componente numérico final en `TRS_TON`.
- No se eliminaron filas ni datos del origen. El prefijo no se interpreta ni se incluye como variable agronómica; su significado sigue pendiente de confirmación documental.
- Se actualizaron el ETL, los notebooks de auditoría y perfil, el README y los documentos de interpretación/estado. Ambos notebooks se ejecutaron sin errores. El ETL preparó 29,529 filas, mantuvo 10,485 prefijos y encontró 29,317/29,340 relaciones dimensionales dentro del 1 %.

## 2026-10-19: exclusión analítica de copias exactas

- Decisión del usuario: deduplicar las copias idénticas y conservarlas aparte en un DataFrame/archivo de excluidos con el motivo de exclusión.
- `scripts/etl_serie1.py` mantiene intacto el CSV fuente, conserva la primera aparición de cada fila exacta y excluye las 126 copias adicionales del dataset analítico. Las guarda en `data/processed/serie1_filas_excluidas.csv`, con `FILA_CSV` y `MOTIVO_EXCLUSION`.
- Los 29,403 registros analíticos se escriben en `serie1_etl_provisional.csv`. Las 224 filas que quedan en 112 grupos con claves candidatas repetidas y mediciones distintas siguen en el conjunto analítico y se marcan para revisión; no se promedian ni se eliminan.
- Después de excluir las copias exactas, 29,191 de 29,214 filas positivas completas cumplen la tolerancia dimensional del 1 %; 23 quedan fuera. El conjunto de revisión contiene 10,500 filas.
- Se actualizaron el README, el estado del proyecto y el notebook de perfil para distinguir el análisis de la fuente sin modificar de la salida ETL deduplicada.
- Verificación ejecutada: `py_compile`, ETL y notebook 02 completados sin errores; las comprobaciones confirmaron que las 126 filas excluidas coinciden exactamente con las copias adicionales de la fuente, el motivo está presente en todas y fuente = analíticas + excluidas (29,529 = 29,403 + 126). `git diff --check` no reportó errores. No se hizo commit ni push.

## 2026-10-19: alertas de revisión y parsimonia

- Decisión acordada: el prefijo de `TRS_TON` permanece disponible como información, pero no exige revisar cada fila individualmente. Las alertas se reservan para claves candidatas repetidas, errores de parseo y observaciones fuera de tolerancia dimensional.
- El subconjunto de revisión baja de 10,500 a 247 filas; las 10,415 filas con prefijo siguen en el dataset y el reporte conserva su conteo.
- Se quitó del JSON de calidad el resumen de `T_SPACRE` por `CROP`, porque ya corresponde al notebook de EDA.
- La skill global ahora explicita que la parsimonia aplica a todo el trabajo: análisis, código, documentación, archivos y explicaciones.
- Verificación ejecutada: `py_compile`, ETL, invariantes de salida, `quick_validate.py` (`Skill is valid!`) y `git diff --check` completados sin errores. Resultado: 29,403 filas analíticas, 126 copias excluidas, 247 filas que requieren revisión y 10,415 prefijos conservados como información. No se hizo commit ni push.

## 2026-10-19: auditoría de claves candidatas repetidas

- Solicitud: investigar las 224 filas restantes que comparten combinaciones de `(CLONE, YEAR, STAGE, LOC, CROP, REP)` y decidir si conviene tratarlas en ETL o en análisis.
- Método: en el notebook 02 se retiraron de forma reproducible solo las 126 copias exactas adicionales para perfilar los grupos restantes. Se compararon tamaños, etapas, años, localidades y valores distintos de las seis mediciones; no se usó la clave para eliminar ni agregar registros.
- Resultado: 112 grupos de dos filas (224 filas), todos en etapa 3. Cada par difiere en `T_SPACRE`, `TRS_TON`, `POPN` y `MSTWT`; 111 difieren también en `TCA` y 94 en `FIBER`. En 106 grupos ambas filas tienen mediciones completas y cumplen la relación dimensional dentro del 1 %; en los otros seis una fila no tiene las mediciones necesarias para verificarla. Los pares aparecen en años 2010–2013 y 2020–2021, localidades AFL, SGL y NIB, y solo nueve clones. Dos coinciden con los controles citados en el artículo (HOCP96-540 y L01-299); los otros siete también presentan claves repetidas. Las diferencias no se explican únicamente por el prefijo de `TRS_TON`.
- Contraste documental: el catálogo USDA describe un número variable de repeticiones. Un artículo del programa de desarrollo varietal informa dos repeticiones en etapa 3, pero no explica estas combinaciones repetidas ni identifica otra dimensión para resolverlas. Fuentes: [USDA-ARS/Data.gov](https://catalog.data.gov/dataset/louisiana-sugarcane-yield-data-2010-2021-collected-for-the-louisiana-variety-development-p) y [Shahi et al. (2025)](https://acsess.onlinelibrary.wiley.com/doi/10.1002/tpg2.20545).
- Interpretación y decisión técnica: el hecho cierto es una colisión de clave candidata con mediciones diferentes; la causa no queda establecida. Podría faltar un identificador de ensayo/parcela o existir un problema de origen, pero ninguna explicación se afirma como hecho. La unidad experimental debe verificarse con documentación del programa o del responsable de la fuente.
- Recomendación: mantener las filas y la alerta en ETL; ubicar el análisis en el notebook 02, como auditoría exploratoria de calidad. No promediar ni elegir arbitrariamente un registro. Si se contaran como independientes, estas filas podrían dar peso adicional a un grupo pequeño de clones en los análisis de etapa 3; representan 224/29,403 filas analíticas (0.76 %), pero el efecto en métricas concretas no está cuantificado. Certeza alta sobre la repetición y las diferencias; baja sobre su causa.
- Verificación: el notebook 02 se ejecutó completo con el entorno fijado. No se cambió la regla del ETL, porque no existe una corrección sustentada. `README.md` y `docs/estado.md` describen el hallazgo y el tratamiento provisional. Sin commit ni push.

## 2026-10-19: comparación contextual de claves repetidas

- Solicitud: comparar las dos filas de cada clave repetida con mediciones del mismo clon y ambiente, para evaluar si ambas son compatibles con ese contexto.
- Método: contexto inmediato `CLONE`, `YEAR`, `STAGE`, `LOC`, `CROP`, comparando otras `REP`; se excluyen de la referencia las observaciones que también tienen clave repetida. Para antecedentes, se usan años anteriores del mismo `CLONE`, `STAGE`, `LOC` y `CROP`, excluyendo claves repetidas y requiriendo al menos dos años previos. Por variable se registra cuántas de las dos filas caen dentro del rango histórico observado, su distancia mediana a la mediana histórica en porcentaje y en unidades de IQR. No se combinan las variables relacionadas en un puntaje. Los ceros se conservan como vienen; seis pares tienen `T_SPACRE=0` con `TCA` faltante y no se presume que ese cero sea una medición real ni un marcador de ausencia.
- Cobertura: 109/112 pares no tienen una referencia limpia de otra `REP` en el mismo año y contexto; tres tienen una referencia. Solo 26/112 pares tienen al menos dos años previos no ambiguos; `POPN` solo puede compararse en un par y `FIBER` en 22.
- Resultado: para `T_SPACRE`, ambas filas están dentro del rango previo en 12 pares, una en 10 y ninguna en 4 (26 pares comparables); desviación porcentual mediana por par: 29.5 % y distancia al centro histórico: 0.95 IQR. Para `TRS_TON`: 13/10/3 (26; 10.0 %; 0.76 IQR); `TCA`: 10/10/3 (23; 31.8 %; 0.77 IQR); `MSTWT`: 13/10/3 (26; 15.8 %; 0.97 IQR); `FIBER`: 4/8/10 (22; 20.9 %; 1.80 IQR). La cobertura de `POPN` no permite una conclusión.
- Interpretación: hay pares donde ambas observaciones quedan dentro del rango histórico, pares donde solo una lo hace y pares donde ninguna lo hace. El rango mezcla años con condiciones ambientales distintas y no es una regla de validez; no señala de forma confiable cuál fila conservar. La comparación tampoco resuelve si falta un identificador de ensayo.
- Recomendación e impacto: mantener las filas marcadas y no añadir detección automática basada en distancia. Sin una llave completa, el riesgo de eliminar una observación legítima sigue siendo mayor que el valor de una regla no confirmada. La comparación es evidencia exploratoria, no produce un efecto de negocio cuantificado. Certeza alta en las cifras; baja en su interpretación causal.
- Verificación: análisis reproducible incorporado en el notebook 02 y ejecutado desde el entorno del proyecto; ETL sigue generando 29,403 filas analíticas, 126 excluidas y 247 en revisión. `git diff --check` sin errores. No se hizo commit ni push.


## 2026-10-19: cobertura para el análisis económico de Serie I

- Método: el notebook 02 resume por `CROP` el número de filas, clones, años, localidades y etapas, además de los faltantes de las mediciones. Se reporta también la distribución `STAGE` × `CROP`. El dataset provisional se conserva completo; esta tabla describe cobertura y no estima efectos causales.
- Resultado: `CROP=4` contiene 84 filas, 13 clones, una localidad, tres años y solo observaciones de etapa 5. `FIBER` tiene 16,851 faltantes de 29,403 (57.3 %) y `POPN` 3,533 (12.0 %); `T_SPACRE`, `TCA` y `TRS_TON` tienen menos de 0.7 % de faltantes cada una.
- Verificación externa: el catálogo oficial USDA-ARS define `T_SPACRE` en lb/acre, `TRS_TON` en lb/ton y `TCA` en ton/acre ([ficha USDA-ARS/Data.gov](https://catalog.data.gov/dataset/louisiana-sugarcane-yield-data-2010-2021-collected-for-the-louisiana-variety-development-p)). Esto permite expresar ingreso y costo por acre con los supuestos del PDF; la contribución resultante seguirá siendo parcial porque esos costos no son un estado completo de resultados.
- Decisión metodológica: continuar con una comparación económica de variedades y ciclos, ajustando la interpretación por etapa, año, localidad y cantidad de ensayos. No recomendar el número de cortes usando el promedio general ni el grupo `CROP=4` aislado. Las filas marcadas se conservarán y se evaluará sensibilidad al incluir/excluir temporalmente los pares conflictivos.
- Verificación ejecutada: notebook 02 ejecutado completo desde `.venv`; conteos y faltantes se imprimen en la sección 5. `git diff --check` sin errores sustantivos. No se hizo commit ni push.


## 2026-10-19: primera lectura económica exploratoria de Serie I

- Solicitud y límite acordado: avanzar en el análisis económico, pero reservar una revisión específica para validar cálculos. La ejecución correcta del notebook solo confirma que el código corrió; no valida unidades, fórmula, costos ni interpretación. Se etiquetó toda salida como exploratoria y no se eligieron clones ni ciclos de renovación.
- Método provisional: filtrar `STAGE=5`, excluir solo filas sin `T_SPACRE` o `TCA` para este cálculo, y mantener ceros observados. Fórmula aplicada literalmente: `T_SPACRE × US$0.20/lb − TCA × US$14/ton − US$350/acre − US$1,100/acre si CROP=0`. No se incluyen otros costos y no es utilidad neta. Precio de equilibrio por fila = costos incluidos / `T_SPACRE`; no se calcula si el azúcar por acre es cero.
- Unidades de rendimiento: la ficha oficial USDA-ARS define `T_SPACRE` en lb/acre, `TRS_TON` en lb/ton y `TCA` en ton/acre ([USDA-ARS/Data.gov](https://catalog.data.gov/dataset/louisiana-sugarcane-yield-data-2010-2021-collected-for-the-louisiana-variety-development-p)). La compatibilidad de la tonelada del costo con la tonelada de la fuente sigue pendiente de revisión. También se debe confirmar que el costo de mantenimiento se aplique a cada observación/ciclo como se asumió.
- Salida exploratoria en etapa 5: 14,033 filas con `T_SPACRE` y `TCA` presentes. Por `CROP=0..4`, n = 4,527 / 3,871 / 3,609 / 1,942 / 84; mediana de aporte = -69.60 / 920.99 / 709.60 / 619.20 / 617.68 USD/acre. Fracción de filas con aporte positivo al precio fijo = 40.95 % / 99.46 % / 98.64 % / 97.84 % / 98.81 %. Las medianas de precio de equilibrio son 0.21 / 0.09 / 0.10 / 0.11 / 0.11 USD/lb, respectivamente. Son estadísticas por observación y no representan una trayectoria de una parcela ni una distribución de precios de mercado.
- Soporte: `CROP=4` tiene 84 observaciones, 13 clones, una localidad y tres años; no sostiene una recomendación firme sobre el cuarto corte. Cuatro filas de etapa 5 están marcadas por discrepancia dimensional. Al excluirlas solo como sensibilidad descriptiva, las medianas por cultivo cambian 0.00, +0.22, +0.20, 0.00 y aproximadamente 0 USD/acre. Esta sensibilidad de la mediana no descarta otros efectos en la distribución. Las colisiones de clave con mediciones distintas corresponden a etapa 3 y no se incluyen en este filtro de etapa 5.
- Cuidado de ciclo: aunque los metadatos USDA describen hasta cinco cosechas y el artículo técnico incluye plantía y socas, todavía no se ha confirmado que `YEAR` y las claves disponibles sigan la misma parcela/cohorte para cada CROP. Por eso no se suman medianas de ciclos ni se calcula retorno acumulado. Tampoco se sustituye el precio fijo por futuros No. 11: antes hay que revisar si ese contrato y su calendario son comparables con el valor del PDF. Referencia de diseño experimental: [Shahi et al. (2025)](https://acsess.onlinelibrary.wiley.com/doi/10.1002/tpg2.20545).
- Interpretación provisional: el costo de renovación hace que la mediana de plantía sea negativa bajo los supuestos aplicados, mientras las observaciones de soca tienen medianas positivas. Esto no indica cuándo conviene renovar: son cortes no emparejados y la etapa 5 no necesariamente representa variedades comerciales disponibles en Santa Ana. El uso razonable por ahora es una señal para investigar, no una decisión.
- Estructura: se separó esta evaluación económica del perfil de calidad; el cálculo y la comparación por ambiente viven ahora en `notebooks/03_analisis_economico_serie1.ipynb`, y `notebooks/02_perfil_eda_inicial_serie1.ipynb` queda enfocado en calidad y cobertura.
- Verificación ejecutada: notebook 03 corrido con `.venv`; las celdas imprimen explícitamente que la ejecución no constituye validación. No se realizó revisión independiente de fórmula ni costos. Sin commit ni push.


## 2026-10-19: comparación relativa por ambiente y límite de cohortes

- Método: para cada clon en etapa 5 se calculó la mediana de aporte parcial por `CROP`, `YEAR` y `LOC`; se comparó contra la mediana de clones del mismo ciclo/año/localidad. Se presenta mediana de diferencias ambientales, dispersión IQR, proporción de ambientes sobre la mediana y soporte de años/localidades. Se resume primero cada clon-ambiente para que las repeticiones no multipliquen su peso en la referencia. Es una pantalla descriptiva, no un ajuste causal ni una selección automática.
- Hallazgo de identificadores: 4,233 de 5,887 combinaciones `(CLONE, STAGE, LOC, YEAR, REP)` en etapa 5 aparecen con más de un `CROP`. Esto no prueba que compartan parcela; muestra que la llave visible no identifica por sí sola una trayectoria única. No se interpreta `YEAR-CROP` como año de plantación y no se suman márgenes de cortes separados.
- Candidatos que merecen revisión, no recomendación: `HoCP 14-885` destaca en las comparaciones relativas de plantía y CROP 2–3, aunque CROP 3 tiene un solo año; `L 01-299` cuenta con 10 años y 12–14 localidades en cada uno de CROP 1–3; en CROP 0, tiene 11 años y se ubica sobre la mediana de ambiente en esos ciclos; `Ho 12-615` tiene evidencia entre 3 y 6 años en CROP 0–3 y diferencias medianas positivas frente al ambiente. `L 01-283` y `HoCP 09-804` también presentan señales favorables en ciertos ciclos. No se reduce a tres porque falta revisar validación económica, estabilidad y estado comercial, además de transferencia a Santa Ana.
- Contraste de estado varietal: fuentes oficiales USDA-ARS/LSU reportan `HoCP 14-885` como liberada para productores de Louisiana en 2021, y el artículo de liberación la compara con `L 01-299`; la guía de LSU lista `L 01-299`, `L 01-283` y `HoCP 09-804` entre variedades plantadas en Louisiana. Esto solo sirve como contexto de liberación/uso regional, no como evidencia de adaptación a Guatemala. Fuentes: [USDA-ARS, liberación HoCP 14-885](https://www.ars.usda.gov/research/publications/publication/?seqNo115=384112), [guía LSU de variedades](https://www.lsuagcenter.com/articles/page1588964225077).
- Verificación: notebook 03 ejecutado completo; notebook 02 conserva perfil, auditoría y cobertura. La sintaxis de la nueva celda se corrigió tras detectarse un error en el primer intento; la ejecución completa posterior concluyó correctamente. La skill global `prueba-santa-ana` incluye ahora la regla de que ejecutar el código no valida por sí solo fórmula/unidades/interpretación. Aún no se ha hecho validación independiente. No se hizo commit ni push.


## 2026-10-19: corrección de alcance y borrador completo de Serie I

- Corrección del usuario: resolver los cuatro apartados con el dataset y los supuestos proporcionados. No buscar datos externos por ahora ni convertir adaptación a Santa Ana, estado comercial o identificador de cohorte en condiciones que impidan concluir. Las limitaciones deben reflejarse en certeza, supuestos y propuesta de captura. Las consultas externas anteriores quedan como historial de contexto, no como requisitos de la recomendación.
- Se descartó la conclusión metodológica anterior de que no era posible comparar rotaciones sin seguimiento de parcelas. Sí se puede comparar la esperanza del aporte de políticas de duración diferente, asumiendo una cosecha/año, costos constantes y renovación inmediata; no se presenta como flujo observado ni efecto causal de una misma parcela. Se utiliza la media para estimar expectativas, en lugar de sumar medianas como si fueran una esperanza.
- Notebook 03: ajuste por referencia L01-299 compartida en corte/año/localidad, política de renovación con renovación cargada una vez y división por duración, escenarios ilustrativos de precio 0.15/0.20/0.25, remuestreo por año, sensibilidad sin ajuste y con alertas incluidas. Se responde con HoCP14-885 a tres cosechas, L01-299 y Ho12-615 a cuatro. El tercer puesto cambia a L01-283 con promedios directos: se comunica certeza menor. Duraciones fuera de la cobertura principal se conservan como sensibilidad, sin afirmar que sean peores.
- Notebook 04: comparación de Ridge, árbol y bosque con validaciones temporales 2019/2020 y test reservado 2021; entradas disponibles antes de la cosecha e historia de años anteriores, referencias históricas y de clon/ambiente reciente. Ridge elegido, desempeño moderado, sensibilidad al entrenamiento con alertas y ejemplo de próxima zafra del archivo (2022). Se informan errores y el fracaso en R² de 2019, sin atribuir una causa externa no observada.
- Notebook 05: cuatro dimensiones agronómicas por variedad, 17 con cobertura, K=2/3/4 y selección de dos perfiles sin grupos de una o dos variedades. Se evita imputar fibra ausente y longevidad sin evidencia para forzar clasificación. Las variedades no elegibles y filas excluidas quedan en archivos con motivo.
- `docs/conclusiones-serie-I.md`: respuestas gerenciales a los cuatro apartados, incluyendo datos propios, ensayos aleatorizados por bloques/sitios y seguimiento de socas, y propuesta de fase para comparar políticas de renovación. Captura/ensayos solo sugeridos, no ejecutados.
- Todo continúa como borrador pendiente de la revisión independiente solicitada. Las comprobaciones de ejecución, formato y dependencias se documentan por separado; no equivalen a validar los cálculos. No se realizó nueva búsqueda ni descarga externa. No se hizo commit ni push.

- Cierre de ejecución del borrador: se ejecutaron los cinco notebooks con kernel explícito que usa `.venv/Scripts/python.exe`; los notebooks nuevos imprimen el intérprete. Se cambió el ejemplo de ejecución a `python -m nbconvert` para invocar el módulo con el intérprete elegido. Las 25 celdas de código finalizan sin salidas de error; el esquema de notebooks es válido. `py_compile`, `pip check`, `git diff --check` y validador de skill sin errores. La figura de segmentos se inspeccionó visualmente. Estas son comprobaciones de ejecución/formato/entorno y no validación independiente de los cálculos. Sin commit ni push.


### Explicación de la selección económica y alcance de renovación

El usuario solicitó entender y poder discutir la elección de variedades, cortes y el uso de acres. Se contrastó la explicación con el código y las tablas existentes del notebook 03; no se cambiaron cálculos ni se realizó la revisión independiente pendiente. El ranking usa 17 variedades con cobertura mínima, promedios de réplicas por ambiente y ajuste aditivo contra L01-299. Acre es una unidad, sin asignación de superficie. Los filtros de cobertura y la referencia son decisiones del análisis, no requisitos del PDF.

Se hizo explícito un límite de la interpretación: las tres duraciones ganadoras son el último corte admitido por cobertura y las extensiones con menos datos aumentan el aporte calculado. Por tanto, no se ha demostrado una caída económica que determine el corte óptimo de renovación; las duraciones son políticas provisionales limitadas por evidencia. Esto debe discutirse antes de presentar una renovación como óptimo demostrado. Se registró también el commit/push ya autorizado y realizado: 1998c00. Estos apuntes documentales quedan sin un nuevo commit.


### STAGE y cobertura de cosechas avanzadas

STAGE es etapa del programa de selección, no etapa de crecimiento ni número de cosecha. Se añadió una sección descriptiva reproducible al notebook 02. En el ETL deduplicado, CROP 4 contiene 84 filas, todas en STAGE 5 y GLENWOOD durante 2019–2021 (27, 27 y 30 filas). HOCP14-885 aparece con CROP 0 desde 2018, CROP 1 desde 2019, CROP 2 desde 2020 y CROP 3 desde 2021; es compatible con truncamiento por el fin del archivo, sin demostrar continuidad de parcela ni duración exacta. L01-299 tiene historia desde 2010, pero CROP 4 solo aparece desde 2019, por lo que la juventud de las variedades no explica todo el desbalance. No se consultaron fuentes externas ni se ajustó una nueva regresión.

Propuesta pendiente de decidir: estudiar aporte operativo por CROP, ajustando por variedad/año/localidad y separando el costo único de renovación. Empezar con efectos por categoría antes de imponer una caída constante; tratar pendientes como asociaciones y extrapolaciones como escenarios. La existencia de menos filas no prueba inviabilidad de una soca.


### Ausencia de CROP 5 y renovación no identificable

Auditoría adicional en notebook 02, sección 7: el CSV original solo contiene CROP 0–4; el ETL no limita ni reinicia CROP. CROP 4 suma 28 combinaciones clon/etapa/localidad/año (84 filas), 18 anteriores al cierre 2021. En 8 de esas 18 aparece CROP 0 al año siguiente; en 25 de las 28 ya aparecen otros cortes el mismo año. Es presencia de variedades en plantaciones de distintas edades, sin una llave que permita afirmar una transición 4→0 de la misma parcela. No se pudo identificar renovación deliberada ni atribuir toda ausencia de CROP 5 al cierre temporal. CROP 5 sería sexta cosecha y no tiene observaciones para contrastar una extrapolación. La regresión económica propuesta sigue sin ajustarse. Conservar distinción entre aporte positivo de la próxima cosecha y mejora del aporte anual de la rotación; únicamente lo segundo justifica prolongarla frente a la política comparada, bajo los supuestos del modelo. No hubo búsqueda externa ni nuevo commit.


### Gráficas económicas solicitadas

Por solicitud explícita se delegó a un agente GPT-6-Luna la elaboración de gráficas. El enunciado pide evidencia y presentación ejecutiva, pero no exige reservar estas visualizaciones para otro apartado; podrán reutilizarse después. El notebook 03 incorpora una celda con dos figuras: ranking de siete mejores aportes ajustados (tres recomendaciones resaltadas y rangos P05–P95 del remuestreo ya existente) y aporte medio anual por duración (extensiones de menor cobertura discontinuas, conteos de años/localidades y plantía negativa visible).

Archivos locales: outputs/serie1_economia_ranking.png y outputs/serie1_economia_duracion.png, ignorados por Git; las figuras quedan embebidas y su código versionable en el notebook. Se inspeccionaron ambas imágenes y se corrigieron centrado de intervalos, visibilidad del aporte negativo y eje de cosechas hasta cinco; no se añaden supuestos ni una nueva regresión. La nota del ranking conserva la sensibilidad del tercer puesto a L01-283 sin ajuste; la figura de duración no afirma un óptimo económico demostrado. La revisión principal corrigió la ruta de exportación para derivarla de la raíz del ETL incluso si outputs aún no existe. Se ejecutaron las seis celdas del notebook 03 con kernel prueba-santa-ana, sin errores. Esta comprobación es de ejecución y presentación, no la validación económica independiente pendiente. Sin nuevo commit/push.


### Claridad de las gráficas económicas y cierre en Git

A petición del usuario se sustituyó la frase genérica sobre superioridad estadística por hechos concretos: L01-299 y HO12-615 tienen estimaciones muy próximas y rangos de remuestreo que se solapan; el tercer puesto cambia sin ajuste ambiental. No se realizó una prueba de diferencias ni se interpreta el solapamiento como una prueba formal.

La figura de duración reemplaza anotaciones flotantes por un panel lateral identificado con nombre y color de cada variedad. Informa el número de cosecha, su CROP y los años/localidades en que se midió ese último corte: HOCP14-885, cosecha 4/CROP3, 1 año y 7 localidades; L01-299, cosecha 5/CROP4, 3 años y 1 localidad; HO12-615, cosecha 5/CROP4, 2 años y 1 localidad. El pie define las líneas continuas y discontinuas. Estos conteos describen la diversidad temporal/geográfica de las mediciones, no la duración de la rotación.

Notebook 03 ejecutado de nuevo (seis celdas, cero errores) y ambas figuras inspeccionadas. Se conserva pendiente la validación económica independiente. El usuario autorizó guardar el avance acumulado de explicación, cobertura y gráficas con el commit «Documenta cobertura de cortes y mejora gráficas económicas». Esta autorización no solicita un nuevo push; comprobar el hash y estado actual con git log/status.


### Verificación externa de STAGE solicitada por el usuario

Se consultaron la ficha oficial USDA/Data.gov y Shahi et al. (DOI 10.1002/tpg2.20545), sección 2.1 y declaración de datos. El artículo enlaza explícitamente al dataset 27248787 y confirma STAGE 2 second line, 3 nursery, 4 infield y 5 outfield. La justificación y fuentes están en docs/interpretacion-serie-I.md. Mantener STAGE 5 para economía/segmentación por diseño y comparabilidad; no tratar otras etapas como errores. El modelo supervisado sigue usando todas las etapas. Se corrigió el texto anterior que decía que la correspondencia exacta no estaba documentada. Solo cambió markdown/documentación; no se ejecutaron modelos ni se alteraron datos o resultados. Sin nuevos datasets, commit ni push.

Git al iniciar esta verificación: commit local 7f0f2d0, último push confirmado 1998c00. Estos cambios de documentación posteriores quedan pendientes de commit.


### Justificación integrada y pendientes de cierre de Serie I

Se incorporó la justificación de usar outfield/STAGE 5 en README, conclusiones y notebook económico. Se diferenció la construcción completa de las cuatro respuestas de su revisión independiente pendiente. Se registraron los criterios de cierre en docs/estado.md: economía/renovación e incertidumbre, ausencia de fuga y evaluación supervisada, coherencia de segmentos/propuesta de ensayos, consistencia documental y reproducción. La regresión económica por CROP sigue siendo una propuesta opcional, necesaria únicamente si se quieren afirmar sus coeficientes o extrapolaciones. No se ajustaron modelos, no se validaron cálculos ni se realizó nuevo commit/push.


### Revisión independiente del punto económico — 2026-10-19

Se recalculó la tabla de decisión desde el ETL, con una reconstrucción aparte de celdas clon/CROP/año/localidad, comparaciones emparejadas frente a L01-299, medias ajustadas por CROP, filtros de cobertura y enumeración de duraciones. Las 198 políticas reconstruidas coincidieron con la salida guardada; la diferencia numérica máxima fue menor a 0.000001 USD/acre/año, atribuible a precisión/redondeo. No se encontró discrepancia aritmética en el cálculo actual.

También se recalcularon los tres escenarios de precio, se incluyeron las cuatro filas Stage 5 marcadas por revisión dimensional y se contrastó un remuestreo independiente por año. Los tres clones/duraciones recomendados se mantienen en los precios ilustrativos; las filas marcadas no mueven las cifras a centavos. La recomendación de tercer lugar sí es sensible al ajuste aditivo: sin él, L01-283 queda por encima de HO12-615. El remuestreo alternativo da conclusiones de duración similares, pero usa solo 12 años y no prueba rangos ni superioridad entre variedades.

La auditoría valida que el código aplica de forma consistente la fórmula declarada; no valida como hechos observados sus supuestos. Se documentaron: una cosecha por año y mantenimiento por cosecha/año, un único costo de renovación por rotación, compatibilidad de la unidad “ton” de TCA con US$14/ton, ajuste aditivo respecto a L01-299, filtro de cobertura elegido por el análisis y carácter descriptivo del remuestreo. El resultado es “sin error aritmético detectado”, no “decisión económica demostrada sin incertidumbre”. Las conclusiones conservan la redacción acordada sobre duraciones iniciales y falta de evidencia para probar un máximo económico.

La revisión quedó inicialmente sin commit ni push.

El usuario pidió dejar explícito que HO12-615 ocupa el tercer puesto solo bajo el ajuste ambiental aditivo; con promedios directos, L01-283 queda por encima. Se aclaró en README, conclusiones y respuesta gerencial del notebook económico antes de guardar este hito.


### Clima, operación del programa y variables por capturar — 2026-10-19

El usuario pidió incorporar al punto 4 de Serie I lo aprendido al revisar los años 2019 y 2020. Se amplió la propuesta de captura para conservar clima por localidad/fecha (lluvia, temperatura, humedad, inundaciones y eventos extremos), cambios de protocolo/cobertura/calendario e interrupciones operativas con fechas y etapa afectada. La finalidad es separar, hasta donde permitan los datos, variación meteorológica de cambios de ejecución y de faltantes.

Se descartó convertir un indicador binario de COVID en explicación causal o feature aislado: en este historial queda confundido con YEAR y no distingue pandemia de clima, cobertura, manejo o medición. Para el análisis retrospectivo se pueden usar condiciones observadas; para un pronóstico previo a cosecha solo variables conocidas al momento de decidir, como clima acumulado o pronósticos ya emitidos. Cambio documental únicamente; no se modificaron datos ni modelos. El usuario pidió guardar esta unidad con un commit y mensaje explícito; no pidió push.


### Granularidad de parcela y disponibilidad de agua — 2026-10-19

El usuario propuso incluir tamaño de parcela, tipo de riego y estabilidad del suministro. Se incorporaron área total y área útil cosechada, sistema/fuente de agua, fechas/volumen aplicado e interrupciones, además de un registro general de eventos externos. La hipótesis de que el riego acompañe mayor productividad es plausible, pero no se presenta como resultado: habría que controlar por localidad, suelo, variedad, manejo y costo; si riego y localidad coinciden, no se separa su efecto. También se aclaró que para predicción solo deben usarse agua/manejo conocidos o planificados en la fecha de decisión. No se modificaron datos ni modelos.


### Interpretabilidad supervisada y revisión de segmentación — 2026-10-19

El enunciado de Serie I exige comparar al menos tres algoritmos e incluir uno interpretable; no exige una descomposición causal. Ridge ya tenía tabla de coeficientes y sección gerencial en el notebook. Se agregó a las conclusiones la lectura del ajuste evaluado en 2021: `CROP` ≈ −802 lb/acre por unidad y `YEAR` ≈ −25 lb/acre por año, condicionados a otras entradas. Se advierte que son asociaciones regularizadas, no pérdidas causales ni regla autónoma de renovación.

Se reconstruyó de forma independiente la segmentación desde el ETL: coinciden las 17 asignaciones exportadas. La selección k=2 (silueta 0.300, tamaños 4/13) sigue la regla de al menos tres variedades por grupo; k=4 apenas supera la silueta (0.302) pero produce un grupo unitario. Se añadió al notebook una prueba reproducible omitiendo una dimensión: ARI frente a la solución completa es 1.000 sin productividad, 0.492 sin calidad, 0.387 sin conservación y 0.130 sin inestabilidad. Esto muestra que los perfiles son sensibles a las variables, especialmente a las últimas tres. El notebook 05 se ejecutó completo sin errores; no se cambiaron datos ni segmentos seleccionados.

### Sesgo temporal de Ridge — 2026-10-19

Se aclaró en las conclusiones y en el notebook 04 por qué la validación temporal alterna entre sobreestimación y subestimación. La tabla ahora calcula `SESGO = predicción − observado` para todos los modelos: Ridge da +2,147.76 lb/acre en 2019 y −1,078.48 en 2020. Se añadió al notebook el promedio de `T_SPACRE` por etapa y el cambio entre años; en las filas modeladas, el objetivo cae 20.6–26.9 % de 2018 a 2019 y rebota 30.4–41.3 % de 2019 a 2020. El desfase de un modelo basado en años previos es una explicación compatible con ese cambio, no causalidad demostrada. Se conserva la cautela: el archivo no permite separar clima, operación, manejo, cobertura y medición, y las claves coincidentes no identifican parcelas pareadas. Notebook reejecutado; validación nbformat y `git diff --check` correctos, cero errores de ejecución.


### Revisión no supervisada: interpretación antes que métricas — 2026-10-19

Por instrucción del usuario se priorizan perfiles comprensibles y utilidad gerencial sobre silueta, Davies–Bouldin o inercia. Primero se guardó el avance anterior en el commit `cdddb7e`, «Explica sesgo temporal del modelo Ridge». La revisión de segmentos es una unidad posterior.

Se detectó que la conservación segunda soca/plantía comparaba medias de ambientes distintos. Se sustituyó por el cociente de medias dentro de los mismos años/localidades para cada variedad: 840 ambientes, con 18–110 comparaciones, 2–12 años y 11–13 localidades por variedad. Se conservan 678 ambientes sin ambos cortes con su motivo; siguen contribuyendo a productividad, calidad y variabilidad. No se afirma seguimiento de parcela ni efecto causal de edad. Se comprobó que las referencias de variabilidad tienen 6–11 clones, sin referencias de un solo clon. Productividad y TRS conservan su significado descriptivo de coberturas diferentes, sin presentarlos como efectos varietales ajustados.

Se mantiene K-means con cuatro entradas y dos perfiles por lectura y parsimonia. Se eliminó la elección automática por máxima silueta y la regla rígida de tres variedades por grupo; K=3/4 aíslan una sola variedad. La silueta de K=2 es 0.254 frente a 0.300 anterior y 0.265 en K=4 actual: no se optimizó la métrica a costa del significado de la conservación. Los perfiles actuales son 5/12 variedades: 7,997/8,376 lb azúcar por acre; TRS 290/277; conservación 75.4/82.6 %; variabilidad del índice 12.1/9.8 puntos porcentuales.

HO05-961 cambia del Perfil 2 al 1: conservación de 83.6 % sin emparejar a 76.0 % con ambientes comunes, con dos años comparables. Ward identifica L99-226 como sensible al algoritmo (una pertenencia distinta). Omitir variabilidad cambia seis asignaciones; se interpreta como otra pregunta de negocio y se conserva la dimensión solicitada. Se muestran casos que no siguen todas las medias del grupo: HOCP96-540 tiene TRS bajo dentro del Perfil 1 y HOCP14-885 conserva alrededor de 75 % dentro del Perfil 2. Las tres recomendaciones económicas se mantienen en el Perfil 2.

Se sustituyó la dispersión de dos ejes por una gráfica de las cuatro dimensiones, números en unidades originales y color estandarizado por columna; se añadió cobertura individual. Se inspeccionó la figura generada y se ejecutó el notebook 05 completo con el kernel del entorno del proyecto. Una reconstrucción independiente mediante cruces de plantía y segunda soca reprodujo las cuatro fórmulas y las 17 pertenencias (diferencia máxima <1e-12); perfiles y métricas son finitos. Los NaN del archivo de ambientes sin par representan cortes ausentes intencionales. Se actualizaron conclusiones, README y estado; los perfiles continúan exploratorios por cobertura, correlación de dimensiones y falta de seguimiento de parcela.

Cierre de esta revisión: cinco notebooks con esquema válido y sin salidas de error guardadas; notebook 05 ejecutado completo y `git diff --check` correcto. Se confirmó el push del commit de Ridge `cdddb7e` a `origin/main`. La revisión no supervisada queda pendiente de un commit propio, con mensaje sugerido «Mejora interpretación y comparación ambiental de segmentos».
