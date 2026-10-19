# Estado persistente — prueba Santa Ana

Actualización: 2026-10-19, America/Guatemala.

## Alcance y forma de trabajo

- **Serie I completada y revisada en su alcance analítico:** cuatro respuestas, evidencia reproducible, evaluación gerencial y 21 pruebas automatizadas. El ejercicio completo aún no está terminado.
- Usar solo el dataset entregado y los supuestos del PDF. No buscar ni descargar datasets externos adicionales por ahora. Las fuentes externas ya consultadas aportan contexto/unidades; no son nuevos predictores. Las limitaciones modifican certeza y supuestos, sin impedir responder las cuatro preguntas.
- Español en comentarios, docstrings y explicaciones. Parsimonia en código, archivos y análisis. Mantener filas excluidas y motivos; no elegir arbitrariamente una medición conflictiva.
- Preferencia del usuario: en no supervisado, priorizar interpretación y utilidad gerencial; silueta, Davies–Bouldin e inercia son diagnósticos secundarios. No quitar dimensiones solicitadas para mejorar esas métricas.
- El usuario tiene poca familiaridad con Git. Sugerir hitos y explicar qué se guarda. **Última instrucción: hacer commits locales y NO hacer push todavía.** Esta instrucción prevalece sobre el seguimiento anterior de subir hitos a GitHub.
- Plazo informado: 48 horas, sin inicio/vencimiento absoluto confirmado. El PDF pide ZIP con `.git`, sin datasets, enlace GitHub/GitLab y presentación; no convertir “lunes siguiente 8:00” en fecha sin referencia.

## Fuente y ETL

- PDF local de seis páginas; requisitos en la skill `prueba-santa-ana/references/prueba.md`.
- USDA y Kaggle Serie I son idénticos. SHA-256 CSV: `5e7b13de6bda8aed51479c5fdfc3de4a28e71ccbb45e4761b6688a34b7cff4b0`.
- `T_SPACRE`: lb azúcar/acre según USDA, corrigiendo la descripción del PDF. `TCA`: ton caña/acre; `TRS_TON`: lb/ton. Se supone compatibilidad de la tonelada de TCA con el costo de US$14/ton; el PDF no especifica su tipo.
- `TRS_TON` analítico es el componente numérico final. Texto original y prefijo de dos dígitos se preservan; no hay definición confirmada del prefijo y no entra al modelado.
- Fuente: 29,529 filas. ETL: 29,403 analíticas y 126 copias exactas adicionales excluidas con motivo. Se mantienen 224 filas en 112 pares de claves con mediciones distintas (etapa 3) y 23 alertas dimensionales. La investigación no permite elegir cuál fila de los pares corregir.
- Fibra ausente en 57.3 % del analítico; no se fuerza imputación. CROP 4: 84 filas, 13 clones, GLENWOOD, 2019–2021. CROP 5 no existe en el CSV original; no fue eliminado por el ETL. Sin parcela/cohorte y motivo de retiro no se identifica renovación deliberada ni se explica toda ausencia por cierre temporal.
- STAGE es etapa del programa: 2 second line, 3 nursery, 4 infield, 5 outfield, confirmado con la fuente técnica. Economía/segmentación usan etapa 5 por comparabilidad del diseño; el supervisado usa las etapas con objetivo disponible.

## 1. Economía — notebook 03

- Aporte anual de rotación: `[suma_cortes(precio × E[azúcar] − 14 × E[caña] − 350) − 1100] / número_cosechas`.
- Una cosecha anual, renovación inmediata una vez por rotación, costos constantes, sin descuento ni descanso. Es aporte parcial esperado, no utilidad neta ni flujo observado de la misma parcela. Acre es una unidad de comparación; no se asignó superficie.
- Etapa 5: 14,029 filas principales y 63 exclusiones conservadas. Promedio de réplicas por clon/corte/año/localidad; ajuste aditivo respecto a L01-299 en 4,197 de 4,708 celdas compartidas. Las no emparejadas se conservan aparte. El ajuste y el filtro de dos años/dos localidades por corte son decisiones del análisis.
- A US$0.20/lb: HOCP14-885, 3 cosechas totales, US$727.58/acre/año; L01-299, 4, US$632.66; HO12-615, 4, US$629.21. Tres cosechas = plantía + dos socas; cuatro = plantía + tres socas. Se evaluaron 17 variedades elegibles, no solo las tres ganadoras.
- Precios ilustrativos 0.15/0.20/0.25 USD/lb conservan esas duraciones. Sin ajuste ambiental, L01-283 desplaza a HO12-615 del tercer puesto; esa elección está condicionada al ajuste. Certeza media para L01-299 y media-baja para duración de HOCP14-885 y tercer puesto.
- Las 198 políticas y escenarios se reconstruyeron independientemente. No se encontró error aritmético. Las cuatro filas etapa 5 marcadas no cambian el resultado a centavos. Las pruebas de integración conservan la comprobación de fórmula, cobertura y recomendaciones.
- Remuestreo por año (500): rangos P05–P95 del aporte de la política elegida ≈652–834, 572–700 y 570–684 USD/acre/año; misma duración en 100/100/98.6 % de remuestras válidas. Son estabilidad dentro de la muestra/método, no probabilidad de superioridad del ranking. Solo 12 años.
- Las duraciones 3/4/4 son fronteras de cobertura, no máximos económicos demostrados. Extensiones menos respaldadas elevan el aporte: HOCP14-885 a 4 cosechas, 753.75; L01-299 a 5, 667.14; HO12-615 a 5, 631.78. Conservar la redacción acordada sobre políticas iniciales e incertidumbre de cortes ausentes.
- Regresión económica por CROP: propuesta opcional no ajustada. No es requisito adicional para cerrar Serie I y no se afirman sus coeficientes ni una extrapolación a CROP 5.

