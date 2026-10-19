# Serie I: significado de columnas y lógica de negocio

El dataset representa ensayos de variedades de caña de Louisiana. Una observación describe una combinación de variedad, año del ensayo, localidad, etapa de selección, ciclo de corte y repetición, con mediciones agronómicas. No representa directamente una parcela comercial de Santa Ana.

## Identificación y condiciones del ensayo

| Columna | Qué representa | Lógica de negocio y cuidado analítico |
| --- | --- | --- |
| `CLONE` | Código del genotipo/variedad evaluada. | Permite comparar materiales genéticos. En distintas etapas del programa hay selección progresiva: los clones que llegan a etapas avanzadas ya pasaron filtros. No suponer que cualquier clone es una variedad comercial disponible ni que sus resultados son comparables sin ajustar por etapa. |
| `YEAR` | Año calendario al que corresponde el ensayo, según la descripción del PDF. | Permite capturar cambios en clima, manejo, condiciones del ensayo o tendencias temporales. No es la edad del cultivo. Confirmar si el año corresponde a siembra, medición o cosecha antes de interpretar rezagos. |
| `STAGE` | Etapa del programa de selección; el PDF declara valores de 2 a 5. | Los resultados en etapas forman parte de la decisión de avanzar candidatos. Tratarla inicialmente como categoría, no asumir que cada incremento es una cantidad lineal de progreso o de rendimiento. La composición del grupo de clones cambia por selección; eso puede crear sesgo de supervivencia al comparar promedios entre etapas. El PDF no proporciona aquí la correspondencia exacta entre números y nombres de cada ensayo. |
| `LOC` | Código de la localidad o finca del ensayo. | El ambiente cambia el rendimiento: suelo, clima, presión de plagas y manejo pueden influir. Sirve para examinar estabilidad por ambiente. El código por sí solo no describe suelo ni clima y no equivale a localidad de Santa Ana. |
| `CROP` | Ciclo de corte: 0 = caña planta (plantada inicialmente); 1 a 4 = número de cosecha de soca, según el PDF. | Permite ver cómo cambian producción y calidad conforme el cultivo rebrota después del corte, y comparar duración productiva frente a renovación. No es el año calendario: es una posición en la vida del cultivo. Antes de calcular una vida de lote, revisar si cada variedad tiene las mismas cosechas observadas y si hay registros ausentes o truncados. |
| `REP` | Repetición del ensayo. | Los ensayos replican una variedad bajo condiciones del diseño para distinguir señal varietal de variación local o de medición. No es otra variedad ni, por sí solo, otro año. Las observaciones repetidas del mismo ensayo pueden depender entre sí; la incertidumbre y validación no deben tratarlas automáticamente como material independiente. El PDF no especifica el diseño de bloques ni la unidad experimental exacta. |

## Producción, calidad y componentes

| Columna | Qué representa | Lógica de negocio y cuidado analítico |
| --- | --- | --- |
| `TCA` | Toneladas de caña por acre (unidad reportada por USDA). | Rendimiento físico de caña. Se relaciona con volumen a cosechar y transportar; el supuesto de costo variable del PDF es US$14 por tonelada. Su unidad de masa específica debe confirmarse antes de multiplicarla por costos expresados por tonelada. |
| `TRS_TON` | Azúcar teórico recuperable por tonelada de caña: USDA indica libras de azúcar por tonelada de caña. | Indicador de concentración/calidad de azúcar recuperable de la caña; en igualdad de caña, más TRS sugiere más azúcar potencial. No es el total de azúcar por acre. Tampoco equivale necesariamente al azúcar efectivamente extraído en una fábrica real, pues esta columna describe un valor teórico. |
| `T_SPACRE` | Rendimiento de azúcar por acre. USDA describe la unidad como **libras de azúcar por acre**. | Es la medida más directa del producto valorizable con el precio referencial de US$0.20 por libra recuperable: ingreso bruto aproximado = `T_SPACRE × precio_por_libra`. El PDF la llama toneladas de azúcar por acre; adoptamos la unidad de la ficha oficial USDA y documentamos la discrepancia en el README. |
| `POPN` | Población/número de tallos, según la descripción USDA. | Componente físico del rendimiento de caña: más tallos podría elevar el tonelaje si se mantiene el peso medio. Las fuentes consultadas solo especifican `#`, no el área, longitud de surco ni factor de escala del conteo; no etiquetarlo como tallos por acre hasta verificar el diccionario detallado. |
| `MSTWT` | Peso medio del tallo; USDA indica libras. | Otro componente de la biomasa de caña. En conjunto con la población ayuda a entender si un rendimiento viene de más tallos, tallos más pesados o ambos. Verificar en el archivo si expresa libras por tallo y el método de muestreo. |
| `FIBER` | Porcentaje de fibra. | Describe composición del tallo. Puede relacionarse con extracción de jugo y cantidad de bagazo para combustión/cogeneración, pero el signo neto económico no se deduce de esta columna sola. Sin datos de extracción, humedad, vapor y electricidad no asignar un valor monetario a la fibra. Confirmar escala del porcentaje y denominador en metadatos. |

