# Fuentes y estructura de datos

## Serie I: ensayos de variedades de Louisiana

Fuente: [dataset indicado en el PDF](https://www.kaggle.com/datasets/siddharth0935/louisiana-sugarcane-yield-data-2010-2021), contrastado con la publicación USDA. Contiene 29,529 registros de ensayos de 2010–2021, con variedad, año, localidad, etapa, corte, repetición y mediciones agronómicas. No identifica parcelas/cohortes persistentes.

T_SPACRE se interpreta como libras de azúcar por acre conforme a USDA; TRS_TON como lb/ton de caña y TCA como toneladas de caña por acre. El ETL conserva el texto de TRS_TON y separa su prefijo sin significado confirmado. La fuente original contiene tres columnas auxiliares, incluidas notas; las variables analíticas y exclusiones están documentadas en el notebook 01.

La recomendación de variedades y la evaluación económica usan ensayos de etapa 5 y los costos/precios referenciales del enunciado. Evidencia y límites en [conclusiones de Serie I](conclusiones-serie-I.md).

## Serie II: operación de caldera

Fuente: [Time-Series of Industrial Boiler Operations](https://www.kaggle.com/datasets/nikitamanaenkov/time-series-of-industrial-boiler-operations). Archivos locales data/raw/serie2/data.csv, data_AutoReg.csv y columns.csv. El original contiene 86,400 registros, treinta sensores y pasos de cinco segundos durante cinco días. La versión AutoReg difiere en las treinta celdas ausentes de agua de atemperación; el análisis usa data.csv.

Cinco señales repiten cada pareja de lecturas, incluido el caudal objetivo. Las unidades, posiciones, latencias y linaje de algunos tags no están confirmados. La temperatura final sí tiene referencia en °C; su banda bibliográfica no es un límite de seguridad. Datos y restricciones en [significado y disponibilidad](serie2-significado-disponibilidad.md).

## Serie III: producción de caña

Fuente local FAOSTAT Production: Crops and livestock products, con tablas de valores/flags y diccionarios en data/raw/serie3/. El cultivo Sugar cane tiene 432 filas área/indicador de 144 áreas y años 1961–2024. El análisis del ejercicio utiliza 1961–2023, área cosechada en ha, rendimiento en kg/ha y producción en t.

La vista de análisis conserva 112 países/territorios y 21,168 celdas; guardo separados, con motivo, los agregados, los predecesores no empalmados y 2024. Las versiones con y sin flags coinciden numéricamente para caña. Evidencia en el [notebook del EDA](../notebooks/13_eda_faostat_serie3.ipynb).

## Serie III: precios de azúcar

Fuente: [Agricultural Commodities Futures](https://www.kaggle.com/datasets/guillemservera/agricultural-futures), archivo individual_data/Sugar_data.csv. Ruta local data/raw/serie3/Sugar_data.csv: 6,097 filas entre 2000-03-01 y 2024-06-24, con date/open/high/low/close/volume. No hay fechas duplicadas ni celdas vacías.

El archivo conserva volúmenes cero y relaciones OHLC para investigar. Todavía no certifico el enlace de contratos, los ajustes ni el significado de cierre/liquidación. [Procedencia y descarga reproducible](fuente-azucar-serie-III.md).

## Conservación y entrega

Los datos crudos y procesados, outputs y el PDF confidencial están fuera de Git. El ZIP de entrega debe excluir datasets y conservar .git. Cada análisis distingue exclusiones de ámbito, marcas de revisión y errores demostrados; el crudo permanece íntegro.
