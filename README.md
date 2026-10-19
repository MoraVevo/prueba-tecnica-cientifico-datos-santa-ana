# Prueba técnica de Científico de Datos — Ingenio Santa Ana

## Decisión de fuente y unidad: Serie I

El PDF describe `T_SPACRE` como toneladas de azúcar por acre, pero la [ficha oficial USDA-ARS](https://catalog.data.gov/dataset/louisiana-sugarcane-yield-data-2010-2021-collected-for-the-louisiana-variety-development-p) la define como **libras de azúcar por acre**. Se utiliza la definición USDA para que el precio de US$0.20/lb del ejercicio sea compatible. `TCA` está en ton de caña/acre y `TRS_TON` en lb de azúcar/ton de caña.

El CSV oficial y la copia Kaggle del enunciado se verificaron como idénticos. El descargador comprueba su SHA-256. En `TRS_TON` hay valores con prefijo sin definición: el ETL conserva el texto y prefijo aparte y utiliza el componente numérico final, coherente con `TCA × TRS_TON ≈ T_SPACRE`. No se utiliza el prefijo como variable agronómica.

## Serie I: cuatro respuestas

Se presenta un **primer borrador completo**. La fórmula económica se reprodujo de forma independiente sin detectar discrepancias aritméticas; la segmentación también se reconstruyó y revisó priorizando interpretación. Sigue pendiente la revisión integral del modelo supervisado. Las limitaciones de cobertura, ajuste ambiental y costos se reflejan en la certeza de las conclusiones. Se utiliza el dataset entregado y escenarios económicos explícitos.

| Pregunta | Respuesta del borrador | Evidencia |
| --- | --- | --- |
| Variedades y renovación | HOCP14-885, L01-299 y HO12-615 encabezan el aporte parcial anual estimado entre las 17 variedades que cumplen la cobertura propuesta. Duraciones iniciales: tres, cuatro y cuatro cosechas. La recomendación de HO12-615 como tercera opción está condicionada al ajuste ambiental aditivo; con promedios directos, L01-283 queda por encima. Prolongar podría elevar el aporte, aunque los cortes adicionales tienen menor respaldo; no se ha demostrado un máximo económico. | Notebook 03 |
| Modelo supervisado | Ridge, árbol y bosque; selección por validación temporal 2019–2020 y evaluación reservada 2021. Ridge elegido: MAE 2,145 lb/acre, R² 0.25; utilidad moderada y errores visibles. | Notebook 04 |
| Segmentación | Dos perfiles de 5 y 12 variedades, elegidos por interpretación y parsimonia. Productividad, TRS, conservación en ambientes comunes y variabilidad relativa; cobertura y excepciones individuales visibles. Otras 23 variedades quedan sin segmento por cobertura insuficiente. | Notebook 05 |
| Datos y ensayos propios | Seguimiento de parcela/cohorte, mediciones y costos; variedades aleatorizadas por bloques/sitios y seguimiento de socas; fase para contrastar políticas de renovación. | Documento de conclusiones |

El detalle de recomendaciones, certeza, impacto y riesgos está en [conclusiones de Serie I](docs/conclusiones-serie-I.md). Tres cosechas significan plantía + dos socas; cuatro significan plantía + tres socas.

`STAGE` identifica la fase de evaluación dentro del programa de mejoramiento varietal; `CROP` identifica la cosecha del ensayo. Para la recomendación económica se utilizan los ensayos outfield, correspondientes a `STAGE=5`, la etapa final de prueba de variedades para su posible uso comercial. Su diseño documentado tiene parcelas más largas, tres repeticiones y evaluación en múltiples localidades. Así se evita mezclar directamente etapas con distintos diseños y procedimientos de medición. Esta delimitación no convierte las etapas anteriores en datos incorrectos: se conservan y el modelo supervisado las utiliza. [Fuente: ficha USDA-ARS](https://catalog.data.gov/dataset/louisiana-sugarcane-yield-data-2010-2021-collected-for-the-louisiana-variety-development-program), [Shahi et al., sección 2.1](https://acsess.onlinelibrary.wiley.com/doi/10.1002/tpg2.20545).

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

- Se aplica el costo de US$14/ton a `TCA` (toneladas de caña/acre), suponiendo compatibilidad entre las unidades de tonelada del dataset y el supuesto económico; el PDF no especifica el tipo. La fórmula se reprodujo independientemente sin discrepancia aritmética.
- La rotación supone una cosecha anual, renovación inmediata, costos constantes y sin descuento ni descanso. Se comparan aportes **esperados**, no flujos observados de la misma parcela.
- Los precios de US$0.15, 0.20 y 0.25/lb son escenarios ilustrativos de ±25 %; no son una distribución de mercado estimada.
- La recomendación exige cobertura temporal/geográfica por corte y muestra duraciones adicionales de menor certeza. El escenario sin ajuste ambiental cambia el tercer puesto.
- El modelo usa entradas disponibles antes de la zafra y medias de años anteriores. La precisión observada es limitada; MAE no es un intervalo de confianza.
- Las validaciones de 2019 y 2020 son zafras contrastantes, no una referencia de años “normales”. En las filas usadas por el modelo, el promedio de `T_SPACRE` cayó entre 21 % y 27 % por etapa de 2018 a 2019 y subió entre 30 % y 41 % de 2019 a 2020. LSU AgCenter relaciona la baja de 2019 con la cosecha muy húmeda de 2018 y condiciones meteorológicas adversas. Para 2020 documenta efectos de las restricciones por COVID en operaciones de cruzamiento y en algunas pruebas de vivero; los ensayos finales outfield se reportaron en 12 localidades con tres repeticiones, y el resumen estatal informa mayores rendimientos de caña que en 2019. El dataset no permite aislar el efecto de COVID frente al clima, cambios de cobertura, manejo o medición; por ello se reportan errores por año y no se atribuye causalidad a la pandemia. [Contexto 2019](https://www.lsuagcenter.com/profiles/rbogren/articles/page1578688656809), [programa varietal 2020](https://www.lsuagcenter.com/~/media/system/2/d/4/f/2d4f56bf87ae85228f7652f9be15d589/03%20variety%20section%202020%20updatedpdf.pdf), [resumen estatal 2020](https://www.lsuagcenter.com/articles/page1677766893201).
- En las validaciones Ridge, el sesgo `predicción − observado` fue +2,148 lb/acre en 2019 y −1,078 lb/acre en 2020. El aumento de `T_SPACRE` también aparece en combinaciones coincidentes de `STAGE`, `CLONE`, `LOC` y `CROP` entre ambos años (418 combinaciones; sube en 90 % de las de etapa 3, 95 % de etapa 4 y 76 % de etapa 5). Son claves coincidentes, no parcelas pareadas: la fuente no tiene identificador de parcela/cohorte. Esto apunta a un cambio amplio entre zafras, pero no identifica su causa.
- Se preservan listas de variedades sin cobertura suficiente para economía/segmentación. Los faltantes extensos de fibra no se imputan para obligar a usarla.

## Archivos y entrega

`notebooks/` contiene evidencia reproducible; `scripts/` contiene descarga y ETL; `docs/` contiene conclusiones y continuidad; `bitacora.md` registra decisiones e hipótesis corregidas. `requirements.txt` fija dependencias. `data/raw/` y `data/processed/`, el PDF confidencial y entornos locales están excluidos de Git. El ZIP final debe excluir datasets e incluir `.git`, según el PDF.

## Pendientes

Completar la auditoría independiente del modelo supervisado y la consistencia final de las cuatro respuestas. Las cuatro entradas y las 17 asignaciones de la segmentación se reconstruyeron tras mejorar la comparación de cortes en ambientes comunes; sus perfiles siguen siendo exploratorios. Después priorizar las demás series, API y presentación. La ejecución sin errores solo acredita ejecución. Series II–V no se presentan como completadas. No se incorporaron datasets externos al modelado; las fuentes de contexto temporal están citadas arriba.
