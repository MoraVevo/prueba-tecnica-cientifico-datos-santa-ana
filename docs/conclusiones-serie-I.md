# Serie I: respuestas a Gerencia

Estado: primer borrador completo de los cuatro apartados, con cálculos y métricas reproducibles. Sigue pendiente la revisión independiente de fórmulas, supuestos y resultados acordada. Ejecutar un notebook no equivale a validar el análisis.

## 1. Tres variedades, renovación y certeza

Recomendaría ampliar las siguientes variedades dentro del ejercicio:

| Variedad | Renovación propuesta | Aporte parcial esperado por acre/año, US$0.20/lb | Certeza de la recomendación |
| --- | --- | ---: | --- |
| HoCP14-885 | Después de 3 cosechas: plantía + 2 socas | US$727.58 | Media-baja para duración: fuerte desempeño, pero solo dos años en el último corte admitido; la tercera soca tiene un año y queda como sensibilidad. |
| L01-299 | Después de 4 cosechas: plantía + 3 socas | US$632.66 | Media: cada corte recomendado tiene al menos diez años y doce localidades; el horizonte de cinco cosechas tiene datos de una localidad y merece seguimiento. |
| Ho12-615 | Después de 4 cosechas: plantía + 3 socas | US$629.21 | Media-baja: al menos tres años y once localidades por corte; el tercer puesto cambia frente a L01-283 al omitir el ajuste ambiental. |

La duración maximiza el aporte promedio anual de repetir una rotación: sumar ingresos y costos esperados de sus cortes, descontar renovación una sola vez y dividir por el número de cosechas. Se supone una cosecha por año, renovación inmediata, costos constantes y sin descuento ni año de descanso. El aporte incluye US$14/ton de caña, US$350/acre/año y US$1,100/acre por renovación; no es una utilidad neta completa.

Se utiliza etapa 5. Se promedian repeticiones por clon/corte/año/localidad y se ajusta cada variedad por su diferencia respecto a L01-299 en ambientes compartidos. Se exige plantía y dos socas con al menos dos años y dos localidades por corte; la tercera soca se admite si alcanza esa cobertura. La falta de llave de cohorte limita la interpretación como flujo realizado, pero permite comparar políticas esperadas bajo estos supuestos. No se atribuye causalidad a la edad por esta comparación.

### Precio volátil

| Variedad | US$0.15/lb | US$0.20/lb | US$0.25/lb |
| --- | ---: | ---: | ---: |
| HoCP14-885 | US$251.45 | US$727.58 | US$1,203.71 |
| L01-299 | US$208.94 | US$632.66 | US$1,056.38 |
| Ho12-615 | US$204.42 | US$629.21 | US$1,054.01 |

Son escenarios ilustrativos de caída/subida de 25 % alrededor del precio del PDF, sin probabilidades ni datos de mercado añadidos. Las duraciones recomendadas se mantienen en esos escenarios, mientras el aporte cambia sustancialmente. Precios fuera del rango y otros costos pueden cambiar la política.

Con 500 remuestras de años, el rango central del 90 % del aporte de la política elegida es aproximadamente US$652–834 para HoCP14-885, US$572–700 para L01-299 y US$570–684 para Ho12-615. La misma duración reaparece en 100 %, 100 % y 98.6 % de remuestras; eso mide estabilidad dentro de esta muestra y modelo de decisión, no la probabilidad de superioridad real. La incertidumbre del tercer puesto es mayor que la pequeña diferencia entre L01-299 y Ho12-615.

La comparación sin ajuste produce US$637.01, US$632.66 y US$601.45 por acre/año para esas mismas políticas; allí L01-283 (US$605.10) ocupa el tercer puesto. Mantendría Ho12-615 como tercera elección condicional al ajuste por ambiente, con L01-283 como alternativa cercana. No asignaría porcentajes de área sin datos de superficie, disponibilidad y restricciones del ejercicio.

Revisaría la decisión después de cada cosecha: mantener la siguiente soca mientras su aporte esperado supere el promedio anual de reiniciar la rotación. Las duraciones adicionales observadas con cobertura reducida se muestran en el notebook; no se afirma que sean inferiores por falta de datos. El seguimiento evita convertir la recomendación inicial en una regla rígida.

