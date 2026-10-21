# Serie II: resultados de interacciones físicas

## Resultado

Las tres interacciones examinadas no aportan una mejora suficientemente consistente para incorporarlas al modelo seleccionado. La campeona es Ridge de diecisiete entradas, descrita en el [informe de rezagos](rezagos-serie-II.md). El [notebook 08](../notebooks/08_experimento_features_serie2.ipynb) contiene las comparaciones de interacciones sobre una referencia de quince señales actuales.

| Interacción | Fórmula | Resultado frente a su referencia |
|---|---|---|
| Aire y oxígeno | z(FT_8302) × z((AIR_8301A+AIR_8301B)/2) | Empeora el MAE medio aproximadamente 0.275 %. |
| Asimetría de oxígeno | abs(AIR_8301A−AIR_8301B) | Empeora el promedio aproximadamente 0.058 %. |
| Agua y temperatura | z(YJJWSLL) × z(TE_8332A) | Mejora el promedio apenas 0.141 %, con empeoramiento en una ventana. |

## Método e interpretación

Comparo la referencia, cada interacción y los controles con sus sensores soporte, usando las mismas tres ventanas temporales. Aprendo los parámetros de imputación, normalización y selección solo en entrenamiento. El quinto día no interviene en este experimento.

Los productos y valores absolutos amplían las relaciones que puede representar Ridge. El aire y el oxígeno describen conjuntamente condiciones de combustión; la diferencia entre lados puede representar asimetría; agua y temperatura describen condiciones de atemperación. Sus asociaciones no son medidas de eficiencia ni efectos causales de manipular la caldera.

La pequeña mejora de agua×temperatura no es estable entre ventanas y no justifica añadirla al modelo. Faltan condiciones del combustible, instrumentación y control para atribuir un mecanismo físico concreto. La importancia condicional de una señal tampoco equivale a su relevancia física.

## Evidencia

Resultados y controles en outputs/experimento_features/. El notebook reproduce métricas y predicciones y declara sus límites de validación histórica. El experimento no simula ahorros ni cambios de consignas.
