# Combustión a carga semejante: contraste descriptivo

## Hallazgo

Bajo el criterio principal que fijé antes de calcular las diferencias, **no se formaron parejas de aire secundario alto y bajo con carga suficientemente comparable**. El filtro exige bloques de cinco minutos con rango intrabloque ≤1.0 en vapor y presión, y diferencias de carga ≤0.20 desviaciones estándar por variable y ≤0.30 en conjunto. De 1,440 bloques, 65 cumplieron estabilidad y cobertura; 46 de ellos no tuvieron pareja y 19 correspondieron al tercil medio. El resultado principal es, por tanto, **cero pares y ningún contraste de O2 o gases bajo ese estándar**.

Al relajar el filtro de estabilidad a rango ≤2.0, la sensibilidad predefinida con caliper 0.20 formó **46 pares en seis fechas de calendario** (cinco jornadas de 24 horas). Las diferencias medianas alto menos bajo fueron +0.285 y +0.350 para O2 A/B, y +2.365 y +2.395 para las temperaturas de gases A/B, en las unidades originales. Los rangos intercuartílicos cruzan cero y los signos no se repiten en todas las fechas. **No se sostiene una diferencia persistente de combustión, exceso de aire, ajuste óptimo ni ahorro.** La comparación sí delimita qué mediciones faltan para una prueba operativa.

## Evaluación gerencial

**Significado.** El archivo no permite afirmar que exista una ineficiencia corregible de aire en un periodo concreto. La ausencia de parejas bajo el criterio principal no demuestra que la caldera opere bien o mal: demuestra que, con las señales y la estabilidad observadas, no hay un contraste suficientemente limpio. Las sensibilidades más amplias mezclan condiciones de carga y fechas; sirven para explorar, no para decidir un ajuste.

**Decisión recomendada.** Recomiendo mantener la revisión de coordinación térmica/atemperación como primera prioridad y, si se decide estudiar el reparto de aire, diseñar una prueba supervisada. Antes de mover consignas, confirmaría ubicación, unidades, escala y calibración de `FT_8302`, `AIR_8301A/B`, `TE_8319A/B`, `ZZQBCHLL` y `PTCA_8324`; registraría carga, combustible y poder calorífico, CO e inquemados, temperatura real de chimenea y energía eléctrica. La comparación de este archivo no autoriza reducir aire ni fijar un oxígeno objetivo.

**Impacto medido.** No cuantifico ahorro de combustible, kWh ni dinero. El beneficio actual es acotar la oportunidad y especificar el experimento que permitiría valorarla. La diferencia de exposición de aire secundario en la sensibilidad fue sustancial —mediana de 2,113.96 unidades originales—, pero las respuestas de O2 y gases no mostraron un patrón consistente que permita atribuirle una mejora.

**Riesgo y certeza.** Certeza alta de que el criterio principal no produce parejas y de que la conservación de filas es completa. Certeza baja para generalizar la sensibilidad: solo hay seis fechas, los pares no son independientes, las unidades no están confirmadas y la carga se aproxima con dos señales. La certeza física del mecanismo general —aire suficiente para combustionar y exceso de gases como pérdida— es alta, pero no identifica una falla ni un beneficio en esta caldera.

## Diseño y método

La unidad es un bloque fijo no solapado de cinco minutos, anclado al primer timestamp del archivo. Resumo cada señal con la mediana de sus lecturas; exijo al menos 55 de 60 lecturas por señal y no imputo. Conservo las 86,400 filas originales y asigno cada fila a un bloque con su motivo.

La carga se representa con la mediana de `ZZQBCHLL` (caudal principal de vapor compensado) y `PTCA_8324` (presión de salida). Los nombres y escalas físicas no están confirmados. El filtro principal retiene bloques con rango intrabloque ≤1.0 en cada señal; evalúo 0.5 y 2.0 como sensibilidades. Es un criterio descriptivo de estabilidad, no un límite de ingeniería.

La exposición es `FT_8302`, caudal de salida del ventilador secundario. Dentro de cada día marco los terciles inferior y superior; el tercil medio no entra al contraste primario. El emparejamiento es 1:1 sin reemplazo, dentro del mismo día, entre bloques de exposición alta y baja. Estimo la escala de carga con la desviación estándar de todos los bloques elegibles del día, incluido el tercil medio, como fijé en el diseño previo. Exijo diferencia ≤0.20 desviaciones estándar en vapor y presión, y distancia euclídea conjunta ≤0.30. La matriz de sensibilidad combina rangos 0.5/1.0/2.0 y calipers 0.15/0.20/0.25, manteniendo 0.30 en la distancia conjunta.

Los resultados primarios son `AIR_8301A`, `AIR_8301B`, `TE_8319A` y `TE_8319B`; reporto `FT_8306A/B` y las diferencias A−B como contexto. No uso O2 ni gases para definir la exposición. Las diferencias son alto menos bajo; las resumo por mediana y rango intercuartílico por fecha y en el total de pares. No calculo p-valores ni trato los pares como réplicas independientes.

## Resultados

La matriz completa muestra que el soporte aparece solo al relajar la estabilidad:

