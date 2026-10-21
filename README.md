# Prueba técnica de Científico de Datos — Ingenio Santa Ana

**Punto único de entrada a las respuestas:** consulta [respuestas directas de todas las series](docs/respuestas-prueba.md) para conocer cada decisión, conclusión y pendiente. Los informes y notebooks enlazados ahí contienen evidencia y detalle.

## Decisión de fuente y unidad: Serie I

El PDF describe `T_SPACRE` como toneladas de azúcar por acre, pero la [ficha oficial USDA-ARS](https://catalog.data.gov/dataset/louisiana-sugarcane-yield-data-2010-2021-collected-for-the-louisiana-variety-development-p) la define como **libras de azúcar por acre**. Se utiliza la definición USDA para que el precio de US$0.20/lb del ejercicio sea compatible. `TCA` está en ton de caña/acre y `TRS_TON` en lb de azúcar/ton de caña.

El CSV oficial y la copia Kaggle del enunciado se verificaron como idénticos. El descargador comprueba su SHA-256. En `TRS_TON` hay valores con prefijo sin definición: el ETL conserva el texto y prefijo aparte y utiliza el componente numérico final, coherente con `TCA × TRS_TON ≈ T_SPACRE`. No se utiliza el prefijo como variable agronómica.

## Serie I: cuatro respuestas

**Serie I completada en su alcance analítico.** Se respondieron los cuatro apartados y se revisaron los cálculos económicos, las particiones y métricas supervisadas, y la construcción de segmentos. Hay 21 pruebas automatizadas: 13 unitarias y 8 de integración con los datos locales. Las limitaciones de cobertura, ajuste ambiental, costos y error predictivo se conservan en las conclusiones. Se utiliza el dataset entregado y escenarios económicos explícitos.

| Pregunta | Respuesta | Evidencia |
| --- | --- | --- |
| Variedades y renovación | HOCP14-885, L01-299 y HO12-615 encabezan el aporte parcial anual estimado entre las 17 variedades que cumplen la cobertura propuesta. Duraciones iniciales: tres, cuatro y cuatro cosechas. La recomendación de HO12-615 como tercera opción está condicionada al ajuste ambiental aditivo; con promedios directos, L01-283 queda por encima. Prolongar podría elevar el aporte, aunque los cortes adicionales tienen menor respaldo; no se ha demostrado un máximo económico. | Notebook 03 |
| Modelo supervisado | Ridge, árbol y bosque; selección por validación temporal 2019–2020 y evaluación reservada 2021. Ridge elegido: MAE 2,145 lb/acre, R² 0.25; utilidad moderada y errores visibles. | Notebook 04 |
| Segmentación | Dos perfiles de 5 y 12 variedades, elegidos por interpretación y parsimonia. Productividad, TRS, conservación en ambientes comunes y variabilidad relativa; cobertura y excepciones individuales visibles. Otras 23 variedades quedan sin segmento por cobertura insuficiente. | Notebook 05 |
| Datos y ensayos propios | Seguimiento de parcela/cohorte, mediciones y costos; variedades aleatorizadas por bloques/sitios y seguimiento de socas; fase para contrastar políticas de renovación. | Documento de conclusiones |

El detalle de recomendaciones, certeza, impacto y riesgos está en [conclusiones de Serie I](docs/conclusiones-serie-I.md). Tres cosechas significan plantía + dos socas; cuatro significan plantía + tres socas.

`STAGE` identifica la fase de evaluación dentro del programa de mejoramiento varietal; `CROP` identifica la cosecha del ensayo. Para la recomendación económica se utilizan los ensayos outfield, correspondientes a `STAGE=5`, la etapa final de prueba de variedades para su posible uso comercial. Su diseño documentado tiene parcelas más largas, tres repeticiones y evaluación en múltiples localidades. Así se evita mezclar directamente etapas con distintos diseños y procedimientos de medición. Esta delimitación no convierte las etapas anteriores en datos incorrectos: se conservan y el modelo supervisado las utiliza. [Fuente: ficha USDA-ARS](https://catalog.data.gov/dataset/louisiana-sugarcane-yield-data-2010-2021-collected-for-the-louisiana-variety-development-program), [Shahi et al., sección 2.1](https://acsess.onlinelibrary.wiley.com/doi/10.1002/tpg2.20545).

## Serie II: respuestas y evidencia

Las [respuestas directas a todas las series](docs/respuestas-prueba.md) son el punto de entrada. La [respuesta detallada por inciso y los dos aportes de mejora](docs/conclusiones-serie-II.md) profundiza en evidencia, acciones, límites e información faltante. La campeona de diecisiete entradas se explica en el informe específico; las oportunidades no son ahorros demostrados.

La [revisión de significado físico y disponibilidad](docs/serie2-significado-disponibilidad.md) explica las familias de señales y las condiciones del sensor virtual. La comparación de tres algoritmos está en el notebook 07; el estudio temporal y la selección de la campeona vigente están en el [notebook 12](notebooks/12_rezagos_serie2.ipynb).

**Campeona vigente: Ridge con diecisiete entradas de quince sensores.** Utiliza quince señales actuales y las presiones PTCA_8322A/PTCA_8324 treinta segundos antes. MAE medio **0.356026** y WAPE agregado **0.598068 %** en tres validaciones históricas. Artefacto: `outputs/campeona_serie2/sensor_virtual.joblib`; decisión y columnas en `outputs/campeona_serie2/decision.json`.

**Justificación de la elección.** Las dos presiones anteriores aportan información de la trayectoria reciente del proceso y mejoran el error en los tres días. Se eligieron diecisiete entradas por resultados, parsimonia e interpretación aditiva de Ridge. No se incorporó toda la memoria explorada: la historia de las otras señales aporta poco en conjunto. Los coeficientes no son efectos causales. La comparación histórica completa se conserva en el [informe de rezagos](docs/rezagos-serie-II.md).

**Salvedad sobre la independencia de las entradas.** El objetivo es un caudal de vapor después de compensación. Aunque el código excluye el propio caudal y sus rezagos, y la auditoría no detectó fuga computacional, podrían existir entradas calculadas a partir de ese caudal o dependientes de su misma cadena de medición. La documentación disponible no permite comprobar ni descartar esas dependencias: faltan la fórmula de compensación, el linaje de cada señal y su disponibilidad al emitir la estimación. Por tanto, los buenos resultados se presentan como evidencia histórica exploratoria, sin afirmar independencia instrumental demostrada ni garantizar el mismo desempeño cuando falle el caudalímetro. Verificar esas dependencias y evaluar la solución congelada en un periodo nuevo son los pasos propuestos para elevar la certeza.

El [experimento de features físicas](notebooks/08_experimento_features_serie2.ipynb), separado de la campeona, prueba tres hipótesis por separado con controles de sensores. Aire × oxígeno y asimetría no mejoran el MAE medio; agua × temperatura mejora solo 0.141 % y empeora una de las tres ventanas. Se mantiene la campeona por parsimonia. El experimento no evalúa el quinto día ni modifica sus resultados; guarda evidencia en `outputs/experimento_features/`. Para reproducirlo, ejecutar el notebook 08 después del 07. Su preparación está aislada en `experimentos/features_fisicas_serie2.py` y no añade dependencias.

El [script de controles de fuga](scripts/auditar_leakage_serie2.py) reproduce el procedimiento de entrenamiento y supera ocho pruebas adversariales de alteración de información futura. No se detectó fuga computacional en el procedimiento comprobado. El linaje del caudal compensado y la disponibilidad instrumental siguen sin confirmarse, y las validaciones han participado en decisiones: el error describe desempeño histórico exploratorio, sin confirmación externa independiente. Reproducir con `python scripts/auditar_leakage_serie2.py`; no sobrescribe la campeona.

El [análisis de regímenes](notebooks/09_regimenes_operacion_serie2.ipynb) identifica con K-means **dos perfiles amplios de estado térmico y aire secundario**, con separación modesta y solapamiento. El Perfil 1 ocupa 37.60 % del tiempo, con menor temperatura del hogar y aire secundario; el Perfil 2 ocupa 62.40 %, con valores mayores y una mediana de caudal también mayor. Ambos reaparecen en los cinco bloques de 24 horas. El 91.86 % del tiempo pertenece a episodios de al menos quince minutos; esa duración es descriptiva, no una regla de alarma. No se interpretan como modos eficientes/ineficientes ni como etiquetas de falla.

Se representan siete familias mediante once entradas construidas a partir de dieciséis sensores, con medianas de un minuto y balance de dimensiones por familia. El caudal y la temperatura de salida quedan fuera del ajuste y se usan después para caracterizar perfiles. Escalado/centros se aprenden en los primeros cuatro días y se proyectan congelados al quinto, sin llamarlo test independiente. Se conservan todas las filas y sus etiquetas retrospectivas, disponibles solo al cierre del minuto. Sensibilidad a días, familias, pesos y resolución está documentada; la interpretación depende especialmente de las señales térmicas. Resultados y modelo separado en `outputs/regimenes/`; preparación en `scripts/regimenes_serie2.py`. La campeona supervisada permanece intacta.

La campeona se evalúa en tres ventanas consecutivas de 24 horas, con selección y procesamiento ajustados solo en entrenamiento y separación de cinco minutos. Su MAE por ventana es **0.400635/0.377115/0.290328** y su WAPE **0.666973/0.634154/0.491640 %**. No se evaluó el quinto día para esta evaluación. El caudal conserva unidades originales sin unidad física confirmada; las validaciones ya usadas describen desempeño histórico, sin confirmación externa independiente.

Se modela cada diez segundos por las parejas repetidas del objetivo. El ajuste final usa 34,464 filas de los primeros cuatro días, con separación final de cinco minutos y recorte inicial común de 660 segundos del estudio. Las filas fuera del ajuste se conservan con motivo en `outputs/campeona_serie2/filas_fuera_ajuste.csv`, sin declararlas inválidas. Para reproducir la campeona, ejecutar el notebook 12 después del 07 o `python -m scripts.entrenar_campeona_serie2` después del estudio de rezagos. El estimador recibe diecisiete columnas preparadas con historia anterior; treinta segundos es un rezago predictivo de la malla, sin tiempo físico certificado.

Se utiliza `data.csv` como base original. El [notebook 06](notebooks/06_eda_caldera_serie2.ipynb) compara versiones y examina faltantes, repetidos, extremos y episodios conjuntos. Ambos CSV de Kaggle coinciden byte por byte con los publicados por los autores. No se han confirmado mediciones físicamente imposibles: se conservan los extremos con banderas de revisión.

Cinco señales, incluido el flujo de vapor objetivo, repiten exactamente cada par de lecturas; debe considerarse al estudiar rezagos y validar. La fuente define 530–545 °C como rango operativo normal de temperatura de salida. Estar fuera de ese rango indica una condición anómala según los autores, sin demostrar que el sensor mida mal. La regla aplicada al archivo da 8.14 %, frente al 8.6 % publicado; se conserva esta discrepancia.

El tramo de válvula idéntica durante 63.58 minutos forma parte de 226.5 minutos entre 11.60 y 11.62. Hay otros tramos largos y cambios concordantes de la señal de agua al entrar y salir del nivel estable. Se conserva como señal mantenida por tramos; sin orden y posición real independientes no se confirma bloqueo ni error del sensor.

Para ejecutar los notebooks de Serie II, descargar `data.csv`, `data_AutoReg.csv` y `columns.csv` del [dataset indicado en el PDF](https://www.kaggle.com/datasets/nikitamanaenkov/time-series-of-industrial-boiler-operations) y guardarlos en `data/raw/serie2/`. La auditoría remite al [artículo original y sus archivos](https://pmc.ncbi.nlm.nih.gov/articles/PMC12052967/). Los cinco incisos están respondidos como análisis del archivo, incluido el estudio explícito de rezagos. Siguen pendientes confirmación instrumental, validación externa y pruebas operativas para elevar certeza; no se presentan como realizadas.

## Serie III: producción mundial y riesgo de precio

**Lectura económica:** Guatemala tiene una fortaleza de productividad territorial en las referencias estudiadas; el riesgo de precio permanece material y la oferta mundial muestra una asociación diferida con los incentivos. La recomendación es conservar productividad, presupuestar escenarios adversos y evaluar expansión por margen esperado de varias zafras, incluyendo posible respuesta de competidores. [Conclusiones y fundamento económico](docs/conclusiones-serie-III.md#lectura-económica-y-decisiones) separan evidencia, mecanismo y decisión, sin exigir identificación causal completa para recomendar criterios de gestión.

**Primer inciso respondido.** Las [conclusiones de Serie III](docs/conclusiones-serie-III.md) describen dos perfiles sobre 74 áreas con cobertura suficiente. Guatemala pertenece al de mayor escala/rendimiento. Indonesia, Bolivia y Vietnam son el núcleo más persistente de referencia por estructura territorial; Nepal/Kenia dependen de la tolerancia de superficie. El rendimiento de Guatemala supera la referencia anual mediana, pero la calidad de datos y los recursos omitidos impiden afirmar ventaja comparativa económica o eficiencia total.

El [notebook 13](notebooks/13_eda_faostat_serie3.ipynb) verifica FAOSTAT; el [notebook 14](notebooks/14_segmentacion_paises_serie3.ipynb) contiene representación, grupos, pares, productividad relativa y sensibilidad. Exige cobertura por bloques de 1961–2023 y cuatro de cinco años recientes; conserva 38 áreas excluidas con sus datos/motivos. La proporción del rendimiento de Guatemala frente a la mediana de cinco pares es 1.679, con límites explícitos por flags E/I y número de referencias. Evidencia en `outputs/serie3_segmentacion/`, fuera de Git; preparación en `scripts/segmentar_paises_serie3.py`.

**Segundo inciso respondido con verificación parcial de continuidad.** El [notebook 15](notebooks/15_precios_azucar_serie3.ipynb) estudia calidad, volatilidad, estados descriptivos y extremos. Volatilidad histórica anualizada 33.36 % observada y 31.10 % en sensibilidad restringida, con 5,748 de 6,096 retornos y todas las filas/motivos conservados. Las 11 inconsistencias OHLC coinciden con fronteras mensuales de posible enlace; 93 volúmenes cero y ausencia de contrato diario limitan el uso. Los contrastes externos corroboran puntualmente una caída extrema, sin certificar toda la serie. [Conclusiones del inciso 2](docs/conclusiones-serie-III.md#2-volatilidad-regímenes-y-extremos-del-azúcar-no-11) y [fuentes](docs/fuentes-precios/indice.md).

**Tercer inciso respondido como ejercicio histórico.** El [notebook 16](notebooks/16_pronostico_azucar_serie3.ipynb) compara ingenuos y Ridge mediante selección/calibración/evaluación temporal separadas. El ingenuo del último cierre se elige a ambos horizontes: WAPE 3.95 % a un mes y 9.31 % a tres. Se pronostica el promedio mensual de cierres publicados; la emisión final utiliza mayo de 2024, con bandas 80/95 % para junio/agosto. Junio parcial se conserva aparte; la continuidad no certificada sigue limitando el uso comercial. [Resultados y límites](docs/conclusiones-serie-III.md#3-pronóstico-a-uno-y-tres-meses-con-incertidumbre).

**Cuarto inciso respondido sin identificación causal.** El [notebook 17](notebooks/17_oferta_precio_serie3.ipynb) cruza años completos de precio y FAOSTAT, compara niveles/cambios y rezagos de uno/dos años sobre veinte ecuaciones anuales por ámbito. La señal mundial a dos años permanece en cambios y mejora errores retrospectivos; en Guatemala el precio no supera la media histórica. No justifica ampliar superficie local ni demuestra un plazo físico. [Método, magnitudes y límites](docs/conclusiones-serie-III.md#4-respuesta-de-superficie-y-producción-al-precio).

El archivo de precios está en `data/raw/serie3/Sugar_data.csv`; descarga reproducible con `python scripts/descargar_azucar_serie3.py`. Preparación en `scripts/analizar_precios_serie3.py`, `scripts/pronosticar_azucar_serie3.py` y `scripts/analizar_oferta_serie3.py`; resultados en `outputs/serie3_precios/`, `outputs/serie3_pronostico/` y `outputs/serie3_oferta/`, fuera de Git. Los cuatro incisos tienen respuesta analítica; el linaje y ajuste exacto de contratos no están confirmados.

## Reproducción

Entorno preparado con Python 3.13.14. En Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/descargar_serie1.py
python scripts/etl_serie1.py
python -m ipykernel install --user --name prueba-santa-ana --display-name "Python (prueba-santa-ana)"
jupyter lab
```

Ejecutar los notebooks en orden:

1. `01_revision_fuente_y_unidades.ipynb`: procedencia y unidades.
2. `02_perfil_eda_inicial_serie1.ipynb`: calidad, repetidos y cobertura.
3. `03_analisis_economico_serie1.ipynb`: aporte, políticas de renovación, precio y certeza.
4. `04_modelo_supervisado_serie1.ipynb`: tres algoritmos, referencias, evaluación temporal y ejemplo de siguiente zafra.
5. `05_segmentacion_variedades_serie1.ipynb`: variables por clon, elección de segmentos y lectura gerencial.
6. `06_eda_caldera_serie2.ipynb`: comparación de archivos, calidad, correlaciones y disponibilidad de sensores.
7. `07_sensor_virtual_serie2.ipynb`: comparación de algoritmos y señales actuales. La campeona vigente se reproduce al cierre del notebook 12.
8. `08_experimento_features_serie2.ipynb`: tres features físicas y controles de sensores; replica la base de quince y evalúa solo las tres ventanas de validación. No cambia la campeona. Genera tablas y figura en `outputs/experimento_features/`.
9. `09_regimenes_operacion_serie2.ipynb`: dos perfiles de operación, interpretación física, recurrencia y sensibilidad temporal/de variables. Conserva correspondencia de todas las filas y genera evidencia en `outputs/regimenes/`. El análisis posterior de anomalías usa solo el último minuto cerrado.

10. `10_anomalias_serie2.ipynb`: inciso 4, Isolation Forest con contexto temporal cerrado, revisión de episodios y omisiones, reglas propuestas de persistencia y distinción equipo/sensor. Conserva las 86,400 filas y genera evidencia en `outputs/anomalias/`; no cambia la campeona.
11. `11_revision_extremos_termicos_serie2.ipynb`: revisión de calidad de los cuatro episodios que contienen extremos térmicos a más de cinco grados de la banda. Contrasta continuidad/contexto y alcance en entrenamiento; conserva con marca 696 filas, cero exclusiones por falta de error demostrado. Exporta decisiones por fila, contexto y cuarentena vacía a `outputs/revision_termica/`. No certifica el sensor ni cambia modelos.
12. `12_rezagos_serie2.ipynb`: inciso 3, correlaciones de niveles/cambios y comparación temporal con historia seleccionada solo en entrenamiento. Localiza utilidad en las dos presiones anteriores y ajusta la campeona de diecisiete entradas; no usa caudal pasado ni evalúa el quinto día. Preparación en `experimentos/rezagos_serie2.py`, evidencia en `outputs/rezagos/`. Puede ejecutarse después del 07.
13. `13_eda_faostat_serie3.ipynb`: cobertura, flags, unidades, agregados, coherencia y conservación de caña en 1961–2023. Evidencia en `outputs/serie3_eda/revision/`.
14. `14_segmentacion_paises_serie3.ipynb`: primer inciso de Serie III, perfiles de países, pares de Guatemala y productividad territorial relativa con sensibilidad y límites de calidad. Requiere ejecutar el 13. Evidencia en `outputs/serie3_segmentacion/`.
15. `15_precios_azucar_serie3.ipynb`: segundo inciso, continuidad parcialmente verificada, volatilidad, estados descriptivos y extremos con contraste externo puntual. Requiere `Sugar_data.csv` y se ejecuta independientemente del 13/14. Evidencia en `outputs/serie3_precios/`.
16. `16_pronostico_azucar_serie3.ipynb`: tercer inciso, promedio mensual a uno/tres meses, comparación frente al ingenuo e intervalos calibrados antes de la evaluación. Requiere `Sugar_data.csv`, sin ejecutar previamente 13–15. Evidencia en `outputs/serie3_pronostico/`.
17. `17_oferta_precio_serie3.ipynb`: cuarto inciso, asociación de superficie/producción con precio y rezagos, estabilidad y diagnóstico temporal retrospectivo. Requiere ejecutar el 13 y disponer de `Sugar_data.csv`. Conserva todas las exclusiones con motivo en `outputs/serie3_oferta/`. No identifica efectos causales.

Para anomalías se ajustan detector y cuantiles en cuatro días; el quinto es una reproducción descriptiva ya vista, no un test independiente. El percentil 99 y la persistencia generan 28 avisos multivariables en cinco días. Hay también dos interrupciones de datos y 85 avisos térmicos con una banda bibliográfica que requiere revisión operativa. Son avisos de desviación, no fallas confirmadas: sin etiquetas no se estiman precisión, falsas alarmas reales ni anticipación. El detector omite el pico de corriente 51.28 y la caída de retornos revisados; requiere complementar con límites físicos autorizados. Cambiar el percentil a 98/99.5 produce 60/17 avisos: no se afirma un umbral óptimo. Las seis presiones concordantes son una familia correlacionada y una perturbación del DCS sigue siendo una explicación posible. Las reglas son simulaciones offline, sin infraestructura ni acción automática.

El mismo notebook 10 incorpora un complemento exploratorio para corriente y ambos retornos: mediana/MAD por contexto ajustadas solo en cuatro días, marcas bilaterales a seis escalas robustas y avisos de persistencia separados. Marca el pico 51.28 y las dos caídas de retornos; estos últimos activan aviso cinco/diez segundos después del mínimo, sin evidencia de anticipación a falla. Corriente produce 384 tramos de marcas pero solo dos avisos sostenidos: se recomienda resumen de revisión, no una alarma de equipo por marca. Los tres sensores se eligieron tras inspeccionar los casos y falta validación nueva; umbral provisional, sin unidades/límites físicos certificados. No altera Isolation Forest ni Ridge. La sensibilidad, carga completa y limitaciones están en el notebook y `outputs/anomalias/`.

La evaluación posterior de carga, en el mismo notebook, contrasta los 384 tramos de corriente con cuatro [fuentes primarias](docs/fuentes-anomalias/indice.md). Son 3.2 tramos/hora, máximo cuatro inicios en diez minutos; 372 (96.875 %) corresponden a una sola lectura. Ese conteo no demuestra saturación ni mala precisión, pero tampoco justifica alarmas de intervención sin acción/consecuencia definidas. Se conserva el complemento diagnóstico y se recomienda validación operativa/temporal antes de convertir marcas en alarmas; no se ajusta el umbral para obtener un número cómodo. La integración reconstruye ventanas, duración y escenarios de carga, sin cambios en parámetros.

También se pueden ejecutar sin interfaz, por ejemplo:

```powershell
python -m nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=600 notebooks/04_modelo_supervisado_serie1.ipynb
```

El ETL guarda 29,403 filas analíticas y separa 126 copias exactas adicionales, con motivo por fila. Mantiene 224 registros de claves repetidas con mediciones distintas y 23 alertas dimensionales. Cada análisis conserva sus exclusiones, motivos y salidas en `data/processed/`. Las alertas se tratan mediante escenarios y no se corrige una medición arbitrariamente. La fuente permanece intacta.

## Pruebas automatizadas

Desde la raíz del proyecto, con el entorno activado:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Este comando ejecuta 42 pruebas unitarias con datos pequeños y resultados conocidos; no necesita descargar datasets. Comprueba separación del prefijo TRS, conservación de datos crudos y ceros, deduplicación trazable, historia estrictamente anterior a la zafra, respaldos de la referencia y preprocesamiento ajustado solo con entrenamiento, incluidas categorías desconocidas. Para Serie II verifica selección de quince, invariancia a unidades, conservación posible de parejas correlacionadas útiles, imputación aislada, fórmulas de error y las tres features experimentales con preparación ajustada solo en entrenamiento. Para regímenes comprueba conservación, disponibilidad al cierre, independencia respecto del caudal, pesos y duraciones de episodios. Para anomalías verifica contexto sin futuro, persistencia/recuperación, episodios e imputación aislada, además de referencias MAD conocidas y marcas aisladas sin aviso. Para rezagos comprueba orientación temporal y selección invariante ante alteraciones futuras.

Después del ETL y de ejecutar los notebooks 01–17:

```powershell
python -m pytest tests/integracion -q
```

Las 30 pruebas de integración requieren los datos y resultados locales. Fallan si falta un archivo; no omiten la comprobación. Reconstruyen exclusiones del ETL, métricas de 2019/2020/2021 desde predicciones por fila, elección por validación, predicciones Ridge, errores por ambiente, políticas económicas y las cuatro dimensiones y pertenencias de los segmentos. Para Serie II contrastan las métricas del test con predicciones, entradas sin objetivo, rejilla, separación temporal y correspondencia de la decisión con validación. Para el experimento verifican conservación y alcance de filas y reconstruyen nueve series de predicciones con las fórmulas y la solución matricial de Ridge, sin reutilizar el módulo experimental. Para regímenes reconstruyen la vista con otra ruta de agregación, recalibran solo con cuatro días, asignan por distancias manuales y contrastan perfiles/duraciones/conservación. Para anomalías reconstruyen contexto por búsqueda binaria, imputación manual, reajuste directo de Isolation Forest, cuantiles y máquina de estados; verifican conservación y huellas de los artefactos previos. El complemento contrasta referencias con NumPy, puntajes individuales, episodios y sensibilidad, conservando picos sin confundirlos con avisos sostenidos. La revisión térmica contrasta episodios completos, selección exhaustiva de extremos, contextos originales y conservación sin excluir por rareza. Para rezagos se reconstruyen correlaciones con NumPy, entradas históricas por timestamps y dieciocho predicciones por solución matricial de Ridge, con filas y huellas protegidas. Para ejecutar ambas suites juntas: `python -m pytest tests/unitarias tests/integracion -q` (72 pruebas).

Para Serie III, las pruebas unitarias verifican ceros trazables, cobertura histórica y selección de pares independiente del rendimiento. Las de integración reconstruyen la vista FAOSTAT desde el crudo, exclusiones, rasgos históricos, distancias, grupos y referencias anuales por otra ruta de cálculo. Para precios se contrastan conservación, fronteras de calendario sin convertir la última fila truncada en vencimiento, exclusiones con ambos extremos, retornos sin puentes, ventanas sin futuro, volatilidad y estados con ecuaciones NumPy. Para pronóstico se reconstruyen agregación mensual, todas las predicciones históricas por ecuación matricial, etiquetas maduras, selección, cuantiles, cobertura y Winkler; pruebas de perturbación comprueban que el futuro no cambia predicciones previas ni la elección realizada en selección. Para respuesta de oferta se comprueban cruce anual, unidades, flags y exclusiones desde los crudos, orientación de rezagos, coeficientes conocidos, perturbación de objetivos futuros y reconstrucción QR independiente de todos los ajustes/predicciones y errores. La versión histórica disponible de FAOSTAT no está certificada: el diagnóstico temporal utiliza versiones finales.

El notebook 04 y las pruebas comparten `scripts/modelado_serie1.py`. Las predicciones de todos los métodos quedan en `serie1_predicciones_validacion.csv` y `serie1_predicciones_modelos_2021.csv`, dentro de `data/processed/`. Las pruebas revisan implementación y consistencia; la evaluación temporal mide el desempeño predictivo y no demuestra causalidad ni precisión futura garantizada.

## Supuestos y límites que afectan la decisión

- Se aplica el costo de US$14/ton a `TCA` (toneladas de caña/acre), suponiendo compatibilidad entre las unidades de tonelada del dataset y el supuesto económico; el PDF no especifica el tipo. La fórmula se reprodujo independientemente sin discrepancia aritmética.
- La rotación supone una cosecha anual, renovación inmediata, costos constantes y sin descuento ni descanso. Se comparan aportes **esperados**, no flujos observados de la misma parcela.
- Los precios de US$0.15, 0.20 y 0.25/lb son escenarios ilustrativos de ±25 %; no son una distribución de mercado estimada.
- La recomendación exige cobertura temporal/geográfica por corte y muestra duraciones adicionales de menor certeza. El escenario sin ajuste ambiental cambia el tercer puesto.
- El modelo usa entradas disponibles antes de la zafra y medias de años anteriores. La precisión observada es limitada y varía entre ambientes; en MAGNOLIA/etapa 5, el MAE y el sesgo positivo de 2021 son 3,498.54 lb/acre (72 observaciones). Se guarda el desglose por localidad/etapa; el MAE no es un intervalo de confianza.
- Las validaciones de 2019 y 2020 son zafras contrastantes, no una referencia de años “normales”. En las filas usadas por el modelo, el promedio de `T_SPACRE` cayó entre 21 % y 27 % por etapa de 2018 a 2019 y subió entre 30 % y 41 % de 2019 a 2020. LSU AgCenter relaciona la baja de 2019 con la cosecha muy húmeda de 2018 y condiciones meteorológicas adversas. Para 2020 documenta efectos de las restricciones por COVID en operaciones de cruzamiento y en algunas pruebas de vivero; los ensayos finales outfield se reportaron en 12 localidades con tres repeticiones, y el resumen estatal informa mayores rendimientos de caña que en 2019. El dataset no permite aislar el efecto de COVID frente al clima, cambios de cobertura, manejo o medición; por ello se reportan errores por año y no se atribuye causalidad a la pandemia. [Contexto 2019](https://www.lsuagcenter.com/profiles/rbogren/articles/page1578688656809), [programa varietal 2020](https://www.lsuagcenter.com/~/media/system/2/d/4/f/2d4f56bf87ae85228f7652f9be15d589/03%20variety%20section%202020%20updatedpdf.pdf), [resumen estatal 2020](https://www.lsuagcenter.com/articles/page1677766893201).
- En las validaciones Ridge, el sesgo `predicción − observado` fue +2,148 lb/acre en 2019 y −1,078 lb/acre en 2020. El aumento de `T_SPACRE` también aparece en combinaciones coincidentes de `STAGE`, `CLONE`, `LOC` y `CROP` entre ambos años (418 combinaciones; sube en 90 % de las de etapa 3, 95 % de etapa 4 y 76 % de etapa 5). Son claves coincidentes, no parcelas pareadas: la fuente no tiene identificador de parcela/cohorte. Esto apunta a un cambio amplio entre zafras, pero no identifica su causa.
- Se preservan listas de variedades sin cobertura suficiente para economía/segmentación. Los faltantes extensos de fibra no se imputan para obligar a usarla.

## Archivos y entrega

`notebooks/` contiene evidencia reproducible; `scripts/` contiene descarga y ETL; `docs/` contiene conclusiones y continuidad; `bitacora.md` registra decisiones e hipótesis corregidas. `requirements.txt` fija dependencias. `data/raw/` y `data/processed/`, el PDF confidencial y entornos locales están excluidos de Git. El ZIP final debe excluir datasets e incluir `.git`, según el PDF.

## Pendientes de la prueba completa

La Serie I puede darse por cerrada como análisis del ejercicio, conservando sus supuestos y limitaciones explícitos. La Serie II responde sus cinco incisos como análisis exploratorio: EDA, sensor virtual con estudio separado de rezagos, regímenes, anomalías con reglas propuestas y dos oportunidades con sus límites de impacto. Para uso en planta faltan confirmación instrumental, periodo nuevo y pruebas operativas. La Serie III responde sus cuatro incisos como análisis: países/pares, riesgo, pronósticos y relación de oferta/precio con rezagos. Conserva continuidad parcialmente verificada y ausencia de identificación causal. También quedan Series IV–V, API, presentación y ZIP. La prueba completa aún no está terminada. No se incorporaron datasets externos al modelado; las fuentes de contexto están citadas arriba.
