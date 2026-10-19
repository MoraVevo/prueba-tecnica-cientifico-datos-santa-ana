# Estado persistente de la prueba Santa Ana

Última actualización: 2026-10-19, America/Guatemala.

## Solicitud y alcance actual

La prueba técnica de Científico de Datos de Ingenio Santa Ana se desarrolla con la Serie I como punto de partida, manteniendo el análisis reproducible y documentado. El proyecto está en un repositorio privado; no hacerlo público ni invitar evaluadores sin que se defina ese acceso.

El plazo informado para la entrega es de 48 horas. La entrega prevista incluye un ZIP y el repositorio GitHub; el PDF exige ZIP con `.git` y enlace GitHub/GitLab, y especifica que el historial forma parte de la evaluación. La hora de inicio y fecha/hora absoluta de vencimiento aún no se han confirmado.

## Trabajo completado

- Leídas y revisadas visualmente las seis páginas de `Prueba de conocimientos técnicos Científico de Datos.pdf`; extraídos también sus enlaces a datasets.
- Creada la skill global `prueba-santa-ana` en `C:/Users/user/.codex/skills/prueba-santa-ana/`.
- Requisitos de las cinco series, extras, datos, supuestos económicos y entrega guardados en `references/prueba.md` dentro de la skill, con referencias de página.
- Preferencia de acompañamiento de Git y rutina de persistencia guardadas en la skill.
- Inspeccionados metadatos y listado de archivos de las cuatro fuentes de Kaggle y encabezados/primeras filas mediante HTTP Range de seis CSV. Inventario y posibles cruces en `docs/inventario-datasets.md`.
- Iniciada `bitacora.md` con decisiones propuestas, supuestos evitados y verificación del uso de IA durante este inventario.
- Explicación de cada columna de Serie I y su lógica de negocio/económica, con fuentes y alertas metodológicas, en `docs/interpretacion-serie-I.md`.
- Discrepancia de `T_SPACRE` verificada contra el CSV USDA completo. README abre con la decisión de fuente y unidad; se prepararon descargador con checksum y notebook reproducible.

## Resultados y decisiones

- No hay todavía rankings, modelos ni recomendaciones de negocio. Se inició EDA descriptiva de la Serie I; sus cifras son preliminares, con datos crudos y duplicados visibles.
- La serie elegida para empezar es la Serie I. El ETL provisional preserva valores crudos y banderas de calidad. `TRS_TON` contiene solo el valor numérico final; el texto original y el prefijo sin interpretar quedan en campos separados. Falta validar la unidad experimental antes de considerar un dataset limpio final.
- La información es confidencial según el PDF. Se recomienda repositorio privado cuando se configure la entrega.
- Se prioriza profundidad y justificación de decisiones. Las actividades pendientes se documentarán en README y los extras son opcionales.
- Decisión de unidad: PDF describe T_SPACRE en toneladas/acre; ficha oficial USDA lo define en libras/acre. La copia Kaggle y el recurso USDA son idénticos. En 10,485 celdas del valor fuente de `TRS_TON` hay dos componentes numéricos separados por espacios; el ETL conserva el texto original en `TRS_TON_raw`, el prefijo como texto y el componente final en la columna analítica `TRS_TON`. La relación dimensional queda dentro del 1 % en 29,317 de 29,340 filas positivas completas. Quedan 23 observaciones fuera de tolerancia.
- Investigación posterior del prefijo: también está en el XLSX oficial USDA; tiene dos dígitos `00`–`99`, aparece únicamente en 2010–2019 y en diez clones, y no se comporta como una medición agronómica ni como `REP`. No se encontró una definición pública. Podría ser un código auxiliar o residuo de estructura/exportación, pero no se afirma que sea un número de parcela. Mantenerlo crudo y fuera de métricas/modelos hasta obtener confirmación. Ver análisis, fuente técnica y snippet reproducible en `docs/interpretacion-serie-I.md`.
- Perfil crudo de `CROP`: mediana de `T_SPACRE` disminuye de 10,100.7 a 6,772.5 lb/acre entre CROP 0 y 4; CROP 4 solo tiene 84 observaciones y existe desbalance por etapa. Es una asociación descriptiva, no causal.
- Calidad: 126 copias extra de filas completas idénticas. La clave candidata `(CLONE, YEAR, STAGE, LOC, CROP, REP)` reúne 476 filas repetidas, con mediciones distintas en 112 grupos; no eliminar ni agregar todavía. `FIBER` tiene 16,861 faltantes/puntos de 29,529 filas; `POPN`, 3,533.
- FAOSTAT realmente tiene años en columnas Y1961-Y2023: requiere reorganización para obtener país-año. Caldera tiene dos archivos data con iguales encabezados y primeras filas, relación completa por determinar. Sugar_data.csv tiene fecha y OHLC/volumen.
- Cruce principal propuesto: FAOSTAT país-año con precios agregados y rezagados de manera justificada. No unir automáticamente campo, caldera y mercado por compartir fechas o tema.
- Para Serie I, el ingreso bruto por acre se vincularía a `T_SPACRE` y el costo de cosecha/transporte a `TCA`; la contribución es parcial con los costos del PDF. La discrepancia de unidad quedó resuelta a favor de USDA, pero falta confirmar escalas de costos para cerrar cálculos.

