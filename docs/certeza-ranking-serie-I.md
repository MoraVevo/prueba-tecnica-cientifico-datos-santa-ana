# Certeza del ranking económico de variedades

## Conclusión gerencial

Mantendría HoCP14-885 y L01-299 entre las variedades prioritarias para evaluación local. La posición de HoCP14-885 es alta cuando cumple la cobertura, pero su recomendación tiene menor respaldo: en el bootstrap solo volvió a ser elegible en 202 de 500 réplicas (40.4 %), porque su cobertura del corte necesario descansa en dos años. No debe leerse su ausencia como bajo aporte; cuando fue elegible, ocupó el primer lugar en las 202 réplicas.

Con el ajuste ambiental, conservaría Ho12-615 como tercera candidata condicionada y añadiría HOCP09-804 como candidata adicional para ensayos, en particular como relevo cuando HoCP14-885 no alcance cobertura. HOCP09-804 fue elegible en 499 de 500 réplicas y quedó top 3 en 271 (54.2 % de todas; 54.3 % cuando fue elegible), con rango mediano 3. Cuando HoCP14-885 no fue elegible, HOCP09-804 sí lo fue en 297 de 298 réplicas y entró al top 3 en 264 de esas (88.9 %). Cuando ambas fueron elegibles, HOCP09-804 estuvo en el top 3 solo en 7 de 202 réplicas (3.5 %), normalmente por debajo de HoCP14-885.

HOCP09-804 supera a L01-283 en esta estabilidad del top 3: 54.2 % frente a 16.4 % global, con aportes medianos de US$598.63 y US$580.31 por acre/año, respectivamente. Sus rangos P05–P95 de aporte se solapan (US$548–662 frente a US$522–632), así que la ventaja no establece una separación concluyente de desempeño. La cobertura de HOCP09-804 es más amplia en CROP 0–3 (9, 8, 7 y 6 años; 15, 14, 14 y 12 localidades) y se detiene después porque CROP 4 aparece en una sola localidad. Esta evidencia justifica probarlo como cuarta opción y relevo contingente; no demuestra que sustituya de forma general a HoCP14-885 o Ho12-615.

A US$0.20/lb, Ho12-615 quedó en el top 3 en 419 de 500 réplicas (83.8 % de todas; 95.7 % cuando fue elegible). L01-283 apareció en el top 3 en 82 de 500 (16.4 %), aunque fue elegible en 499. Sin el ajuste ambiental, la frecuencia de top 3 cae a 37.4 % para Ho12-615 y sube a 43.0 % para L01-283. La elección de tercera variedad depende de cómo se ajuste por ambiente, por lo que la evidencia no justifica una asignación amplia o irreversible.

El ranking base del notebook estima aportes parciales anuales de US$727.58 para HoCP14-885, US$632.66 para L01-299 y US$629.21 para Ho12-615. En las remuestras ajustadas a US$0.20, las medianas del aporte de la política que cada variedad vuelve a elegir fueron US$725, US$632 y US$619 por acre/año, respectivamente. Los percentiles 5–95 de esas políticas elegidas fueron US$666–789, US$569–691 y US$569–676. Se solapan entre L01-299 y Ho12-615; describen variación de los años observados bajo este cálculo, no intervalos de confianza de rentabilidad real.

Al mover el precio supuesto de US$0.15 a US$0.25 por libra, la mediana del aporte de HoCP14-885 pasó de US$249 a US$1,202 por acre/año; L01-299, de US$208 a US$1,056; y Ho12-615, de US$193 a US$1,051. En los tres escenarios HoCP14-885 ocupó el primer lugar cuando fue elegible y L01-299 permaneció en el top 3 en 98.8–100 % de las réplicas. La frecuencia total de Ho12-615 en el top 3 subió de 66.6 % a US$0.15 a 85.8 % a US$0.25; L01-283 bajó de 28.6 % a 13.2 %. HOCP09-804 estuvo en el top 3 en 54.2 % a US$0.20, con aporte mediano de US$598.63 y política modal de cuatro cosechas (98.6 %). Los escenarios cambian mucho el valor económico y refuerzan relativamente a Ho12-615 en el extremo de precio alto, sin incorporar probabilidades de precio.

La sensibilidad que incluye las cuatro observaciones completas marcadas para revisión no cambia el resumen de los cuatro candidatos a la precisión presentada. Conservo la marca y la trato aparte; no elimino el dato crudo.

## Método

