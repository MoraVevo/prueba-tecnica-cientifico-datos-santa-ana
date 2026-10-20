# Propuesta de features físicas para Serie II

Fecha: 2026-10-20. **Diseño previo del experimento.** El usuario pidió inicialmente pensar relaciones/interacciones sencillas y después autorizó probarlas. La ejecución y las conclusiones están en [notebook 08](../notebooks/08_experimento_features_serie2.ipynb). Las secciones siguientes conservan las hipótesis antes de evaluarlas; no son resultados. Ridge/Reducida 15 continúa como campeona; todas las variables originales y comparaciones permanecen disponibles.

Resultado posterior: aire × oxígeno y asimetría empeoran el MAE medio; agua × temperatura lo reduce apenas 0.141 %, de forma desigual por día. La regla de parsimonia vigente mantiene la base de quince. Experimento aislado y conservado como evidencia, sin promoción ni uso del quinto día. Ver tablas y limitaciones en el notebook.

## Idea y evidencia disponible

Ridge representa una suma de contribuciones lineales. Si recibe A y B, ya puede representar A−B o su promedio. Añadir esas combinaciones lineales cambia la parametrización y la penalización, pero no amplía las relaciones representables. Productos, valores absolutos o curvas sí pueden ampliar esa capacidad. [Documentación de transformaciones polinómicas de scikit-learn](https://scikit-learn.org/1.6/modules/preprocessing.html#generating-polynomial-features).

La cadena económica propuesta por el usuario incluye mecanismos temporales. El alcance vigente del sensor virtual usa señales contemporáneas, sin memoria: las candidatas siguientes representan estados e interacciones instantáneas. No reconstruyen una cadena causal con retardos ni sustituyen el estudio temporal pendiente.

Se revisaron el diccionario, el documento físico y los coeficientes existentes. Las dos presiones PTCA tienen los mayores coeficientes estandarizados y signos opuestos; el contraste ya está representado por Ridge. Los dos sensores de oxígeno tienen coeficientes menores y opuestos. Eso sugiere examinar su contribución conjunta, sin demostrar importancia física o causal. La colinealidad, la regularización y el rango observado también condicionan los coeficientes. Los coeficientes finales son un diagnóstico ya observado, no evidencia independiente de mejora de nuevas features.

Solo se inspeccionaron rangos de las señales en el primer entrenamiento temporal para comprobar que las hipótesis se apoyan en columnas existentes. No se calcularon errores de modelos nuevos ni se utilizó la comprobación final para decidir fórmulas.

## Tres candidatas, con prioridad

En las fórmulas se omite el sufijo `.AV_0#`. `z(x)` significa centrar por la media y dividir por la desviación del entrenamiento correspondiente. Imputación/normalización se aprenderían dentro de cada entrenamiento; también se estandarizarían las columnas derivadas antes de Ridge para que su penalización no dependa arbitrariamente de la escala.

### 1. Interacción entre aire secundario y oxígeno medio

```text
O_medio = (AIR_8301A + AIR_8301B) / 2
aire_x_oxigeno = z(FT_8302) * z(O_medio)
```

**Hipótesis física:** el caudal de aire y el oxígeno residual informan conjuntamente sobre la combustión. Aire insuficiente puede limitar la combustión; demasiado aire puede aumentar pérdidas con los gases. La documentación DOE respalda ese mecanismo general, sin aportar un óptimo aplicable directamente a esta caldera. [DOE: eficiencia de combustión](https://www.energy.gov/sites/prod/files/2014/05/f16/steam4_boiler_efficiency.pdf).

**Qué aportaría a Ridge:** permitir que la asociación del aire secundario con el vapor cambie según el estado del oxígeno. Con un término `b*F + c*O + d*F*O`, la pendiente respecto de F depende de O. El modelo aprende el signo y magnitud; no imponemos que más aire siempre produzca más vapor.

**Por qué priorizarla:** los tres tags ya están entre los quince del ajuste final y FT_8302 tiene un coeficiente estandarizado pequeño. Permite probar si esa asociación está incompletamente representada por un efecto lineal constante. No requiere nuevos sensores en ese ajuste.

**Límite:** falta flujo/composición del combustible, calibración de oxígeno y configuración de control. Esta feature no mide relación aire/combustible ni eficiencia y no prueba causalidad. El promedio solo es una síntesis numérica de ambos tags.

### 2. Magnitud de la asimetría entre los dos oxígenos

```text
asimetria_oxigeno = abs(AIR_8301A - AIR_8301B)
```

**Hipótesis:** un promedio parecido puede ocultar distribuciones distintas entre lados. La magnitud del contraste podría aportar información sobre heterogeneidad del estado de combustión y su asociación con el vapor.

**Qué aportaría a Ridge:** representar un efecto que dependa del tamaño de la diferencia, sea A mayor que B o B mayor que A. La resta firmada ya es representable por el modelo; su valor absoluto añade una forma distinta. Los signos opuestos de los coeficientes actuales motivan revisar esta familia, pero no prueban que la magnitud absoluta sea útil.

**Límite:** es una hipótesis de esta propuesta, no una relación validada por el dataset o una regla operativa. La comparabilidad de escala/calibración de los dos tags es un supuesto. El contraste también puede reflejar sesgo instrumental; no se etiquetará como desequilibrio de combustión confirmado.

### 3. Interacción entre agua de atemperación y temperatura del vapor

```text
agua_x_temperatura = z(YJJWSLL) * z(TE_8332A)
```

**Hipótesis física:** el agua de atemperación y el estado térmico del vapor describen conjuntamente el enfriamiento/control. En atemperación por contacto, el agua absorbe calor al evaporarse; su necesidad depende del estado del vapor. [Spirax Sarco: teoría de atemperación](https://www.spiraxsarco.com/learn-about-steam/desuperheating/basic-desuperheating-theory?sc_lang=en-GB).

**Qué aportaría a Ridge:** permitir que la asociación del caudal de agua con el vapor principal cambie con la temperatura. Puede describir un estado de operación/control que una suma de efectos constantes represente peor.

**Por qué conservarla como segunda etapa:** TE_8332A quedó fuera de las quince finales, pero sigue disponible entre las 29. No estar seleccionada no demuestra irrelevancia para una interacción. Esta candidata incorpora información de un tag adicional al conjunto final de quince, aunque solo se agregue una columna derivada: hay que contar ambas cosas por separado.

**Límite:** TE_8332A es temperatura global de salida, sin confirmación de que sea la temperatura local del atemperador primario. No tenemos temperatura antes/después de ese equipo, temperatura del agua, consigna ni entalpías. El producto no representa un balance de energía, no estima calor absorbido ni demuestra que la inyección aumente el objetivo medido. El control en lazo cerrado también puede producir asociaciones que no corresponden a efectos de manipular agua.

## Ideas que no priorizaría

- Añadir solo `PTCA_8322A−PTCA_8324`: ambas ya tienen coeficientes grandes y opuestos; se conservaría como explicación del modelo, sin afirmar capacidad nueva.
- Aplicar una raíz a ese contraste invocando una ecuación de caudal: no está confirmado que sean las tomas de un elemento de medición de flujo. La teoría de instrumentación no identifica los tags de este equipo. [Spirax Sarco: instrumentación](https://www.spiraxsarco.com/learn-about-steam/flowmetering/instrumentation).
- Cocientes válvula/agua, eficiencia, densidad o exceso de aire con unidades asumidas. Falta la información para darles esa interpretación física.
- Combinar todas las columnas entre sí. La primera prueba propuesta es una sola interacción: aire × oxígeno. Las otras dos quedan como siguientes hipótesis, sin búsqueda masiva.

## Cómo distinguir un futuro experimento

Si el usuario pide implementarlo, usar un notebook experimental separado, manteniendo el notebook 07 y su artefacto campeón intactos. Comparar primero la base de quince con esa misma base más una candidata por vez, en las mismas ventanas y separación temporal. La selección de las quince se repetiría dentro de cada entrenamiento, como ahora; no se congelaría retrospectivamente la lista aprendida en desarrollo para evaluar días anteriores. La transformación derivada podría consultar otras señales crudas cuando la hipótesis lo requiera, declarando cuántos sensores usa.

No fijar la mejora por un coeficiente grande. Comparar errores por ventana, peor ventana, sesgo, estabilidad y costo de sensores; una ganancia en el promedio que empeore sensiblemente otra ventana necesita una decisión explícita. El día final ya reutilizado no servirá para aceptar fórmulas. La iteración sobre las validaciones también limita la independencia de la evidencia; una confirmación nueva requiere otro periodo.

No hay implementación, fórmula ganadora, reducción de error, cambio de campeón ni autorización para publicar en esta propuesta. Si se descarta el experimento, podrá retirarse su implementación diferenciada conservando en la bitácora la hipótesis y razón del descarte, como pide el enunciado.
