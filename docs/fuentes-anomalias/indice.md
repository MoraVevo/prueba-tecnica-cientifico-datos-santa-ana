# Fuentes para evaluar la carga del complemento estadístico

Alcance: inciso 4 de Serie II. Cuatro fuentes primarias sustentan la evaluación de los 384 tramos de corriente como marcas estadísticas, sin interpretarlos como fallas confirmadas.

| ID | Fuente | Aporte y localización |
|---|---|---|
| f001 | [Dunn y Sands, ISA/InTech, 2020](https://www.isa.org/intech-home/2020/march-april/features/alarm-management-questions-that-everyone-asks) | Definición operativa y racionalización, sección “What is alarm management?”: necesidad de respuesta oportuna, consecuencia y acción. |
| f002 | [NIST/SEMATECH, Detection of Outliers](https://itl.nist.gov/div898/handbook/eda/section3/eda35h.htm) | Secciones de etiquetado, supuestos distributivos y modified Z-score. Distancia robusta no demuestra error de medición ni falla. |
| f003 | [Scofield et al., ISA/InTech, 2021](https://www.isa.org/intech-home/2021/august-2021/features/from-alarm-floods-to-highly-protected-status) | Caso industrial Solvay, párrafo inicial sobre calidad/cantidad: una tasa baja no sustituye pertinencia. |
| f004 | [HSE, Better alarm handling, CHIS6, 2000](https://www.hse.gov.uk/pubns/chis6.pdf) — [copia local pública](fuentes/f004_hse_better_alarm_handling.pdf) | Páginas 1–2: tasa media de referencia, acción necesaria, respuesta definida. Página 4: guía de buenas prácticas no obligatoria, marzo de 2000. |

El registro `fuentes.jsonl` conserva URL, autores, localización, cita breve y límites. La ficha pública HSE tiene 72,320 bytes; no es el PDF confidencial de la prueba ni una norma actual de cumplimiento guatemalteco o cupo de alarmas por sensor. Los cálculos y la conclusión aplicada están en el notebook 10; el texto externo no valida estos sensores.

## Información necesaria para aplicación operativa

Huella SHA-256 de la copia HSE verificada: `220daccb2dfdcdad85dac373d8961c2cd4ed4febb75190f67fe5d980ae2ead32`.

- No hay bitácora etiquetada de fallas/calidad, acciones del operador, consecuencias ni tiempo de respuesta admisible por evento.
- No conocemos la carga total de alarmas del puesto ni separamos operación normal y perturbaciones con etiquetas independientes.
- Cinco días vistos no representan el promedio de largo plazo; faltan periodo nuevo y validación del ingeniero de proceso.
- No se conoce el costo de revisar una marca. Cualquier cálculo de tiempo será escenario explícito, no costo observado.
