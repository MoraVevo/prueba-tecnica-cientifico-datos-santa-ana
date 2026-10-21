# Serie III: fuentes de precios y producción

## Archivo obtenido

El PDF pide Agricultural Commodities Futures, de `guillemservera/agricultural-futures`. El archivo se encuentra dentro de `individual_data/Sugar_data.csv` en el [dataset indicado](https://www.kaggle.com/datasets/guillemservera/agricultural-futures), no en la raíz del paquete. Se descargó desde la API pública de Kaggle sin credenciales.

- Ruta local: `data/raw/serie3/Sugar_data.csv`.
- Tamaño: 536,051 bytes, coincidente con el inventario público.
- SHA-256: `944471f40adce9a236bc992e3824f8c07f8f87b0f1aa7a5e50c47c888dcd52d1`.
- Registros: 6,097; fechas desde 2000-03-01 hasta 2024-06-24.
- Columnas originales: `date`, `open`, `high`, `low`, `close`, `volume`.
- Fechas ordenadas, cero fechas repetidas y cero celdas ausentes.
- 93 filas tienen volumen cero. En 11 filas no se cumple que high/low contengan todos los otros precios OHLC. Son aspectos para investigar, no exclusiones justificadas todavía.

Se conserva el CSV íntegro, sin cambiar encabezados ni retirar observaciones. La procedencia y revisión estructural quedan en `data/raw/serie3/fuente_sugar.json`, ignorados por Git. Los metadatos de la versión 188 declaran Yahoo Finance como origen. El [notebook 15](../notebooks/15_precios_azucar_serie3.ipynb) y las [conclusiones del inciso 2](conclusiones-serie-III.md#2-volatilidad-regímenes-y-extremos-del-azúcar-no-11) analizan volatilidad, estados y extremos, con las [fuentes registradas](fuentes-precios/indice.md). La verificación de continuidad es parcial: faltan reglas e identificadores de contratos, ajustes y definición de cierre/liquidación; no se atribuyen automáticamente todos los saltos a movimientos reales del mismo contrato.

Para reproducir desde la raíz:

```powershell
python scripts/descargar_azucar_serie3.py
```

El descargador contrasta nombre y tamaño con el inventario y evita sobrescribir una versión local distinta. No modifica el EDA existente.

## Fuente de producción

FAOSTAT aporta área cosechada, rendimiento y producción de caña. La fuente local contiene 1961–2024; el ámbito del ejercicio es 1961–2023. Sus unidades son ha, kg/ha y toneladas. La vista analítica reúne 112 países/territorios, con datos y flags conservados.

El [notebook de FAOSTAT](../notebooks/13_eda_faostat_serie3.ipynb) desarrolla cobertura, comparabilidad geográfica, calidad, consistencia aritmética y Guatemala. La [respuesta centralizada](respuestas-prueba.md) reúne los resultados de todas las series.