## 2. Predicción — notebook 04 y scripts/modelado_serie1.py

- Tres algoritmos: Ridge, árbol y bosque; dos referencias históricas. Entradas: CLONE, LOC, STAGE, CROP, YEAR y medias anteriores de azúcar por clon, localidad y clon/corte. No se usan TCA/TRS/POPN/MSTWT/FIBER contemporáneos.
- Validación 2019 y 2020 con entrenamiento en años anteriores; selección por MAE promedio. Ridge elegido: 2,405.64 lb/acre. Test final 2021 reservado, sin usarlo para elegir algoritmo ni retocar hiperparámetros.
- Test 2021 Ridge: MAE 2,144.55 lb/acre; RMSE 2,770.97; R²≈0.25; etapa 5 MAE 1,898.11. Referencias: MAE 2,662.69 histórica y 2,270.33 reciente. Error absoluto agregado / azúcar observada≈25.5 %. Utilidad moderada y heterogénea, sin intervalos de predicción calibrados.
- Hay 2,288 filas de test: 1,980 de clones vistos (MAE 2,140.11) y 308 sin historia del clon (2,173.05). Se entregan errores por corte/etapa y por localidad/etapa. MAGNOLIA etapa 5: 72 observaciones, MAE y sesgo positivo 3,498.54; limitar el uso puntual en ese ambiente. No se atribuye una causa no observada.
- Sesgo Ridge `predicción − observado`: +2,148 en 2019 y −1,078 en 2020. Caída/rebote del objetivo y uso de historia previa explican un posible desfase; no identifican efecto causal de clima/COVID. Contexto y fuentes en README.
- Coeficientes Ridge evaluado en 2021: CROP≈−802 lb/acre por unidad, YEAR≈−25 lb/acre/año, condicionados y regularizados. No son efectos causales ni regla autónoma de renovación.
- Principal: 28,981 filas, 422 exclusiones trazables; ocho ceros fuente conservados. Sensibilidad con alertas en entrenamiento/historia: MAE≈2,135.10 sobre la misma prueba limpia. Ejemplo de próxima zafra del archivo: 2022, ilustrativo y sin resultado observado.
- Auditoría completada: funciones compartidas con pytest, historia estrictamente previa, transformaciones ajustadas en entrenamiento, elección solo por validación, métricas reconstruidas desde predicciones por fila de los cinco métodos en 2019/2020/2021 y reproducción de Ridge. La reorganización del código conservó exactamente las predicciones previas de 2021.

## 3. Segmentación — notebook 05

