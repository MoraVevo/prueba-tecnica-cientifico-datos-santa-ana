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
- Ficha oficial Data.gov/USDA dice que `T_SPACRE` es libras de azúcar por acre; PDF dice toneladas por acre. Se adopta la unidad de USDA, explicada al inicio de README. Perfil inicial de `TRS_TON`: 10,485 celdas tienen dos componentes separados por espacios. Preservando el prefijo y usando el componente final como candidato, 29,317/29,340 filas positivas completas coinciden con `TCA × TRS_TON` dentro de 1 % (mediana del ratio 0.999975); 23 observaciones quedan para revisar y el prefijo sigue sin explicación.
- El CSV tiene 29,529 registros y 15 campos físicos: 12 variables del ensayo y tres columnas auxiliares sin nombre; la última contiene seis notas sueltas. Se separan de las mediciones en el notebook. El diccionario de las notas tiene un fragmento truncado `T_SPACRE, ons of sugar per acre`; se conserva como detalle de calidad del CSV y se usa la unidad de la ficha oficial USDA.
- Creado `scripts/descargar_serie1.py`, que descarga la versión oficial a `data/raw/` y valida SHA-256. Creado `notebooks/01_revision_fuente_y_unidades.ipynb`, ejecutado completo sin error. README documenta la discrepancia, procedencia y pasos de instalación; `requirements.txt` fija el entorno.
- Reproducibilidad verificada desde un `.venv` limpio con Python 3.13.14: instalación completa desde `requirements.txt`, `pip check` sin dependencias rotas y notebook ejecutado con el kernel local del entorno.

## 2026-10-19: inicio de perfil EDA de Serie I

- Se perfilaron los marcadores faltantes: 175 en `T_SPACRE`, 91 en `TRS_TON`, 166 en `TCA`, 3,533 en `POPN`, 198 en `MSTWT` y 16,861 en `FIBER`. Las columnas auxiliares contienen dos campos completamente vacíos y seis anotaciones en el tercero.
- Se identificaron 126 copias extra de filas idénticas. Una clave candidata `(CLONE, YEAR, STAGE, LOC, CROP, REP)` agrupa 476 filas repetidas; 112 grupos muestran mediciones distintas. No se deduplicó porque la unidad experimental no está confirmada.
- Mediana descriptiva de T_SPACRE por CROP: 10,100.7; 9,236.5; 7,862.5; 6,819.0; 6,772.5 lb/acre para CROP 0–4. El grupo CROP 4 solo tiene 84 observaciones y hay cobertura desigual por etapa; no interpretar como efecto causal.
- Creado y ejecutado `notebooks/02_perfil_eda_inicial_serie1.ipynb`. Se conservó `TRS_TON` crudo y el prefijo de las celdas compuestas no se interpretó.
- Creado `scripts/etl_serie1.py` y ejecutado. Produce `data/processed/serie1_etl_provisional.csv`, `serie1_resumen_calidad.json` y `serie1_filas_revision.csv`, todos locales e ignorados por Git. Mantiene cada valor crudo junto al parseo numérico, clasifica `TRS_TON`, renombra las auxiliares y marca duplicados sin borrarlos ni imputar faltantes. Retiene los 29,529 registros; 10,682 se incluyen además en el subconjunto de revisión y 23 presentan una relación dimensional fuera del 1 %. No hubo errores al parsear las columnas simples. La preferencia del usuario de guardar aparte cualquier exclusión futura se registró en `AGENTS.md`; aún no se excluye ninguna fila.
- Primer commit local creado con los archivos de código y documentación del hito `Inicia ETL y EDA de Serie I`. Verificado que los datos y el PDF quedan ignorados.
- El usuario pidió configurar GitHub. Creado el repo privado `https://github.com/MoraVevo/prueba-tecnica-cientifico-datos-santa-ana`, configurado como `origin` y enviado el commit inicial a `main`. Verificada privacidad, rama remota, archivos versionados y árbol de trabajo limpio. No se añadieron colaboradores.
- Creado `.gitignore` para excluir PDF confidencial, datos crudos, entornos, secretos y salidas; inicializado Git en `main`. No se hizo commit ni push.

## 2026-10-19: investigación del prefijo de TRS_TON

- Se comparó el CSV original con el XLSX publicado por USDA (recurso Figshare `49874103`); ambos contienen celdas `TRS_TON` con el patrón de prefijo más valor decimal. El XLSX se descargó solo en `data/raw/`, carpeta ignorada por Git.
- Las 10,485 celdas compuestas tienen dos dígitos en el prefijo y tres decimales en el componente final. Se ubican en 2010–2019 y en diez clones; no aparecen en 2020–2021. Los prefijos recorren `00`–`99` y no muestran asociación lineal relevante con las variables de respuesta ni con año, cultivo, réplica o etapa.
- La ficha USDA y el artículo técnico del programa describen los rasgos y el diseño experimental, pero no definen el token prefijo. `REP` ya es una columna separada y representa la réplica; el token `79` no debe confundirse con ella. El componente final sí reproduce la relación dimensional de `T_SPACRE` para el ejemplo examinado.
- Decisión prudente: significado exacto sigue sin resolver. Se considera posiblemente un código auxiliar o residuo de una estructura histórica/exportación, sin afirmar que sea número de parcela ni una medida biológica. Conservar valor crudo y prefijo; usar el sufijo solo como candidato de TRS; no modelar ni monetizar el prefijo. Evidencia, ejemplo y código reproducible en `docs/interpretacion-serie-I.md`.
- Fuentes consultadas: ficha oficial [USDA/Data.gov](https://catalog.data.gov/dataset/louisiana-sugarcane-yield-data-2010-2021-collected-for-the-louisiana-variety-development-p) y artículo de Shahi et al. (2025), [The Plant Genome](https://acsess.onlinelibrary.wiley.com/doi/10.1002/tpg2.20545). Ninguna fuente pública consultada asigna significado al prefijo.

## 2026-10-19: simplificación y español en el ETL

- Se tradujeron al español los comentarios, docstrings, mensajes y textos del reporte JSON. Se conservaron los nombres originales de columnas de la fuente para no alterar el esquema.
- Se reorganizó `scripts/etl_serie1.py` en pasos legibles: validar/cargar fuente, convertir mediciones, marcar alertas, resumir calidad y guardar resultados. No se añadieron comportamientos para casos hipotéticos; la lógica de faltantes, formatos y alertas corresponde a valores presentes en el archivo.
- Se volvió a ejecutar el ETL: 29,529 filas preparadas, 10,485 celdas `TRS_TON` con dos componentes, 29,317/29,340 relaciones dentro del 1 % y 10,682 filas para revisión. Los CSV provisional y de revisión conservaron exactamente sus hashes previos, confirmando que la reorganización no cambió sus resultados. El JSON ahora presenta claves y decisiones en español.
- Se añadió a la skill `prueba-santa-ana` la preferencia del usuario: código y explicaciones en español, con nombres originales de fuente/API cuando corresponda; priorizar parsimonia y eliminar complejidad para escenarios no presentes.
- Verificación: `py_compile` del ETL, ejecución completa del ETL y `git diff --check` sin errores. La skill también pasó `quick_validate.py` (`Skill is valid!`).
