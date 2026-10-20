# Auditoría independiente de lo realizado — 2026-10-20

Base revisada: `main`, commit `79e7034`, con árbol de trabajo versionado limpio al inicio. Revisión solicitada por el usuario mediante tres subagentes `gpt-6-luna`, todos con esfuerzo `max`, y contraste del agente principal. Prioridad confirmada: avanzar poco y con profundidad antes que abarcar mucho superficialmente.

**Resultado:** no se encontraron bugs reproducibles de cálculo, fuga temporal o selección del campeón en lo comprobado, ni hallazgos P1/P2. Se confirmaron dos observaciones P3 de evidencia/documentación. Esto no demuestra ausencia absoluta de errores ni certifica validez instrumental o generalización futura.

## Alcance y método

- Auditor de Serie I: ETL, unidades, economía, modelo supervisado, segmentos, pruebas y conclusiones.
- Auditor del sensor virtual: módulo, notebook 07, selección de variables, particiones, métricas, artefacto y pruebas.
- Auditor de datos y requisitos: crudo/diccionario de Serie II, notebook 06, instrucciones, README y documentación física.
- Control central: suite completa, dependencias, esquema/salidas de notebooks, métricas de validación, conservación de filas y estado de Git.

Se leyeron `AGENTS.md`, la skill `prueba-santa-ana`, su referencia de requisitos y las memorias del proyecto. Se contrastó el trabajo con los requisitos extraídos del PDF. No se reabrió visualmente el PDF ni se consultaron nuevas fuentes: no surgió una ambigüedad que lo exigiera. No se ejecutaron notebooks completos ni se sobrescribieron resultados. Los recálculos adicionales se hicieron en memoria con `.venv/Scripts/python.exe`.

## Hallazgos accionables

### P3 — Mostrar la evidencia estadística de los 30 sensores

Ubicación: `notebooks/06_eda_caldera_serie2.ipynb`, celda 20 (índice desde cero), línea 1930 del JSON revisado: `tabla_resumen_sensores.head()`.

El código calcula los estadísticos para los 30 tags, pero la salida guardada solo muestra cinco, todos de la familia de presiones del hogar. Las otras tablas sí muestran los 30 sensores. No hay error en los cálculos; la evidencia visible de mínimos, máximos, negativos, ceros y constancia queda incompleta para un lector que revisa las salidas sin ejecutar código.

Corrección mínima sugerida: mostrar la tabla completa. No hace falta ampliar el análisis ni incorporar gráficos adicionales.

### P3 — Actualizar la descripción del estado del sensor virtual

Ubicación principal: `docs/serie2-significado-disponibilidad.md:26`: el alcance se describe como una propuesta «pendiente del desarrollo del modelo», aunque el mismo documento recoge después el resultado vigente y el notebook 07 ya lo implementa. El notebook 06, celdas 30, 32 y 35, conserva también el lenguaje de planificación previo.

README, estado y notebook 07 sí describen correctamente el modelo actual y la comprobación reutilizada. La mezcla de estados puede confundir al lector sobre qué existe y qué sigue pendiente; no altera las cifras.

Corrección mínima sugerida: enlazar el desarrollo existente en el notebook 07 y distinguir los pendientes reales: rezagos, regímenes, anomalías no supervisadas y eficiencia. Mantener explícito que el último día es una comprobación exploratoria reutilizada.

## Evidencia verificada

### Serie I

- La suite de integración comprueba conservación/exclusiones del ETL, métricas y particiones supervisadas, políticas económicas y segmentación.
- El auditor reprodujo en memoria Ridge 2021 sobre 2,288 filas: MAE 2,144.546 lb/acre, RMSE 2,770.972 y R² 0.250673, coincidentes con las salidas.
- Reconstruyó desde el ETL las 51 políticas óptimas de 17 variedades y tres precios mediante otra rutina: coincidencia dentro de precisión numérica. Se mantienen HOCP14-885 (tres cosechas), L01-299 (cuatro) y HO12-615 (cuatro) en los tres escenarios.
- Reconstruyó las cuatro dimensiones y K-means: 17 variedades y 840 ambientes pareados; pertenencias idénticas (ARI=1).
- La falta de cohortes, el ajuste ambiental aditivo, la cobertura limitada de cortes y la incertidumbre del tercer puesto están documentados; no se elevaron a bugs ocultos ni se exigieron datos externos.

