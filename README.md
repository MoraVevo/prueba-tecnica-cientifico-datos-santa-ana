# Prueba técnica de Científico de Datos — Ingenio Santa Ana

## Decisión de fuente y unidad: Serie I

El PDF de la prueba llama a `T_SPACRE` **toneladas de azúcar por acre**. La documentación del conjunto de datos publicada por el Servicio de Investigación Agrícola del Departamento de Agricultura de Estados Unidos (USDA-ARS) la define como **libras de azúcar por acre** (`lbs./acre`). Para este análisis se seguirá la unidad de la fuente oficial, porque es la institución que publica y documenta los datos originales. Consulta la [ficha del USDA-ARS en Data.gov](https://catalog.data.gov/dataset/louisiana-sugarcane-yield-data-2010-2021-collected-for-the-louisiana-variety-development-p) y el [CSV original asociado](https://ndownloader.figshare.com/files/49874100).

Se contrastó el CSV oficial completo con la copia de Kaggle indicada en el enunciado: ambas descargas tienen el mismo SHA-256 y los mismos bytes. El perfil inicial también detectó que 10,485 celdas de `TRS_TON` contienen dos componentes numéricos separados por espacios. El patrón también aparece en el XLSX oficial; la ficha de USDA no define el prefijo de dos dígitos. El ETL conserva el texto completo en `TRS_TON_raw`, guarda el prefijo como texto en `TRS_TON_prefijo_sin_interpretar` y deja `TRS_TON` como el componente numérico final, aislado para métricas y modelos. Con esta decisión, `T_SPACRE` coincide con `TCA × TRS_TON` dentro del 1 % en 29,317 de 29,340 filas completas y positivas (99.92 %); hay 23 filas fuera de esa tolerancia. El componente final es coherente con la relación de unidades, pero el prefijo aún no tiene interpretación confirmada y no se tratará como variable agronómica. La relación dimensional es libras de azúcar por tonelada de caña × toneladas de caña por acre = libras de azúcar por acre. La unidad absoluta se adopta de la ficha oficial USDA. La auditoría de fuente está en [`notebooks/01_revision_fuente_y_unidades.ipynb`](notebooks/01_revision_fuente_y_unidades.ipynb) y el perfil inicial en [`notebooks/02_perfil_eda_inicial_serie1.ipynb`](notebooks/02_perfil_eda_inicial_serie1.ipynb).

Esta precisión importa porque el PDF supone un precio de US$0.20 por libra de azúcar recuperable. Tratar `T_SPACRE` como toneladas cambiaría el ingreso estimado por un factor grande y no corresponde a la definición documentada del dataset.

## Objetivo y alcance actual

La Serie I analiza ensayos varietales de caña de Louisiana entre 2010 y 2021. La fuente describe hasta 32 localidades y más de mil genotipos, no datos de las fincas de Ingenio Santa Ana. Los resultados se presentarán como evidencia de ensayos externos y se explicarán sus límites de transferencia al contexto guatemalteco.

El primer notebook documenta la fuente, verifica unidades y registra alertas de calidad visibles en el archivo. Todavía no contiene una recomendación de variedades, análisis de renovación ni modelos predictivos; esos resultados se desarrollarán y validarán en los siguientes pasos.

## Fuente y descarga

La fuente prioritaria es la ficha oficial del [USDA-ARS en Data.gov](https://catalog.data.gov/dataset/louisiana-sugarcane-yield-data-2010-2021-collected-for-the-louisiana-variety-development-p). El CSV original se descarga desde el recurso asociado de [Ag Data Commons / Figshare](https://ndownloader.figshare.com/files/49874100). El archivo de Kaggle enlazado por el PDF se verificó como una copia idéntica; se cita USDA como fuente de autoridad y para documentar las unidades.

El archivo se guarda en `data/raw/`, carpeta excluida de Git y de la entrega ZIP. Para repetir el análisis en Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python scripts/descargar_serie1.py
python scripts/etl_serie1.py
jupyter lab
```

Después abre y ejecuta los notebooks de `notebooks/` en orden. El script ETL crea una copia provisional, un reporte de calidad y un subconjunto de filas marcadas para revisión con sus motivos en `data/processed/`. Conserva `TRS_TON` original en `TRS_TON_raw`, separa el prefijo no interpretado y deja la columna analítica `TRS_TON` libre de ese prefijo. No elimina ni imputa registros. Si un análisis posterior justifica excluir filas, se conservarán aparte con el criterio y motivo de exclusión. El script de descarga comprueba el SHA-256 de la versión documentada para detectar cambios o descargas incompletas.

## Estructura del proyecto

```text
.
├── data/raw/                       # CSV local, ignorado por Git
├── docs/                           # Contexto, decisiones y avance
├── notebooks/
│   ├── 01_revision_fuente_y_unidades.ipynb
│   └── 02_perfil_eda_inicial_serie1.ipynb
├── scripts/
│   ├── etl_serie1.py
│   └── descargar_serie1.py
├── README.md
├── bitacora.md
└── requirements.txt
```

## Reproducibilidad y decisiones

- Las cifras de los hallazgos deben recalcularse desde el CSV de USDA mediante los notebooks y scripts del repositorio.
- Los datos crudos, el PDF confidencial, secretos y entornos locales no forman parte de Git.
- El CSV tiene tres columnas finales auxiliares sin nombre estándar y seis notas sueltas en la última. El primer notebook las identifica por separado de las doce variables del ensayo.
- Mantendremos explícitos los supuestos, limitaciones y tareas pendientes en el notebook, la bitácora y esta guía conforme avance la prueba.

## Pendiente

Validar la unidad experimental y el significado del prefijo observado en 10,485 celdas `TRS_TON`; ampliar el análisis de productividad, calidad, longevidad y estabilidad; comparar modelos para la siguiente zafra; evaluar sensibilidad económica al precio; y proponer un plan de captura y ensayos propios. Las actividades fuera del alcance se documentarán junto con cómo se abordarían.
