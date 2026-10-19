# Estado persistente — prueba Santa Ana

Actualización: 2026-10-19, America/Guatemala.

## Alcance vigente

- Desarrollar las cuatro respuestas de Serie I con el dataset entregado y los supuestos del PDF. La última corrección del usuario prevalece sobre interpretaciones anteriores: las limitaciones deben modificar certeza y supuestos, sin impedir dar tres variedades, renovación, modelo, segmentos y propuesta de ensayos.
- Por ahora no buscar ni descargar datos externos adicionales. Las búsquedas previas de metadatos/unidades forman parte del historial. El usuario pidió centrar las conclusiones en los datos y supuestos del ejercicio, sin repetir advertencias sobre adaptación a Santa Ana.
- La fórmula económica y sus 198 políticas se reprodujeron en una revisión independiente el 2026-10-19; no se encontró discrepancia aritmética. Esto verifica la implementación frente al método elegido, no demuestra que todos sus supuestos sean los únicos correctos. La revisión independiente del modelo supervisado y de la segmentación sigue pendiente.
- Español en comentarios, docstrings y explicaciones; parsimonia en código, archivos y análisis. Guardar exclusiones con motivos. Sugerir Git en hitos; ejecutar commit/push cuando se autorice.
- Plazo informado: 48 horas; falta confirmar inicio y vencimiento absolutos. PDF exige ZIP con `.git`, sin datasets y enlace GitHub/GitLab. No convertir “lunes siguiente 8:00” en fecha sin referencia.

## Fuente y preparación

- PDF local de seis páginas leído y revisado; requisitos en la skill global `prueba-santa-ana/references/prueba.md`.
- USDA y Kaggle Serie I son idénticos. SHA-256 CSV: `5e7b13de6bda8aed51479c5fdfc3de4a28e71ccbb45e4761b6688a34b7cff4b0`.
- `T_SPACRE` se trata como lb azúcar/acre según USDA, corrigiendo la descripción del PDF. `TCA`: ton caña/acre; `TRS_TON`: lb/ton. El costo se aplica a la tonelada de TCA como supuesto del ejercicio.
- `TRS_TON` analítico es el último componente numérico. Texto crudo y prefijo de dos dígitos se preservan; no hay definición pública confirmada del prefijo y no entra a métricas/modelos.
- Fuente 29,529 filas; ETL 29,403 analíticas + 126 copias exactas adicionales excluidas con motivo. Las 224 filas en 112 pares de claves distintas en mediciones se mantienen marcadas; todas en etapa 3. Otras 23 filas tienen discrepancia dimensional >1 %.
- La investigación contextual no eligió cuál fila de cada par corregir. Se conserva la incertidumbre y se evalúa sensibilidad. No seguir investigando indefinidamente el prefijo/llave como requisito para avanzar.
- CROP 4 tiene 84 filas, 13 clones, una localidad y tres años. Fibra falta en 57.3 % del dataset analítico; no se fuerza su imputación.

## Primer borrador de las cuatro respuestas

### 1. Economía — notebook 03

- Formula aporte anual de rotación: `[suma_cortes(precio × E[azúcar] − 14 × E[caña] − 350) − 1100] / número_cosechas`.
- Una cosecha/año, renovación inmediata, sin descuento ni descanso. Puede estimarse con expectativas por corte sin fingir que sean flujos de una misma parcela.
- Etapa 5; 14,029 filas en escenario principal, 63 conservadas aparte por faltantes/alertas. Promediar réplicas por clon/corte/año/localidad y ajustar respecto a L01-299 en ambientes compartidos. 4,197 de 4,708 celdas emparejadas; las no emparejadas se conservan aparte.
- Para recomendar se exige plantía + dos socas con dos años y dos localidades por corte; se permite tercera soca con igual criterio. CROP 4 y duraciones de menor cobertura se muestran como sensibilidad.
- Tres recomendaciones del modelo de decisión a US$0.20/lb: HOCP14-885, tres cosechas totales, US$727.58/acre/año; L01-299, cuatro, US$632.66; HO12-615, cuatro, US$629.21.
- Precios ilustrativos 0.15/0.20/0.25 USD/lb: se mantienen esas duraciones. Sin ajuste, L01-283 desplaza ligeramente a HO12-615 del tercer puesto. Certidumbre media para L01-299 y media-baja para HoCP14-885/duración y tercer puesto. No afirmar óptimo fuera del horizonte evaluado.
- Remuestreo por año (500): rangos centrales 90 % del aporte de la política elegida ≈652–834, 572–700 y 570–684 USD/acre/año. Frecuencias misma duración: 100 %, 100 %, 98.6 %. No son probabilidades de superioridad real.