| Rango máximo | Caliper por variable | Bloques elegibles | Pares | Bloques pareados | Filas fuente en pares |
|---:|---:|---:|---:|---:|---:|
| 0.5 | 0.15 / 0.20 / 0.25 | 0 | 0 | 0 | 0 |
| 1.0 | 0.15 | 65 | 0 | 0 | 0 |
| 1.0 | 0.20 (principal) | 65 | 0 | 0 | 0 |
| 1.0 | 0.25 | 65 | 2 | 4 | 240 |
| 2.0 | 0.15 | 1,016 | 36 | 72 | 4,320 |
| 2.0 | 0.20 (sensibilidad) | 1,016 | 46 | 92 | 5,520 |
| 2.0 | 0.25 | 1,016 | 59 | 118 | 7,080 |

En la sensibilidad de rango ≤2.0 y caliper 0.20, el emparejamiento redujo las diferencias de carga: antes, la diferencia estandarizada máxima era 1.96 en vapor y 0.57 en presión; después, 0.091 y 0.078, respectivamente. La exposición de aire secundario conservó una diferencia mediana de 2,113.96 unidades originales (Q1–Q3: 1,844.40–2,505.55).

| Resultado, 46 pares | Mediana alto − bajo | Q1 | Q3 |
|---|---:|---:|---:|
| O2 lado A | +0.285 | −0.041 | +0.536 |
| O2 lado B | +0.350 | −0.055 | +0.640 |
| Gases A | +2.365 | −0.795 | +5.870 |
| Gases B | +2.395 | −1.154 | +10.779 |
| Aire de retorno A | 0.000 | −5.544 | +5.924 |
| Aire de retorno B | −1.515 | −5.064 | +3.868 |
| Asimetría O2 A−B | −0.080 | −0.130 | +0.044 |
| Asimetría gases A−B | −2.168 | −5.463 | +1.171 |

Todas las magnitudes están en las unidades originales, sin calibración confirmada. Los signos de O2 A/B y gases A son positivos en cuatro de las seis fechas; gases B, en cinco. Sin embargo, las fechas 27 y 28 de marzo concentran signos negativos y la dispersión por fecha es amplia. Al ampliar el caliper a 0.25, con 59 pares, las medianas fueron +0.23/+0.33 para O2 y +0.99/+1.85 para gases; la lectura no cambia. Los dos únicos pares del rango 1.0 con caliper 0.25 no alcanzan para un contraste por fecha.

## Conservación y límites

Conservo las 86,400 filas y los 1,440 bloques. En el escenario principal, las 86,400 filas quedan fuera del contraste con motivo: 1,375 bloques inestables en vapor o presión, 46 bloques elegibles sin pareja y 19 del tercil medio. En la sensibilidad de 46 pares, 5,520 filas están en bloques pareados y 80,880 quedan en `filas_fuera_contraste.csv` con sus campos crudos, IDs y motivos. No elimino ni imputo ninguna lectura.

La interpretación está limitada por:

- **Unidades y calibración:** no confirmo la unidad física de `ZZQBCHLL` ni de `PTCA_8324`; tampoco certifico la escala de O2 ni la base de `AIR_8301A/B`; `TE_8319A/B` corresponden a puntos del economizador, no necesariamente a la temperatura final de chimenea. `FT_8306A/B` es aire de cámaras de retorno, no condensado.
- **Cobertura temporal:** cinco jornadas de operación en 2022, que abarcan seis fechas de calendario. No representan estados estacionales, combustibles o cargas distintas.
- **Dependencia:** los 46 pares comparten días, historia y señales; no son observaciones independientes. Los rangos intercuartílicos describen dispersión entre pares, no intervalos de confianza.
- **Carga aproximada:** vapor y presión son proxies; no dispongo de flujo de combustible, poder calorífico, CO, inquemados, temperatura de chimenea ni energía eléctrica. Sin esos datos no calculo eficiencia, exceso de aire ni ahorro.
- **Selección:** fijé el criterio principal antes de ver O2/gases; las sensibilidades también estaban predefinidas. Aun así, la matriz es exploratoria y no sustituye una prueba prospectiva.

## Reproducción

Desde la raíz del proyecto:

```powershell
.venv\Scripts\python.exe scripts\comparar_carga_serie2.py
.venv\Scripts\jupyter.exe nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=600 notebooks\22_combustion_carga_serie2.ipynb
.venv\Scripts\python.exe -m pytest tests\unitarias\test_carga_serie2.py tests\integracion\test_carga_serie2_resultados.py -q
```

El [notebook 22](../notebooks/22_combustion_carga_serie2.ipynb) ejecuta el contraste principal, recorre la matriz de nueve escenarios y genera las figuras. El módulo [comparar_carga_serie2.py](../scripts/comparar_carga_serie2.py) reproduce el escenario principal y las tablas de auditoría. Los resultados quedan en `outputs/serie2_carga/`, incluida `matriz_final/`, y permanecen fuera de Git. Las pruebas reconstruyen la mediana de cada bloque desde las filas fuente, verifican los calipers con la escala de todos los bloques elegibles y comprueban que las filas fuera del contraste conservan sus valores crudos.
