# Inventario inicial de datasets

Inventario iniciado el 2026-10-19 con el PDF y muestras HTTP de Kaggle (máximo 4096 bytes por CSV). Posteriormente se descargaron y revisaron completos los archivos de campo y caldera, como se documenta en sus apartados. Los apartados FAOSTAT y futuros siguen siendo inspecciones de metadatos/primeras filas; sus dimensiones y cobertura completa aún no se verifican.

## Fuentes y estructura

### Campo: Louisiana

- [Kaggle](https://www.kaggle.com/datasets/siddharth0935/louisiana-sugarcane-yield-data-2010-2021).
- Archivo listado: `Copy of All_Genotypes_2010_onwards.csv` (1,950,511 bytes según la API).
- Encabezado observado: `CLONE,YEAR,STAGE,LOC,CROP,REP,T_SPACRE,TRS_TON,TCA,POPN,MSTWT,FIBER,,,`.
- Los registros representan observaciones de ensayos de variedades en determinados años, localidades, ciclos de corte, etapas y repeticiones. La clave única debe comprobarse; no asumir que CLONE-YEAR o CLONE-LOC-YEAR identifican una fila.
- Estructura longitudinal de ensayos con múltiples grupos; YEAR es tiempo calendario y CROP es edad/ciclo de cultivo, no fecha. Los metadatos describen 2010-2021, 32 localidades y 1158 genotipos, con distintas cantidades de repeticiones. Es necesario medir el balance y comprobar si se puede identificar la misma parcela o cohorte a través del tiempo; no asumir un panel de parcelas completas.
- El archivo muestra columnas finales sin nombre, notas de diccionario incrustadas y puntos `.` en algunos campos. Esos ejemplos no prueban todavía su frecuencia ni tratamiento definitivo.
- Discrepancia documental comprobada: PDF dice T_SPACRE = toneladas de azúcar/acre; la [fuente USDA](https://catalog.data.gov/dataset/louisiana-sugarcane-yield-data-2010-2021-collected-for-the-louisiana-variety-development-p) lo define como libras de azúcar/acre. El CSV USDA oficial y la copia Kaggle enlazada en el PDF son byte por byte idénticos: 1,950,511 bytes y SHA-256 `5e7b13de6bda8aed51479c5fdfc3de4a28e71ccbb45e4761b6688a34b7cff4b0`.
- En el CSV fuente, 10,485 valores de `TRS_TON` contienen un prefijo de dos dígitos sin definición pública seguido por la medición. El ETL conserva el texto completo en `TRS_TON_raw`, separa el prefijo como texto y expone el componente numérico final en `TRS_TON`; así las métricas no incorporan el prefijo.
- Auditoría completa inicial: 29,529 registros; el CSV físico trae 15 campos, doce variables esperadas y tres columnas finales sin nombre. Dos están vacías y la última contiene seis notas en las primeras filas; excluir esas notas de las variables analíticas. Entre las 18,855 filas con valores positivos y completos para T_SPACRE, TRS_TON y TCA, el producto dimensional TCA × TRS_TON coincide con T_SPACRE dentro de 1 % en 18,854 (99.9947 %). Una fila con razón observado/calculado 0.970945 queda como señal para revisar calidad; no cambia la unidad documentada. Ver `notebooks/01_revision_fuente_y_unidades.ipynb`.
- No requiere otro dataset para comenzar. Precios y costos de referencia están en el PDF y se pueden manejar como parámetros. Clima, suelo u otros enriquecimientos no son requisitos actuales.

### Caldera

- [Kaggle](https://www.kaggle.com/datasets/nikitamanaenkov/time-series-of-industrial-boiler-operations).
- Archivos listados: `data.csv`, `data_AutoReg.csv`, `columns.csv` y `41597_2025_5096_Fig3_HTML.png`.
- Dataset descargado el 2026-10-19 desde la fuente indicada por el PDF. Archivos y hashes SHA-256 quedan registrados en `data/raw/serie2/fuente.json` (carpeta local ignorada por Git).
- Ambos CSV tienen 86,400 filas, las mismas 31 columnas (`date` y 30 sensores), y la misma secuencia ordenada de marcas de tiempo desde 2022-03-27 14:28:54 hasta 2022-04-01 14:28:49, cada cinco segundos. No hay timestamps duplicados ni intervalos faltantes.
- Comparación celda por celda: difieren en exactamente 30 celdas, todas en `YJJWSLL.AV_0#` (flujo de agua de atemperación primaria). `data.csv` tiene 30 faltantes; `data_AutoReg.csv` tiene valores en esos 30 momentos y conserva idénticas las 86,370 observaciones originalmente presentes. No cambia ningún otro campo.
- Esos 30 valores faltantes forman dos tramos: 28 mediciones entre 2022-03-28 06:22:24 y 06:24:39, y 2 mediciones entre 2022-03-30 05:54:44 y 05:54:49. La versión AutoReg se entiende como una imputación, no como nuevas observaciones del sensor. Para el análisis principal se parte del archivo sin completar; la versión completada sirve para una sensibilidad cuando sea pertinente. No concatenar los archivos.
- `columns.csv` tiene 30 filas de sensores. Su campo `Variant` omite el sufijo `#`, que sí aparece en el encabezado de los CSV; al añadirlo, las 30 etiquetas corresponden con las columnas de sensores. El campo `Description` está vacío; los nombres descriptivos en inglés están en `Attribute name`.
- Objetivo de vapor observado: `ZZQBCHLL.AV_0#`, flujo de vapor principal compensado después del punto de medición; es la columna asociada al nombre abreviado del PDF.
- Kaggle describe una caldera de carbón de una planta química en Zhejiang, China y licencia CC BY 4.0. El ejercicio usa esta instalación como caso analítico; no se debe presentar como una caldera de bagazo ni trasladar directamente sus conclusiones a otra planta.
- Comparación reproducible: `notebooks/06_eda_caldera_serie2.ipynb`. El artículo fuente describe la versión completada como resultado de imputación AutoReg: [Hu et al. (2025)](https://doi.org/10.1038/s41597-025-05096-4).

El contraste posterior con [los archivos de los autores](https://doi.org/10.6084/m9.figshare.28868849.v1) confirma que ambas versiones Kaggle son idénticas byte por byte. El [artículo fuente](https://pmc.ncbi.nlm.nih.gov/articles/PMC12052967/) identifica °C y el rango operativo 530–545 para `TE_8332A`. Su aplicación al CSV da 8.14 % fuera del rango inclusivo, frente a 8.6 % publicado; esta diferencia no convierte los valores en errores de medición. Cinco señales (`SXLTCYZ`, `SXLTCYY`, `ZCLCCY`, `YCLCCY`, `ZZQBCHLL`) repiten exactamente las lecturas en 43,200 pares, compatible con actualización más lenta que la cadencia del archivo. El notebook conserva los extremos como casos de revisión, sin exclusiones.

### FAOSTAT: producción agrícola

- [Kaggle](https://www.kaggle.com/datasets/vijayveersingh/faostat-crops-and-livestock-data).
- Archivos listados: `Production_Crops_Livestock_E_All_Data.csv`, `Production_Crops_Livestock_E_All_Data_NOFLAG.csv`, y catálogos `Production_Crops_Livestock_E_AreaCodes.csv`, `Production_Crops_Livestock_E_Elements.csv`, `Production_Crops_Livestock_E_Flags.csv`, `Production_Crops_Livestock_E_ItemCodes.csv`.
- Encabezado del archivo completo: identificadores Area, Item y Element, sus códigos, Unit, y grupos anuales `Y1961,Y1961F,Y1961N` hasta `Y2023,Y2023F,Y2023N`.
- Tipo conceptual: panel anual de países/productos/indicadores. El CSV tiene formato ancho: el año está en nombres de columnas. Cada fila original identifica una combinación de área, producto e indicador, no un país-año.
- Preparación propuesta: filtrar Sugar cane y países; transformar las columnas anuales a filas preservando flags y notas; organizar área, producción y rendimiento por país-año, verificando unidades y unicidad.
- NOFLAG es una versión alternativa según su nombre, no otro país ni otro periodo que deba anexarse. Preferir el archivo con flags para evaluar confiabilidad, sujeto a comprobación de contenido. Los catálogos pueden enriquecer códigos; no añaden mediciones independientes.

### Precio del azúcar: futuros

- [Kaggle](https://www.kaggle.com/datasets/guillemservera/agricultural-futures).
- Archivo solicitado por el PDF: `individual_data/Sugar_data.csv`.
- Encabezado observado: `date,open,high,low,close,volume`. Primeras fechas observadas: 2000-03-01, 2000-03-02 y 2000-03-03. La cobertura completa aún no se verificó.
- Tipo: serie temporal financiera diaria de sesiones de mercado; no asumir que tiene observaciones para todos los días calendario. Los metadatos la atribuyen a Yahoo Finance. Pendientes: símbolo/contrato exacto, unidades, construcción de la serie y posibles cambios de contrato/errores.
- El paquete también tiene `all_agricultural_products_data.csv` y archivos individuales de Cocoa, Coffee, Cotton, Orange_Juice y Random_Length_Lumber. No son necesarios para lo solicitado; tampoco se deben anexar el consolidado y el individual de azúcar sin revisar duplicación.

## Cruces previstos

- Las series de campo, caldera y países no comparten observaciones de una misma instalación/finca. Compartir el tema azúcar o un año calendario no justifica unir las cuatro fuentes.
- Cruce relevante para Serie III: FAOSTAT país-año con precios agregados a una frecuencia compatible y rezagos justificados. Tras organizar FAOSTAT, la relación esperada es muchos países por cada año de precio mundial; comprobar unicidad y cardinalidad antes del merge.
- No unir todas las filas diarias de precios a una observación anual de producción para tratarlas como muestras independientes. Definir primero el periodo del precio que tiene sentido para la decisión agrícola, su disponibilidad y el solapamiento real.
- El pronóstico de precio puede estudiarse inicialmente solo con Sugar_data.csv. El análisis de países y el de respuesta de oferta tienen necesidades distintas.
- La recomendación agrícola puede explorar escenarios de precio y, si se decide, utilizar escenarios provenientes de Serie III; eso no implica un merge de registros históricos de campo con producción nacional.
- No se han añadido fuentes externas. Evaluar enriquecimientos solo si cubren una necesidad concreta y caben en el plazo de 48 horas.

## Cómo repetir la inspección de metadatos

API pública usada para cada referencia owner/slug: `https://www.kaggle.com/api/v1/datasets/view/{owner}/{slug}` para descripción y `https://www.kaggle.com/api/v1/datasets/list/{owner}/{slug}` para archivos. Encabezados y muestras leídos desde `https://www.kaggle.com/api/v1/datasets/download/{owner}/{slug}/{filename}` con nombre codificado en URL y cabecera `Range: bytes=0-4095`. No se usaron credenciales.