Evidencia: `notebooks/03_analisis_economico_serie1.ipynb`; salidas locales de políticas, sensibilidad y remuestreo en `data/processed/`.

## 2. Modelo supervisado para la siguiente zafra

Se comparan Ridge, árbol de decisión y bosque aleatorio. Ridge se elige por el menor MAE promedio al entrenar hasta 2018 y validar 2019, y entrenar hasta 2019 y validar 2020. En esos dos cortes su MAE medio es 2,405.64 lb/acre, frente a 2,787.95 del árbol y 2,882.48 del bosque. El año 2021 se reserva para evaluación final y no determina la elección.

| Método | MAE 2021, lb/acre | RMSE 2021, lb/acre | R² 2021 |
| --- | ---: | ---: | ---: |
| Ridge elegido | 2,144.55 | 2,770.97 | 0.25 |
| Árbol de decisión | 2,330.43 | 2,983.90 | 0.13 |
| Bosque aleatorio | 2,261.69 | 2,877.42 | 0.19 |
| Referencia histórica de clon/corte | 2,662.69 | 3,385.62 | -0.12 |
| Referencia de clon/ambiente reciente | 2,270.33 | 2,938.43 | 0.16 |

Las entradas son variedad, localidad, etapa, corte planificado, año y promedios históricos del azúcar por clon, localidad y clon/corte, calculados con años estrictamente anteriores. El código ajusta codificación, imputación y escalado solo con cada entrenamiento. No usa mediciones de la cosecha que pretende anticipar: TCA y TRS_TON casi reconstruyen el objetivo y generarían fuga de información.

Ridge ofrece una explicación aditiva; el árbol aporta reglas y el bosque permite interacciones. Se muestran coeficientes numéricos y reglas en el notebook, con interpretación asociativa. Tras conservar la evaluación de 2021, se reajusta Ridge hasta ese año para ilustrar una predicción de 2022, siguiente zafra disponible en el ejercicio.

La mejora en 2021 es de aproximadamente 19.5 % respecto a la referencia histórica sencilla y 5.5 % respecto a la referencia reciente más exigente. En etapa 5 el MAE es 1,898.11 lb/acre. El error absoluto agregado representa aproximadamente 25.5 % del azúcar observado; la utilidad es moderada para presupuestar y comparar escenarios, y baja para comprometer un rendimiento exacto por parcela. A US$0.20/lb, el MAE global equivale a unos US$428.91/acre de ingreso bruto, sin ser un intervalo de confianza ni error del beneficio total.

En 2019 todos los algoritmos tienen R² negativo: hay una variación anual que estas entradas no explican bien. No se inventa una causa climática. La sensibilidad incluyendo alertas de calidad en entrenamiento e historia da MAE cercano a 2,135.10 en las mismas filas limpias de 2021; se conserva el escenario principal más conservador. Las predicciones deben acompañarse de errores por corte/ambiente y monitoreo de sesgo; se requiere calibración específica antes de ofrecer intervalos de predicción.

Evidencia: `notebooks/04_modelo_supervisado_serie1.ipynb`; comparación temporal, predicciones y evaluación por fila en `data/processed/`.

## 3. Segmentación y significado gerencial

Se segmentan 17 variedades con cobertura de plantía y dos socas, dos años y dos localidades por corte. Las restantes de etapa 5 se conservan en una lista sin segmento por falta de evidencia. Las cuatro dimensiones son productividad de azúcar, TRS, conservación segunda soca/plantía y variabilidad relativa entre localidades/años centrada por clon/corte. No se completa fibra ausente para forzar su uso.

Se comparan K-means con 2, 3 y 4 grupos sobre variables estandarizadas. Se elige la mayor silueta entre soluciones con al menos tres variedades por grupo: dos segmentos, silueta aproximada de 0.30. Es una separación moderada, útil como perfil inicial y no como clasificación biológica definitiva.

| Perfil | Variedades | Azúcar medio, lb/acre | TRS, lb/ton | Conservación en segunda soca | Variabilidad relativa |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1: más TRS, más caída y variación | 4 | 7,940 | 290 | 74 % | 0.126 |
| 2: más productividad y conservación | 13 | 8,365 | 278 | 82 % | 0.099 |