- 17 variedades de etapa 5, plantía/dos socas y dos años/localidades por corte; otras 23 con motivo de cobertura insuficiente. Cuatro entradas estandarizadas: azúcar, TRS, conservación y variabilidad relativa centrada por variedad/corte. Conteos y códigos no entran a la distancia.
- Conservación CROP 2/CROP 0 en los mismos años/localidades de cada variedad: 840 comparaciones, 18–110 ambientes por variedad, 2–12 años y 11–13 localidades. Se conservan 678 ambientes sin ambos cortes; contribuyen a otras dimensiones. No es seguimiento de parcela ni vida útil máxima.
- K-means con K=2 por parsimonia/lectura gerencial. K=3/4 generan un grupo unitario. Silueta secundaria: 0.254/0.229/0.265 para K=2/3/4. No hay selección automática por máxima silueta.
- Perfil 1: cinco variedades, azúcar≈7,997, TRS≈290, conservación≈75.4 %, variabilidad≈12.1 pp. HO05-961, HO07-613, HOCP00-950, HOCP96-540 y L03-371. Mayor vigilancia de continuidad de socas y excepciones individuales visibles.
- Perfil 2: doce variedades, azúcar≈8,376, TRS≈277, conservación≈82.6 %, variabilidad≈9.8 pp. Incluye las tres recomendaciones económicas; no todos sus miembros conservan igual ni son igualmente rentables.
- HO05-961 pasó de 83.6 % sin emparejar a 76.0 % en ambientes comunes, y de Perfil 2 a 1, con solo dos años comparables. Ward cambia L99-226 de perfil. Omitir variabilidad cambia seis pertenencias; esa prueba cambia la pregunta de negocio y no justifica eliminar una dimensión solicitada.
- Reconstrucción independiente de cuatro entradas y 17 asignaciones: diferencia máxima <1e-12. Pruebas de integración lo reproducen. Tabla en unidades originales, cobertura individual y gráfica de cuatro dimensiones inspeccionada (`outputs/serie1_segmentos_perfiles.png`, también embebida).
- Certeza exploratoria: productividad/TRS con coberturas diferentes, referencia ambiental variable, dimensiones correlacionadas y falta de cohortes. No son clases naturales ni un ranking económico.

## 4. Datos propios y ensayos

- Conclusiones incluyen ID de parcela/cohorte/bloque, tamaño total y área útil, clima por fecha/localidad, sistema/fuente/volumen/continuidad del agua, manejo, calidad, costos y causas de retiro/eventos externos. Registrar interrupciones concretas; un indicador COVID aislado queda confundido con el año.
- Ensayo ilustrativo: tres sitios × tres bloques × cuatro variedades únicas = 36 parcelas, con aleatorización y seguimiento de socas. Dimensionar repeticiones con variación real/diferencia relevante. Proponer segunda fase aleatorizada de políticas de renovación en horizonte común. Captura y ensayos se proponen, no se ejecutan.

## Pruebas y reproducción

- Entorno Python 3.13.14; `requirements.txt` para análisis, `requirements-dev.txt` añade pytest 8.4.2. Desde la raíz: instalar dependencias, ejecutar descargador/ETL y notebooks 01–05 según README.
- `python -m pytest -q`: 13 unitarias sin datasets; `pytest.ini` fija esa suite por defecto.
- `python -m pytest tests/integracion -q`: 8 de integración con datos/resultados locales. Si falta un archivo, fallan con instrucción, sin saltarse la prueba.
- `python -m pytest tests/unitarias tests/integracion -q`: ambas suites. Última ejecución: **21 pruebas aprobadas**. Comprobaciones de prefijo/ceros/exclusiones, invariancia temporal, referencia, imputación/escalado/categorías desconocidas, predicciones/métricas/particiones, errores por ambiente, políticas y segmentos.
- Perfiles, predicciones y métricas numéricas revisados sin NaN/inf inesperados. Las historias desconocidas/primer año y los cortes ausentes en `serie1_segmentacion_ambientes_sin_par.csv` contienen faltantes intencionales y trazables.
- Notebooks 03/04 reejecutados al cerrar; 05 ejecutado tras su revisión. Los cinco notebooks tienen esquema válido y cero salidas de error guardadas. `pip check` sin dependencias rotas. Verificar resultados de los comandos en bitácora antes de afirmar futuras ejecuciones.
- Las pruebas verifican implementación y consistencia, no eliminan incertidumbre estadística ni validan supuestos como hechos.

## Git, privacidad y siguientes pasos

- Repositorio privado: https://github.com/MoraVevo/prueba-tecnica-cientifico-datos-santa-ana ; rama main, origin.
- Último push confirmado: `cdddb7e` (sesgo Ridge). Segmentación guardada localmente en `0c61391`; pruebas y cierre constituyen otro hito local. **No hacer push hasta nueva autorización del usuario.** Consultar `git log` y `git status` para hashes/sincronización actuales.
- `AGENTS.md` privado e ignorado en cualquier carpeta. Historial main reescrito anteriormente; los SHA antiguos aún respondían a consultas directas de GitHub, por lo que no afirmar borrado universal. Respaldo fuera del proyecto en `../respaldo-agents-historial.bundle`, fuera del ZIP/Git. PDF, datasets, entornos y outputs excluidos de Git.
- La Serie I se puede cerrar con los supuestos y limitaciones declarados. Series II–V, API, presentación y entrega ZIP siguen pendientes; no convertirlos en requisitos para cerrar el análisis de Serie I. Siguiente paso sugerido: continuar con la siguiente serie, conservando estos resultados para la presentación y entrega general.