### Revisión económica independiente — 2026-10-19

- Se reconstruyeron las celdas elegibles desde el ETL y se recalcularon por separado coberturas, ajuste aditivo frente a L01-299, cosechas consecutivas y aporte anual. Las 198 políticas coincidieron con `serie1_politicas_renovacion.csv`; máxima diferencia por redondeo: menos de 0.000001 USD/acre/año. No se detectó error aritmético en la fórmula implementada.
- Con precios de US$0.15, US$0.20 y US$0.25/lb se conservan las tres variedades y las duraciones seleccionadas; sus aportes cambian sustancialmente. Incluir las cuatro filas Stage 5 marcadas por revisión dimensional no cambia resultados a centavos. Sin el ajuste ambiental, L01-283 desplaza a HO12-615 del tercer puesto: esa elección depende del método de ajuste.
- Un segundo remuestreo independiente por bloques de año da rangos P05–P95 próximos a los publicados y conserva las mismas duraciones en la gran mayoría de las remuestras válidas. El remuestreo usa solo 12 años, no evalúa la probabilidad de que cada variedad ocupe el top 3 y no es una prueba formal de diferencias.
- Límites del supuesto económico: el cálculo trata cada CROP como una cosecha/año, cobra mantenimiento en cada año/cosecha y resta renovación una vez por rotación. Se usan TCA (toneladas de caña/acre) y el costo de US$14/ton con tonelada compatible, como indica el supuesto operativo, aunque el enunciado no especifica el tipo de tonelada. Se denomina aporte parcial, pues faltan otros costos e ingresos.
- El ajuste ambiental es aditivo y toma a L01-299 como referencia en celdas compartidas. Es una forma de estandarización escogida, no una corrección causal o exigida por el enunciado; la sensibilidad sin ajuste cambia el tercer lugar. El filtro de dos años/dos localidades por corte también es una regla analítica, no una garantía estadística.
- Resultado para defensa: no hay un error de cálculo identificado; la recomendación está condicionada a cobertura, ajuste aditivo y costos referenciales. Las duraciones 3/4/4 son políticas iniciales dentro de la cobertura establecida, no máximos económicos demostrados. No estimar certeza de ranking a partir de las frecuencias de duración.

### 2. Predicción — notebook 04

- Tres algoritmos: Ridge interpretable, árbol, bosque. Historial objetivo calculado estrictamente con años anteriores. Entradas: clon, localidad, etapa, CROP, YEAR y medias históricas. No usar TCA/TRS/otras mediciones contemporáneas como predictores de esa zafra.
- Validaciones 2019 y 2020 con entrenamiento en años anteriores; selección por MAE promedio. Ridge elegido (MAE medio 2,405.64). Año final reservado 2021.
- Test 2021 Ridge: MAE 2,144.55 lb/acre, RMSE 2,770.97, R²≈0.25; MAE etapa 5: 1,898.11. Referencia histórica MAE 2,662.69; referencia clon-ambiente reciente ≈2,270.33. Utilidad moderada, no exagerar precisión. Todos los algoritmos fallan en R² 2019.
- Principal: 28,981 registros; 422 exclusiones con motivo. Se conservan ocho ceros fuente. Sensibilidad incluyendo alertas en entrenamiento e historia: MAE≈2,135.10 en la misma prueba limpia.
- Se reajusta elegido hasta 2021 e ilustra entrada/predicción de 2022, sin afirmar que sea una zafra actual o evaluada.