### Serie II

- Crudo y diccionario: 86,400 filas, 30 tags alineados, intervalos de cinco segundos; 30 faltantes solo en `YJJWSLL`, en dos tramos; sin duplicados de fecha/fila/vector ni infinitos. Coinciden los cinco tags repetidos por parejas y las correlaciones principales.
- El EDA recorre los 30 sensores; los extremos se conservan como candidatos de revisión, sin convertir MAD/Tukey en pruebas de falla. No se asignan unidades instrumentales por apariencia.
- RFE, imputación y escalado se ajustan dentro de cada entrenamiento. La selección de Ridge/Reducida 15 concuerda con la regla de validación y no incorpora el objetivo ni sus rezagos como entradas.
- El agente principal reconstruyó seis métricas desde las 155,520 predicciones guardadas de validación: 18 grupos de 8,640 filas, diferencia máxima 6.89e-15 respecto de las métricas exportadas. La referencia mediana no está en ese archivo de predicciones; no se incluye dentro de esos 18 grupos.
- Las 43,200 filas fuera de rejilla son idénticas a las de la segunda fase del crudo y tienen motivo completo. No se declararon inválidas.
- Las pruebas reproducen las predicciones de la comprobación final cargando el artefacto guardado y contrastan el objetivo por timestamp con el crudo.

### Controles generales

Ejecutado en esta auditoría:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unitarias tests/integracion -q
.\.venv\Scripts\python.exe -m pip check
```

Resultado: **29 pruebas aprobadas**, sin dependencias rotas. Los siete notebooks pasan validación de esquema y no contienen salidas de error guardadas. Esto último no equivale a una nueva ejecución completa de los notebooks.

## Observaciones que no se trataron como bugs

- El último día de Serie II ya fue observado antes de la revisión a quince señales. Está declarado en README/notebook/JSON como comprobación reutilizada; no se presenta como test independiente.
- Retirar memoria del código y usar quince señales responde a una decisión explícita del usuario. Los rezagos del PDF siguen pendientes, sin darlos por completados.
- Cinco días no certifican generalización amplia ni continuidad ante una falla compartida. La independencia del caudal compensado respecto de otras señales requiere fórmula/linaje instrumental.
- La gráfica de sesgo por hora del reloj tiene extremos parciales (187 y 173 observaciones frente a 360 por hora completa). Las medias calculadas son correctas. Señalar los intervalos parciales sería una mejora opcional de presentación; no se consideró un bug ni motivo para cambiar métricas.
- La bitácora registra históricamente 61/31 y después 58/30 celdas/código del EDA, mientras la versión actual tiene 61/31. No se verificó la cronología de esas capturas; se recomienda identificar la versión de cada nota si se revisa esa sección, sin corregir retrospectivamente el historial por conjetura.
- Regímenes, anomalías, eficiencia y las demás series/entregables pendientes no se implementaron durante esta auditoría. No se considera cerrada la Serie II.

## Cambios y Git

Solo se añadieron este informe, la memoria de auditoría en `docs/estado.md`/`bitacora.md` y la preferencia de profundidad en el `AGENTS.md` local ignorado. No se modificaron código, notebooks, datos, modelos ni resultados.

No se hizo commit, push, fetch ni descarga. Al inicio, `HEAD` estaba tres commits por delante de la referencia local `origin/main` (sin consultar el estado actual del servidor). PDF, datos, resultados y `AGENTS.md` están ignorados y no figuran en el índice actual; esta comprobación no certifica borrado de copias históricas. Sigue vigente la restricción de no hacer push.

Una vez revisado el informe, este es un hito coherente para sugerir un commit local: `Documenta auditoría independiente de Series I y II`. No está ejecutado. El siguiente paso propuesto es resolver primero los dos P3 con cambios pequeños y verificables, antes de ampliar el alcance.