## Verificaciones

- PDF: seis páginas, texto extraído y revisión visual de todas ellas.
- SHA-256 del PDF: `d5797133d33baacea0e2e1befc7ee4eb215b64dd8a942567f320324a2d8de67f`.
- Se extrajeron cuatro enlaces de datasets de las anotaciones del PDF y posteriormente se contrastaron sus metadatos. Para Serie I se descargó el CSV completo de la fuente oficial y se validó su SHA-256.
- Serie I: el descargador verificó 1,950,511 bytes y el SHA-256 documentado; el recurso USDA y Kaggle son byte por byte idénticos. Los notebooks 01 (unidad/fuente) y 02 (perfil EDA) se ejecutaron sin errores con 29,529 registros. `scripts/etl_serie1.py` genera CSV provisional, reporte JSON y subconjunto de revisión; conserva todas las filas (0 descartadas), no deduplica ni imputa. `TRS_TON` contiene solo el componente numérico final; `TRS_TON_raw` preserva el texto y `TRS_TON_prefijo_sin_interpretar` conserva el prefijo como texto. Registra 0 errores de parseo en columnas simples, 23 alertas de coherencia dimensional y 10,682 filas marcadas para revisión por prefijos, repetidos u otras alertas.
- Series II y III: solo se inspeccionaron muestras remotas y metadatos; faltan descargas y auditorías completas.
- Entorno limpio de Python 3.13.14 creado con `requirements.txt`; `pip check` no reportó dependencias rotas. El notebook volvió a ejecutarse con el kernel de `.venv` y los paquetes fijados.
- Skill validada con `quick_validate.py`: `Skill is valid!`. Comprobadas las referencias internas y la codificación UTF-8 de los documentos y metadatos; selección automática habilitada por defecto.

## Git: estado actual

- El historial conserva cuatro hitos cronológicos del desarrollo.
- El PDF de la prueba y las carpetas `data/raw/` y `data/processed/` permanecen excluidos de Git.
- Repositorio privado: https://github.com/MoraVevo/prueba-tecnica-cientifico-datos-santa-ana.
- Rama principal `main` con remoto `origin` asociado al repositorio privado.
- Privacidad y rama `main` verificadas en GitHub. No se han invitado evaluadores ni hecho público el repo.
- Antes de la entrega, revisar los archivos versionados, el contenido del ZIP y el acceso de los evaluadores.

## Pendientes y siguiente paso sugerido

- El prefijo de `TRS_TON` fue investigado en CSV/XLSX oficial y fuentes técnicas: continúa sin definición pública. El ETL lo conserva como texto separado de la variable analítica y no lo usa en métricas/modelos. El siguiente paso analítico es ampliar EDA de cobertura, faltantes, rangos y comparaciones por CROP/clon, aclarando unidad experimental y diseño; cualquier exclusión futura debe guardarse aparte con criterio y motivo.
- Aún falta conocer la hora desde la cual se cuentan las 48 horas para fijar el vencimiento exacto. El usuario puede aportar ese dato mientras se avanza en tareas independientes.
- Antes de publicar, decidir cómo dar acceso a los evaluadores sin incumplir la indicación de confidencialidad del PDF; revisar si se puede añadirlos al repositorio privado.
- Priorizar análisis reproducibles y profundos, controlar el alcance y sugerir commits frecuentes que reflejen trabajo real. Repo remoto ya creado y primer commit enviado; el usuario debe definir cómo dar acceso a los evaluadores.
- El README y `bitacora.md` ya documentan la decisión de fuente y el primer análisis reproducible; seguir actualizándolos conforme avance el trabajo.
- Conservar para cada resultado futuro la ruta al notebook/script y el comando que permite reproducirlo, además de decisiones, supuestos, pruebas realizadas y pendientes.
- El ETL quedó reorganizado en funciones breves con comentarios, docstrings, mensajes y reporte en español; se conservaron los nombres de columnas originales. La reorganización produjo exactamente los mismos CSV que la versión anterior. La skill global ahora recoge la preferencia del usuario por parsimonia y eliminar código para escenarios hipotéticos.
