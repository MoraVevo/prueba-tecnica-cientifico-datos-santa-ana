# Prueba técnica de Científico de Datos — Ingenio Santa Ana

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

## Serie II en curso: calidad y contexto de sensores

La [revisión de significado físico y disponibilidad](docs/serie2-significado-disponibilidad.md) explica las familias de señales, las unidades sin confirmar y las condiciones del sensor virtual. El [notebook 07](notebooks/07_sensor_virtual_serie2.ipynb) compara Ridge, bosque y HistGradientBoosting para estimar el caudal contemporáneo con otras señales recibidas, sin usar el propio caudal ni sus rezagos. La implementación vigente utiliza solo señales actuales: 29 frente a 15 seleccionadas mediante eliminación recursiva con Ridge dentro de cada entrenamiento.

Tres validaciones consecutivas de 24 horas seleccionaron **Ridge con 15 señales actuales**: MAE medio **0.4573**, frente a **0.4622** con 29 señales. La mejora es pequeña (1.06 %), con 14 sensores menos. Con quince entradas, HistGradientBoosting obtuvo MAE 0.7640 y el bosque 0.9430. La comprobación del último día da MAE **0.3378**, RMSE **0.4234**, R² **0.9625**, WAPE **0.5564 %** y sesgo **−0.0901**; la mediana de entrenamiento obtuvo MAE 1.8936. Caudal en unidades originales sin unidad física confirmada. Como ese último día ya se había observado antes de esta revisión, sus resultados son una **comprobación reutilizada exploratoria**, no un test independiente intacto.

Se modela cada diez segundos por las parejas repetidas del objetivo, con separación de cinco minutos entre entrenamiento/evaluación y transformaciones ajustadas solo en entrenamiento. Las 43,200 filas fuera de la rejilla se conservan con motivo en `outputs/serie2_filas_fuera_modelado.csv`; no se declaran inválidas. No hay exclusión por arranque de historia. La ingeniería de memoria se retiró del código por decisión del usuario; el estudio riguroso de rezagos sigue pendiente para completar ese requisito del PDF. Las métricas no certifican el instrumento ni demuestran ahorro.

Se utiliza `data.csv` como base original. El [notebook 06](notebooks/06_eda_caldera_serie2.ipynb) compara versiones y examina faltantes, repetidos, extremos y episodios conjuntos. Ambos CSV de Kaggle coinciden byte por byte con los publicados por los autores. No se han confirmado mediciones físicamente imposibles: se conservan los extremos con banderas de revisión.

Cinco señales, incluido el flujo de vapor objetivo, repiten exactamente cada par de lecturas; debe considerarse al estudiar rezagos y validar. La fuente define 530–545 °C como rango operativo normal de temperatura de salida. Estar fuera de ese rango indica una condición anómala según los autores, sin demostrar que el sensor mida mal. La regla aplicada al archivo da 8.14 %, frente al 8.6 % publicado; se conserva esta discrepancia.

El tramo de válvula idéntica durante 63.58 minutos forma parte de 226.5 minutos entre 11.60 y 11.62. Hay otros tramos largos y cambios concordantes de la señal de agua al entrar y salir del nivel estable. Se conserva como señal mantenida por tramos; sin orden y posición real independientes no se confirma bloqueo ni error del sensor.

Para ejecutar los notebooks de Serie II, descargar `data.csv`, `data_AutoReg.csv` y `columns.csv` del [dataset indicado en el PDF](https://www.kaggle.com/datasets/nikitamanaenkov/time-series-of-industrial-boiler-operations) y guardarlos en `data/raw/serie2/`. La auditoría remite al [artículo original y sus archivos](https://pmc.ncbi.nlm.nih.gov/articles/PMC12052967/). Siguen pendientes regímenes, método no supervisado de anomalías y eficiencia; estos resultados aún no cierran la Serie II.

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
7. `07_sensor_virtual_serie2.ipynb`: tres algoritmos, comparación de 29/15 señales actuales, validación temporal y comprobación reutilizada. Requiere los archivos de Serie II; genera resultados y modelo en `outputs/`, ignorado por Git.

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

Este comando ejecuta 19 pruebas unitarias con datos pequeños y resultados conocidos; no necesita descargar datasets. Comprueba separación del prefijo TRS, conservación de datos crudos y ceros, deduplicación trazable, historia estrictamente anterior a la zafra, respaldos de la referencia y preprocesamiento ajustado solo con entrenamiento, incluidas categorías desconocidas. Para Serie II verifica selección de quince, invariancia a unidades, conservación posible de parejas correlacionadas útiles, imputación aislada y fórmulas de error.

Después del ETL y de ejecutar los notebooks 01–07:

```powershell
python -m pytest tests/integracion -q
```

Las 10 pruebas de integración requieren los datos y resultados locales. Fallan si falta un archivo; no omiten la comprobación. Reconstruyen exclusiones del ETL, métricas de 2019/2020/2021 desde predicciones por fila, elección por validación, predicciones Ridge, errores por ambiente, políticas económicas y las cuatro dimensiones y pertenencias de los segmentos. Para Serie II contrastan las métricas del test con predicciones, entradas sin objetivo, rejilla, separación temporal y correspondencia de la decisión con validación. Para ejecutar ambas suites juntas: `python -m pytest tests/unitarias tests/integracion -q` (29 pruebas).

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

La Serie I puede darse por cerrada como análisis del ejercicio, conservando sus supuestos y limitaciones explícitos. La Serie II tiene EDA y primera versión del sensor virtual; siguen pendientes el estudio riguroso de rezagos, regímenes, anomalías no supervisadas y eficiencia, junto con Series III–V, API, presentación y ZIP. La prueba completa aún no está terminada. No se incorporaron datasets externos al modelado; las fuentes de contexto están citadas arriba.
