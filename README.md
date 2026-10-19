# Prueba técnica de Científico de Datos — Ingenio Santa Ana

## Decisión de fuente y unidad: Serie I

El PDF describe `T_SPACRE` como toneladas de azúcar por acre, pero la [ficha oficial USDA-ARS](https://catalog.data.gov/dataset/louisiana-sugarcane-yield-data-2010-2021-collected-for-the-louisiana-variety-development-p) la define como **libras de azúcar por acre**. Se utiliza la definición USDA para que el precio de US$0.20/lb del ejercicio sea compatible. `TCA` está en ton de caña/acre y `TRS_TON` en lb de azúcar/ton de caña.

El CSV oficial y la copia Kaggle del enunciado se verificaron como idénticos. El descargador comprueba su SHA-256. En `TRS_TON` hay valores con prefijo sin definición: el ETL conserva el texto y prefijo aparte y utiliza el componente numérico final, coherente con `TCA × TRS_TON ≈ T_SPACRE`. No se utiliza el prefijo como variable agronómica.

## Serie I: cuatro respuestas

Se presenta un **primer borrador completo, pendiente de revisión independiente de cálculos y supuestos**. Las limitaciones se incorporan a la certeza de las conclusiones. Se utiliza el dataset entregado y escenarios económicos explícitos; no se requieren datos externos adicionales para resolver esta serie.

| Pregunta | Respuesta del borrador | Evidencia |
| --- | --- | --- |
| Variedades y renovación | HoCP14-885: tres cosechas; L01-299 y Ho12-615: cuatro. Aportes anuales esperados aproximados de US$728, US$633 y US$629/acre al precio del PDF. Tercer puesto sensible frente a L01-283. | Notebook 03 |
| Modelo supervisado | Ridge, árbol y bosque; selección por validación temporal 2019–2020 y evaluación reservada 2021. Ridge elegido: MAE 2,145 lb/acre, R² 0.25; utilidad moderada y errores visibles. | Notebook 04 |
| Segmentación | Dos perfiles sobre productividad, TRS, conservación en soca y estabilidad; 17 variedades segmentadas y restantes con razón de cobertura insuficiente. | Notebook 05 |
| Datos y ensayos propios | Seguimiento de parcela/cohorte, mediciones y costos; variedades aleatorizadas por bloques/sitios y seguimiento de socas; fase para contrastar políticas de renovación. | Documento de conclusiones |

El detalle de recomendaciones, certeza, impacto y riesgos está en [conclusiones de Serie I](docs/conclusiones-serie-I.md). Tres cosechas significan plantía + dos socas; cuatro significan plantía + tres socas.

## Reproducción

Entorno preparado con Python 3.13.14. En Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/descargar_serie1.py
python scripts/etl_serie1.py
jupyter lab
```

Ejecutar los notebooks en orden:

1. `01_revision_fuente_y_unidades.ipynb`: procedencia y unidades.
2. `02_perfil_eda_inicial_serie1.ipynb`: calidad, repetidos y cobertura.
3. `03_analisis_economico_serie1.ipynb`: aporte, políticas de renovación, precio y certeza.
4. `04_modelo_supervisado_serie1.ipynb`: tres algoritmos, referencias, evaluación temporal y ejemplo de siguiente zafra.
5. `05_segmentacion_variedades_serie1.ipynb`: variables por clon, elección de segmentos y lectura gerencial.

También se pueden ejecutar sin interfaz, por ejemplo:

```powershell
python -m nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=600 notebooks/04_modelo_supervisado_serie1.ipynb
```

El ETL guarda 29,403 filas analíticas y separa 126 copias exactas adicionales, con motivo por fila. Mantiene 224 registros de claves repetidas con mediciones distintas y 23 alertas dimensionales. Cada análisis conserva sus exclusiones, motivos y salidas en `data/processed/`. Las alertas se tratan mediante escenarios y no se corrige una medición arbitrariamente. La fuente permanece intacta.

## Supuestos y límites que afectan la decisión

- Se adopta la tonelada de `TCA` como unidad del costo US$14/ton del ejercicio. La revisión independiente comprobará la compatibilidad y todas las fórmulas.
- La rotación supone una cosecha anual, renovación inmediata, costos constantes y sin descuento ni descanso. Se comparan aportes **esperados**, no flujos observados de la misma parcela.
- Los precios de US$0.15, 0.20 y 0.25/lb son escenarios ilustrativos de ±25 %; no son una distribución de mercado estimada.
- La recomendación exige cobertura temporal/geográfica por corte y muestra duraciones adicionales de menor certeza. El escenario sin ajuste ambiental cambia el tercer puesto.
- El modelo usa entradas disponibles antes de la zafra y medias de años anteriores. La precisión observada es limitada; MAE no es un intervalo de confianza.
- Se preservan listas de variedades sin cobertura suficiente para economía/segmentación. Los faltantes extensos de fibra no se imputan para obligar a usarla.

## Archivos y entrega

`notebooks/` contiene evidencia reproducible; `scripts/` contiene descarga y ETL; `docs/` contiene conclusiones y continuidad; `bitacora.md` registra decisiones e hipótesis corregidas. `requirements.txt` fija dependencias. `data/raw/` y `data/processed/`, el PDF confidencial y entornos locales están excluidos de Git. El ZIP final debe excluir datasets e incluir `.git`, según el PDF.

## Pendientes

Revisar de manera independiente cálculos económicos, agregaciones, remuestreo, métricas y diseño de validación; revisar redacción final de certeza; y preparar las demás series, API y presentación según priorización. La ejecución sin errores solo acredita ejecución. Series II–V no se presentan como completadas. No se han descargado fuentes adicionales durante este desarrollo de las cuatro respuestas de Serie I.