La ficha oficial de USDA define `T_SPACRE` como libras de azúcar por acre; `TRS` como libras de azúcar por tonelada de caña; `TCA` como toneladas de caña por acre; `POPN` como número de tallos; y `MSTWT` como peso medio del tallo en libras. Confirma además 32 localidades, los años 2010–2021, 1,158 genotipos, etapas 2–5 y cosechas/crops hasta 5. La comparación completa del CSV USDA con la copia Kaggle enlazada por el PDF dio archivos byte por byte idénticos. El perfil posterior encontró 10,485 celdas fuente de `TRS_TON` con dos componentes numéricos; se preserva el prefijo sin asignarle significado y se usa el componente final como valor analítico `TRS_TON`. En 29,317 de 29,340 filas positivas completas, `TCA × TRS_TON` coincide con `T_SPACRE` dentro de 1 %; 23 filas quedan para revisión. La referencia técnica general de LSU describe que los datos de cosecha permiten derivar rendimiento de caña a partir de conteo de tallos y peso; no reemplaza la validación de las unidades de este CSV.

### Investigación del prefijo de `TRS_TON`

Se revisaron el CSV y el XLSX que publica USDA, además del perfil de las 29,529 observaciones. El XLSX oficial también contiene las 10,485 celdas compuestas: el prefijo no se originó al descargar la copia de Kaggle ni durante nuestro ETL. En cada una, el prefijo tiene exactamente dos dígitos (`00`–`99`) y va seguido por un valor con tres decimales. Todas aparecen en registros de 2010–2019; no se encontraron en 2020–2021. Se concentran en diez clones y no mostraron asociación lineal relevante con `T_SPACRE`, `TCA`, el valor final de `TRS_TON`, el año, `CROP`, `REP` o `STAGE`.

La ficha pública de USDA documenta `TRS`, `TCA`, `POPN`, `MSTWT` y las repeticiones del ensayo, pero no define un campo adicional de dos dígitos en `TRS_TON`. El artículo técnico asociado explica que `REP` corresponde a las réplicas experimentales (dos en algunas etapas y tres en la etapa 5), de modo que `79` no puede tratarse como el número de repetición; además, el archivo ya tiene una columna `REP` separada. Para el ejemplo `TRS_TON_raw = "79    227.620"`, `TCA = 43.8` y `T_SPACRE = 9,977`, el componente final (`TRS_TON = 227.620`) da `43.8 × 227.620 = 9,969.756`, coherente con `T_SPACRE` dentro del 1 %. El prefijo no es necesario para esa medición.

**Conclusión y límite:** no se encontró una fuente pública que asigne significado exacto al prefijo. La evidencia es más compatible con un código auxiliar o un residuo de la estructura histórica/exportación que con una medición agronómica, pero no permite distinguir entre esas posibilidades ni llamarlo número de parcela. El ETL conserva el texto original en `TRS_TON_raw`, guarda el prefijo con su formato de texto en `TRS_TON_prefijo_sin_interpretar` (por ejemplo, `"00"`) y deja el valor numérico final en `TRS_TON`. Así el prefijo no entra inadvertidamente a métricas ni modelos y tampoco se pierde información de la fuente. Cualquier interpretación más específica requiere confirmación del responsable de los datos.

Este perfil se reproduce desde el CSV procesado después de ejecutar `scripts/etl_serie1.py`:

```python
import pandas as pd

datos = pd.read_csv(
    "data/processed/serie1_etl_provisional.csv",
    dtype={"TRS_TON_prefijo_sin_interpretar": "string"},
    low_memory=False,
)
prefijo = datos.loc[datos["TRS_TON_prefijo_sin_interpretar"].notna()]
print(prefijo.groupby("YEAR").size())
print(prefijo.groupby("CLONE").size().sort_values(ascending=False))
print(prefijo["TRS_TON_raw"].str.extract(r"^\s*(\d{2})\s+(\d+\.\d{3})\s*$").notna().all())
```

