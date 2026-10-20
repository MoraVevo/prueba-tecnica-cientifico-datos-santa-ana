# Auditoría específica de leakage del sensor virtual

Fecha: 2026-10-20. Campeona auditada: Ridge/Reducida 15, alpha=100, estimación contemporánea de `ZZQBCHLL` con otras señales. **No se detectó fuga computacional en la ruta revisada. El CSV no permite certificar independencia instrumental, latencia ni una evaluación externa independiente.** Se conserva el resultado como desempeño histórico de selección/validación, sin promover otro modelo.

## Reproducción

Desde la raíz y con datos/resultados locales:

```powershell
.\.venv\Scripts\python.exe scripts/auditar_leakage_serie2.py
.\.venv\Scripts\python.exe -m pytest tests/unitarias tests/integracion -q
```

Evidencia nueva en `outputs/auditoria_leakage/`: pruebas adversariales, duplicados entre particiones, diagnósticos, resumen y `verificacion.json`. No se escriben archivos de la campeona. Su fuente, notebook, módulo y salidas se protegen con SHA-256.

El script ejecuta los cálculos de las celdas 3, 5, 6 y 8 del notebook 07. Mediante AST elimina solo exportaciones CSV/JSON/joblib y silencia visualización/impresión durante la reproducción. Para las pruebas de entrenamiento restringe la fábrica a Ridge, preservando su pipeline e hiperparámetros; reproduce aparte la elección real desde las métricas de todos los algoritmos. No equivale a reentrenar todos los competidores ni a ejecutar el notebook entero.

## Controles ejecutados

| Riesgo | Comprobación y resultado |
| --- | --- |
| Objetivo o fecha como entrada | Las 29 candidatas excluyen `ZZQBCHLL` y `date`; las quince son un subconjunto. No hay columnas de historia o del propio objetivo en esta versión. |
| Cruce temporal | Se reproducen las máscaras reales: entrenamiento estrictamente anterior, separación efectiva mayor de cinco minutos y validaciones de 24 horas. No hay partición aleatoria. |
| Copias en ambas particiones | Cero vectores completos idénticos entre entrenamiento y evaluación para 29 y 15 entradas, en los tres pliegues y la comprobación final: ocho contrastes. Esto no implica independencia de muestras autocorrelacionadas. |
| RFE usando etiquetas futuras | Se permutan todas las etiquetas posteriores al entrenamiento en cada pliegue. Las quince elegidas y los parámetros permanecen idénticos. |
| Imputación/escalado con datos futuros | Se alteran masivamente los predictores posteriores al entrenamiento. No cambian selección, medianas, medias, escalas ni coeficientes. Se comparan predicciones sobre las mismas entradas originales, no sobre las entradas alteradas. |
| Comprobación final contaminando el fit | Se repiten ambas pruebas después del límite de desarrollo. No cambian las quince, parámetros ni predicciones al mantener fija la decisión previamente elegida. Esto no borra el conocimiento humano de resultados anteriores. |
| Artefacto entrenado en todas las filas | El reajuste real coincide con el joblib. Las estadísticas se reconstruyen desde las 34,530 filas permitidas de desarrollo; `n_samples_seen_` coincide. |
| Selección distinta de la documentada | La celda real de elección reproduce exactamente el JSON vigente desde las métricas de validación completas, sin consultar las métricas del último día. |
| Métricas/filas desalineadas | Las predicciones de validación se reproducen por pliegue; las pruebas existentes contrastan timestamps, objetivo crudo y métricas por fila. |

**Resultado:** ocho pruebas adversariales aprobadas, con diferencia máxima cero al comparar predicciones de entradas originales bajo las perturbaciones futuras. Los ocho contrastes de vectores repetidos dan cero cruces. Suite existente completa: **34 pruebas aprobadas**. No se modificaron código/notebook/modelo de la campeona ni sus resultados.

## Sensibilidad a proximidad temporal y a las presiones