### 3. Segmentos — notebook 05

- 17 variedades de etapa 5 con plantía/dos socas y dos años/localidades por corte. Resto conservado sin segmento por cobertura. Cuatro variables estandarizadas: azúcar, TRS, conservación segunda soca/plantía, variación ambiental relativa centrada por clon/corte.
- Comparar K-means 2/3/4; mayor silueta con al menos tres variedades/grupo: dos grupos, silueta≈0.30.
- Perfil 1, cuatro clones: mayor TRS≈290, menor azúcar≈7,940, conservación≈74 %, más variabilidad≈0.126. HO07-613, HOCP00-950, HOCP96-540, L03-371.
- Perfil 2, trece clones: azúcar≈8,365, TRS≈278, conservación≈82 %, menor variación≈0.099. Incluye las tres recomendadas. Segmentos complementan economía, no son ranking.

### 4. Datos propios — documento de conclusiones

- `docs/conclusiones-serie-I.md` responde los cuatro puntos y propone seguimiento de parcela/cohorte, variables de ambiente/manejo/calidad/costos, causas de retiro y ensayo aleatorizado por bloques/sitios seguido durante socas.
- Ejemplo ilustrativo: tres sitios × tres bloques × cuatro variedades distintas =36 parcelas; no sustituye cálculo de tamaño muestral. Segunda fase compara políticas de renovación asignadas al azar en horizonte común. Solo propuesta, sin captura adicional ejecutada.

## Archivos y reproducción

- `scripts/descargar_serie1.py`; `scripts/etl_serie1.py`; notebooks 01–05 en orden; requisitos e instrucciones en README.
- Notebooks 01/02: fuente/unidades, calidad y cobertura. 03: decisión económica. 04: comparación/modelo. 05: segmentos.
- Salidas y exclusiones por análisis en `data/processed/`, ignoradas por Git. Bitácora conserva decisiones, uso de IA, sugerencias descartadas y corrección metodológica.
- Ejecución final: notebooks 01–05 completos con el kernel explícito `prueba-santa-ana` que apunta a `.venv`; 25 celdas de código ejecutadas, cero salidas de error. JSON/esquema de notebooks comprobados. `py_compile`, `pip check` y `git diff --check` sin errores; skill `quick_validate.py`: válida. Figura de segmentos inspeccionada visualmente. Estas comprobaciones no sustituyen la revisión independiente de fórmulas, diseño y métricas.

## Git y privacidad

- Repositorio privado: https://github.com/MoraVevo/prueba-tecnica-cientifico-datos-santa-ana ; rama `main`, remoto `origin`.
- Último commit observado `1998c00`, “Completa borrador analítico de Serie I”, realizado y enviado a `origin/main` por petición del usuario. Las revisiones posteriores de cobertura y gráficas se cierran con un commit local autorizado; consultar git log para su hash. El último push confirmado corresponde a 1998c00. El repositorio sigue privado.
- `AGENTS.md` privado e ignorado; historial main reescrito anteriormente. La skill conserva advertencia de SHA antiguos aún consultables en GitHub y respaldo fuera del proyecto. No afirmar borrado universal del historial anterior.
- PDF, datasets y entornos ignorados. Revisar ZIP/acceso antes de entrega.

## Pendiente concreto

1. Revisión independiente de unidades, fórmula de rotación, ajuste de ambientes, cobertura, remuestreo, ausencia de fuga temporal, métricas y segmentación. El usuario pidió dedicarle una sesión; no bloquear la construcción del borrador por esa revisión futura.
2. Revisar certeza del tercer puesto y duración por frontera de cobertura; conservar sensibilidad y alternativas.
3. El borrador completo de Serie I ya tiene commit y push (`1998c00`). Sugerir un nuevo commit cuando se cierre la revisión metodológica; no fabricar historial retroactivo.
4. Series II–V, API y presentación siguen pendientes; solo hubo inspecciones remotas iniciales de otros datasets. No se afirman realizadas.

