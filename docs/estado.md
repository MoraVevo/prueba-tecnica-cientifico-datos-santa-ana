# Estado persistente — prueba Santa Ana

Actualización: 2026-10-19, America/Guatemala.

## Alcance vigente

- Desarrollar las cuatro respuestas de Serie I con el dataset entregado y los supuestos del PDF. La última corrección del usuario prevalece sobre interpretaciones anteriores: las limitaciones deben modificar certeza y supuestos, sin impedir dar tres variedades, renovación, modelo, segmentos y propuesta de ensayos.
- Por ahora no buscar ni descargar datos externos adicionales. Las búsquedas previas de metadatos/unidades forman parte del historial; liberación comercial o adaptación a Santa Ana no son condiciones para resolver este ejercicio.
- Cálculos/métricas reproducibles pero pendientes de revisión independiente con tiempo específico. Ejecutar sin errores no es validar fórmula ni negocio.
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
- Último commit observado `e1adc18`, “Excluye copias exactas del dataset analítico”. Nuevos análisis, simplificación ETL y documentación sin commit ni push. No hay autorización nueva para publicarlos o invitar evaluadores.
- `AGENTS.md` privado e ignorado; historial main reescrito anteriormente. La skill conserva advertencia de SHA antiguos aún consultables en GitHub y respaldo fuera del proyecto. No afirmar borrado universal del historial anterior.
- PDF, datasets y entornos ignorados. Revisar ZIP/acceso antes de entrega.

## Pendiente concreto

1. Revisión independiente de unidades, fórmula de rotación, ajuste de ambientes, cobertura, remuestreo, ausencia de fuga temporal, métricas y segmentación. El usuario pidió dedicarle una sesión; no bloquear la construcción del borrador por esa revisión futura.
2. Revisar certeza del tercer puesto y duración por frontera de cobertura; conservar sensibilidad y alternativas.
3. Guardar un commit coherente cuando el usuario lo autorice; no fabricar historial retroactivo.
4. Series II–V, API y presentación siguen pendientes; solo hubo inspecciones remotas iniciales de otros datasets. No se afirman realizadas.