## Cómo se conectan entre sí

La relación conceptual es:

```text
rendimiento de caña (TCA)
             × azúcar recuperable por tonelada (TRS_TON)
             ≈ azúcar recuperable por acre (T_SPACRE)
```

La aproximación solo es numéricamente válida cuando las unidades de `TCA` y `TRS_TON` son compatibles. La auditoría de Serie I confirmó la relación en 29,317 de 29,340 filas positivas completas con tolerancia de 1%; `TRS_TON_raw` mantiene el texto original de las 10,485 filas con prefijo, mientras que `TRS_TON` contiene únicamente el componente numérico final. `POPN` y `MSTWT` aportan una descomposición agronómica del rendimiento de caña; no se deben sumar al azúcar producido.

El valor económico indicado en el PDF puede aproximarse así, una vez confirmadas las escalas de costo y las limitaciones del supuesto:

```text
ingreso bruto por acre = T_SPACRE (lb azúcar/acre) × US$0.20/lb
costo de cosecha y transporte por acre = TCA (ton caña/acre) × US$14/ton
contribución indicativa en caña planta = ingreso bruto − costo de cosecha/transporte
                                         − US$350 mantenimiento − US$1,100 renovación
contribución indicativa en soca = ingreso bruto − costo de cosecha/transporte
                                  − US$350 mantenimiento
```

No llamar beneficio neto completo a esa cifra: el enunciado solo aporta algunos costos referenciales. La tabla no incluye todos los costos agrícolas, financieros, fabriles ni la variación real de precio. Comparar variedades por `T_SPACRE` aislado tampoco resuelve el momento óptimo de renovar: hay que considerar el rendimiento de cada `CROP`, costos por ciclo, incertidumbre y consistencia entre ambientes.

## Alertas que conviene resolver en el primer notebook

1. Usar la unidad USDA para `T_SPACRE` (libras por acre) y mantener documentada la discrepancia del PDF. Esta decisión ya quedó respaldada por la auditoría de fuente y unidades.
2. Revisar las 23 filas positivas que difieren más de 1 % de `TCA × TRS_TON`; mantener el prefijo separado mientras no exista documentación que aclare su significado.
3. Confirmar unidad de `TCA`, escala de `POPN`, definición porcentual de `FIBER` y sentido exacto de `YEAR`.
4. Examinar las columnas sin nombre, seis notas incrustadas y puntos `.` del CSV.
5. Contar filas y nulos, detectar claves repetidas y averiguar la unidad de ensayo antes de agregar. No elegir una clave única por intuición.
6. Contar clones, localidades, etapas, años, repeticiones y ciclos por clon; medir cobertura desigual. Evitar que las variedades con más ensayos parezcan mejores solo porque tienen más observaciones.
7. Como Louisiana no es Santa Ana, formular conclusiones como candidatos/hallazgos del conjunto y explicar qué ensayo local confirmaría su transferencia.

## Fuentes

- [USDA / Data.gov: descripción, unidades y cobertura del dataset](https://catalog.data.gov/dataset/louisiana-sugarcane-yield-data-2010-2021-collected-for-the-louisiana-variety-development-p).
- [Artículo técnico del programa de desarrollo varietal de Louisiana (2025): diseño por etapas, réplicas y mediciones agronómicas](https://acsess.onlinelibrary.wiley.com/doi/10.1002/tpg2.20545).
- [LSU AgCenter: panel de avance de variedades; distingue rendimiento de azúcar, calidad TRS, caña, ciclo y localidad, y documenta datos modelados y fiabilidad de ensayos](https://www.lsuagcenter.com/topics/crops/sugarcane/blanchard-sugarcane-lab/variety-advancement-dashboard).
- [LSU AgCenter: actividades del programa por año, con ejemplos de etapas de selección](https://www.lsuagcenter.com/~/media/system/4/8/1/d/481d121dd5056e4db20afb50b8d8750a/03%20variety%20section%202023pdf.pdf).
- [PDF de la prueba](../Prueba%20de%20conocimientos%20t%C3%A9cnicos%20Cient%C3%ADfico%20de%20Datos.pdf), páginas 2–3.