## Aclaraciones para defender la decisión económica

- No se asignó superficie a las variedades: acre es la unidad de comparación. Una cosecha anual y escala proporcional son supuestos, no una medición de superficie asignada.
- Se evaluaron 17 variedades elegibles de 40 presentes en la base económica de etapa 5; 23 quedaron fuera del ranking por la cobertura mínima declarada. Para cada elegible, el código sí compara duraciones de una cosecha hasta el último corte admitido, no solo tres o cuatro.
- L01-299 se eligió como referencia con amplia cobertura (393 celdas clon/corte/año/localidad; 12 años y 15 localidades en total); no es la variedad con más celdas. El ajuste aditivo es una decisión metodológica, no una exigencia del PDF ni una corrección causal demostrada.
- Dos años y dos localidades por corte y exigir plantía/dos socas son filtros propuestos por el análisis. No son garantías estadísticas ni reglas del enunciado.
- En las tres recomendaciones, la mejor duración coincide con el último corte admitido por cobertura. Las extensiones observadas con menor cobertura aumentan el aporte calculado: HOCP14-885 pasa de 727.58 (3 cosechas) a 753.75 (4); L01-299 de 632.66 (4) a 667.14 (5); HO12-615 de 629.21 (4) a 631.78 (5). No se identificó una caída del aporte que establezca un máximo económico interior. Explicar la renovación como política provisional respaldada hasta ese corte y revisar este criterio antes de afirmar una duración óptima.
- El ranking económico procede de medias por ambiente y enumeración de políticas; no de las predicciones Ridge ni del agrupamiento. Los escenarios de precio verificaron duración dentro de cada variedad; no equivalen a una optimización robusta de una cartera de tres variedades.


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


## Criterio para cerrar Serie I

Las cuatro respuestas están construidas como borrador. La justificación de STAGE 5 ya se incorpora a README, conclusiones y notebook 03 con fuente primaria. Pendiente para cierre:

1. Revisión económica independiente completada en cuanto a reproducción aritmética, escenarios de precio, inclusión de filas marcadas y remuestreo descriptivo. No se encontró error aritmético. Los supuestos de tonelada compatible, mantenimiento anual, ajuste aditivo, cobertura y alcance del remuestreo quedaron explícitos arriba; son límites del análisis y no se resuelven con otra ejecución. La conclusión ya presenta las duraciones como políticas iniciales y no como máximos demostrados.
2. Auditar predicción: historia estrictamente anterior al año predicho, separación temporal, ajuste de transformaciones en entrenamiento, selección de algoritmo y métricas/referencias. Ya existen tres algoritmos y train/validaciones/test temporal; no falta construirlos.
3. Revisar segmentación: definiciones y unidades de cuatro dimensiones, escalado/elección de grupos y correspondencia entre perfiles y lectura gerencial. Ya existe propuesta de captura y ensayos; comprobar coherencia con limitaciones detectadas.
4. Consolidar conclusiones/notebooks/README: retirar formulaciones categóricas de renovación que contradigan la cobertura, referencias históricas superadas y lenguaje confuso; comprobar reproducción ordenada y cerrar con commit/push autorizado.

Regresión económica por CROP: propuesta, todavía no ajustada. Solo es necesaria para incluir resultados b/R de esa regresión en la conclusión; no es una exigencia explícita adicional de Serie I. No extrapolar una cifra sin ajustar/evaluar el modelo. No exigir API (Serie IV), presentación (Serie V), nuevos datasets o programación lineal para dar por cerrado el análisis de Serie I.

La revisión de STAGE y la auditoría económica se guardan en el commit de este hito; último push confirmado: 1998c00. Consultar `git log` para el hash local más reciente. La revisión aritmética económica se completó y no cambió resultados numéricos; siguen pendientes las revisiones independientes de los puntos 2 y 3 y la consolidación final.