Diagnósticos con los mismos días de validación y Ridge alpha=100. No se eligieron nuevas variables a partir de sus métricas ni se cambió la campeona.

| Diagnóstico | MAE medio | WAPE agregado |
| --- | ---: | ---: |
| Campeona de quince | 0.457279 | 0.7682 % |
| Separación de una hora en lugar de cinco minutos | 0.459661 | 0.7722 % |
| Solo las dos presiones PTCA | 0.631388 | 1.0606 % |
| Quince del pliegue, retirando las dos PTCA | 0.862244 | 1.4484 % |

En la separación de una hora, RFE se vuelve a ajustar con el pasado permitido; se conservan fechas de evaluación. La cercanía inmediata a la frontera no explica por sí sola el resultado: el error cambia poco. Es sensibilidad a otra separación, no prueba de independencia estadística o estabilidad futura.

Las presiones contienen una parte importante de la capacidad predictiva. Quitarlas empeora el resultado, aunque el resto todavía predice. **Una asociación fuerte no demuestra fuga.** Este diagnóstico orienta qué linaje instrumental revisar; no justifica borrar esas columnas ni certifica que estén libres de dependencias calculadas.

## Riesgos que siguen abiertos

### 1. Linaje del caudal compensado y disponibilidad

El diccionario identifica el objetivo como caudal principal después de compensación. La [publicación original](https://doi.org/10.1038/s41597-025-05096-4) describe adquisición DCS, acondicionamiento, compensación y supresión de ruido; no aporta en el texto revisado la fórmula del caudal ni dependencias/latencias individuales de los tags. Se revisó su XML completo mediante [Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12052967/fullTextXML); copia y procedencia con SHA-256 quedan en la carpeta ignorada de esta auditoría. Las ecuaciones explícitas del artículo son MSE y MAE.

Falta confirmar si alguna entrada se calcula usando el propio caudal, si comparte el instrumento que se pretende sustituir y si su valor está recibido al estimar. También faltan el detalle del filtrado/adquisición y las edades de lectura. Compartir presión o temperatura para compensación no implica automáticamente fuga; depender del caudal objetivo o de información no disponible sí invalidaría el escenario de reemplazo correspondiente.

El CSV y las pruebas de perturbación detectan dependencias introducidas por nuestro código; no reconstruyen cómo generó el DCS las columnas. Se necesita fórmula de compensación, linaje de tags y metadatos de recepción/calidad para cerrar ese punto. El modelo actual estima caudal contemporáneo bajo el supuesto explícito de disponibilidad de otras señales.

### 2. Reutilización de la evaluación

El día 5 ya fue observado antes de revisar a quince variables. Las tres validaciones también participaron en elegir algoritmos/variantes, probar features y mantener la solución simple. No son una confirmación externa nueva. El EDA global vio el archivo entero antes del modelado; la implementación actual aprende selección y transformaciones solo con entrenamiento, pero la exposición previa puede influir en decisiones humanas.

Por tanto, no corresponde llamar a 0.7682 % «error futuro confirmado sin sesgo de selección» ni al 0.5564 % del día 5 un test virgen. Son resultados históricos reproducibles, útiles para comparar alternativas en este archivo. No se puede recuperar independencia renombrando particiones ya vistas. Una confirmación nueva requiere congelar la solución y evaluarla en otro periodo que no haya guiado decisiones.

## Decisión

Se conserva Ridge/Reducida 15 y su resultado histórico, condicionado al alcance contemporáneo y disponibilidad declarados. No se detecta un bug que obligue a descartar las métricas. La etiqueta correcta es **buen desempeño histórico exploratorio, con controles de fuga computacional aprobados e independencia instrumental/externa pendiente**, sin certificar ausencia absoluta de leakage de todo tipo.

No se realizaron nuevas features, ajuste de hiperparámetros, cambio de campeona, commit ni push. El siguiente paso para elevar la certeza es verificar linaje/latencia y obtener un periodo nuevo para la solución congelada, sin convertir esa falta de datos en un requisito que impida entregar el ejercicio con sus límites.