Perfil 1: HO07-613, HOCP00-950, HOCP96-540 y L03-371. Su calidad más alta no compensa automáticamente la menor productividad/conservación; conviene revisar económicamente cada soca con mayor cautela. Perfil 2: las otras trece variedades elegibles, incluidas las tres recomendadas. Permite explorar permanencia de socas y ampliación según su aporte, evitando tratar a todos sus miembros como igualmente buenos.

El cociente de conservación usa medias de muestras por corte, no seguimiento causal de una misma parcela. La composición de ensayos, poca muestra de variedades y ausencia de causas de descarte afectan los perfiles. La segmentación complementa el ranking económico y el modelo supervisado; no sustituye esas decisiones.

Evidencia: `notebooks/05_segmentacion_variedades_serie1.ipynb`; miembros, perfiles y alternativas de K en `data/processed/`.

## 4. Datos propios y diseño de ensayos propuesto

### Qué capturar

| Bloque | Campos prioritarios | Decisión que permite |
| --- | --- | --- |
| Identidad y seguimiento | ID único de ensayo, parcela, bloque, cohorte de plantación; variedad/lote de semilla; ubicación, superficie y unidades; fechas de siembra/cosecha; corte planeado/real | Seguir la misma unidad entre socas y distinguir repeticiones de registros duplicados. |
| Productividad y calidad | Caña pesada por parcela y área cosechada, azúcar recuperable y protocolo de laboratorio, TRS, fibra cuando se mida, tallos y peso de muestra | Medir rendimientos y explicar el intercambio entre cantidad de caña y recuperación de azúcar. |
| Ambiente y manejo | Suelo y análisis, riego/lluvia, fertilización, labores, plagas/enfermedades, daños y fecha de cada aplicación | Explicar variación, comparar ambientes y disponer de entradas conocidas antes de la zafra. |
| Economía | Preparación, semilla/siembra, mantenimiento desglosado, corte/alce/transporte, área/cantidades/precio de cada insumo, precio efectivo y condiciones de liquidación | Completar el aporte, comparar renovación y someter la política a precio/costos reales. |
| Pérdidas y decisiones | Parcelas sin cosecha, resiembra o abandono y su causa; fecha/motivo de renovación; rendimientos cero confirmados; ausencias y correcciones trazables | Evitar estudiar solo las socas supervivientes y distinguir un cero real de un dato ausente. |

### Cómo ensayar

Propondría un ensayo de las tres variedades recomendadas más la variedad de referencia operativa de la empresa, en sitios que representen sus ambientes principales. Dentro de cada sitio, formar bloques de suelo/manejo comparable y asignar variedades al azar. Como estructura inicial ilustrativa: tres sitios, tres bloques y cuatro variedades únicas dan 36 parcelas experimentales; las repeticiones definitivas se dimensionan con variación por parcela y diferencia económicamente relevante. No se consideran tallos individuales como réplicas independientes de parcelas.

Mantener el mismo identificador y seguir cada parcela desde plantía durante al menos tres socas, documentando retiros y manejo. Usar área de medición, protocolo de pesaje y laboratorio consistentes, con orden de muestreo aleatorio cuando corresponda. Capturar fechas reales para calcular duración, descansos y costo de oportunidad, en vez de asumir siempre un año por corte.

Para evaluar directamente la política de renovación, añadir una segunda fase con parcelas asignadas al azar a renovar después de dos, tres o cuatro cosechas y compararlas durante un horizonte común. Así se observa el costo y la producción de reiniciar, además de la soca que se deja de cosechar. La fase y sus recursos se acuerdan con Gerencia; aquí se propone el diseño y no se ejecuta captura adicional.

El análisis separaría efecto de variedad, corte y ambiente, usando la parcela seguida en el tiempo y bloques. Para pronosticar se reservaría una zafra completa y, si se desea ampliar a fincas nuevas, también localidades completas. Cada zafra cerraría con aporte económico, estabilidad del ranking, errores de pronóstico y decisión de mantener/renovar, revisando los supuestos antes de ampliar superficie.