Analicé las 14,092 filas `STAGE=5` de `serie1_etl_provisional.csv`, delimitación de campo usada por el notebook 03. De ellas, 14,033 tenían `T_SPACRE` y `TCA` completos. Excluí del escenario principal cuatro filas completas con `REQUIERE_REVISION=True`, y 59 filas sin alguna de esas dos mediciones; el escenario principal contiene 14,029 filas. Aparté las 15,311 filas de otras etapas porque el cálculo económico vigente se limita a `STAGE=5`. Las conservé todas en una salida con motivo por fila y con los flags originales. Además, 511 celdas variedad/corte/año/localidad sin L01-299 en el mismo ambiente no entran al contraste ajustado; las guardo aparte con la razón.

Interpreto el azúcar por acre en lb/acre: `TCA` (ton/acre) por `TRS_TON` (lb/ton) reproduce `T_SPACRE` en la escala del dato. Agrego las filas primero por variedad, corte, año y localidad. El ajuste sustrae el resultado de L01-299 en cada ambiente compartido y añade la media del referente por corte, como hace el notebook 03. No supongo independencia entre repeticiones de un mismo ensayo.

Fijé el año completo como unidad de remuestreo. Cada una de las 500 réplicas sorteó con reemplazo 12 de los 12 años observados, conservando juntas todas sus localidades, variedades, cortes, etapas y repeticiones. Una repetición de un mismo año recibe peso repetido en las medias, pero no cuenta como segundo año distinto para elegibilidad. En cada remuestra vuelvo a estimar los contrastes ambientales, la media de referencia, la cobertura de todas las variedades y cortes, la mejor duración por variedad y el ranking completo. No restringí el universo a las variedades del ranking original.

Exijo que CROP 0, 1 y 2 sean consecutivos y tengan cada uno al menos dos años fuente distintos y dos localidades. Admito los cortes posteriores solo hasta el primer corte que no cumple la regla. Comparo el ajuste ambiental con promedios directos a US$0.20/lb; también evalúo filas marcadas incluidas a ese precio. Recalculo los precios US$0.15, US$0.20 y US$0.25/lb en el ranking ajustado.

La fórmula que aplico es:

`aporte parcial anual (US$/acre/año) = [precio (US$/lb) × azúcar esperado (lb/acre) − 14 (US$/ton) × caña esperada (ton/acre) − 350 (US$/acre/año) × cosechas − 1,100 (US$/acre de renovación)] / cosechas`.

Asumo una cosecha anual y una renovación al iniciar la rotación, sin descuento, año de descanso ni otros costos. No representa utilidad neta completa.

## Certeza, límites y decisión

En las 500 réplicas hubo al menos tres variedades elegibles, así que ordeno el ranking en todos los casos. La frecuencia «sobre todas las réplicas» cuenta ausencia/no elegibilidad como falta de selección top 3, nunca como aporte cero. La frecuencia condicional divide las apariciones en top 3 por el número de réplicas donde la variedad sí fue elegible. Calculo los percentiles de aporte y rango solo cuando aparece elegible.

El resultado es condicional al archivo y al procedimiento de ajuste, con apenas doce conglomerados anuales. El remuestreo refleja sensibilidad a qué años observados entran, pero no estima la probabilidad de superioridad en futuras zafras, no resuelve dependencia temporal entre años y no corrige la selección histórica de localidades o variedades. El ajuste depende de ambientes compartidos con L01-299. La ausencia de cohortes y parcelas persistentes impide leer los cortes como rotaciones observadas o atribuir diferencias al envejecimiento. Tampoco hay datos de Santa Ana para trasladar directamente los valores.

Recomiendo usar HoCP14-885, L01-299 y Ho12-615 como candidatas de evaluación, y añadir L01-283 como comparación directa para resolver la tercera posición. Antes de ampliar superficie, mediría las cuatro en ambientes de Santa Ana y seguiría las mismas parcelas desde plantía, registrando renovación, causas de retiro, rendimiento y costos reales. La decisión depende del precio esperado y los costos locales; los escenarios de precio muestran sensibilidad material del aporte parcial.

## Reproducción

Desde la raíz del proyecto, ejecutar:

```powershell
.venv\Scripts\python.exe scripts\evaluar_ranking_serie1.py
.venv\Scripts\jupyter.exe nbconvert --to notebook --execute --inplace notebooks\21_certeza_ranking_serie1.ipynb
.venv\Scripts\python.exe -m pytest tests\unitarias\test_ranking_serie1.py tests\integracion\test_ranking_serie1_resultados.py -q
```

El script usa semilla `20261020`, 500 réplicas y escribe resultados auditables en `outputs/serie1_ranking/`, carpeta ignorada por Git. La tabla completa por réplica conserva elegibilidad, cobertura, política y rango; los archivos de exclusiones y ambientes sin referencia permiten revisar los apartados. Las pruebas específicas reconstruyen la fórmula base y tres rankings remuestreados mediante expansión literal de cada conglomerado sorteado, además de verificar conservación de flags, unidades y exclusiones.
