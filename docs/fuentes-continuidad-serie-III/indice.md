# Fuentes — continuidad de precios del azúcar No. 11

Registro independiente del apartado de precios. Conservo los datos y archivos descargados en `outputs/serie3_continuidad/`, ignorado por Git.

## Fuentes consultadas

| ID | Fuente | Aporte y alcance |
|---|---|---|
| f001 | [ICE Sugar No. 11](https://www.ice.com/products/23/) | Benchmark, unidad y especificación vigente. No establece reglas de enlace Yahoo históricas. |
| f002, f021 | [ICE Daily Arb Mark, 27-ene-2011](https://www.ice.com/publicdocs/futures_us_reports/sugar/Settlement%20%20Daily%20Arb%20Price_Jan27.pdf) | Tabla de doce contratos en una fecha; marca intradía informativa. f021 agrega la huella de la descarga local. |
| f003 | [ICE Report Center](https://www.ice.com/report-center) | Reporta disponibilidad de datos históricos/diarios bajo términos de ICE; no encontré una descarga completa gratuita. |
| f004, f014, f022 | [Yahoo Help](https://help.yahoo.com/kb/yahoo-finance-plus/partnerships-sln2310.html), [Kaggle](https://www.kaggle.com/datasets/guillemservera/agricultural-futures), [Yahoo SB=F](https://finance.yahoo.com/quote/SB%3DF/) | Kaggle declara Yahoo como origen; la ficha actual de SB=F muestra Sugar No. 11/ICE. El mapeo histórico específico y la regla de roll no están demostrados. |
| f005 | [ICE Sugar No. 11 rulebook](https://www.ice.com/publicdocs/rulebooks/futures_us/11_Sugar_11.pdf) | Meses regulares y último día de negociación actuales; las enmiendas muestran cambios históricos. No aporta calendario completo por día ni metodología del proveedor. |
| f006 | [USDA ERS Documentation](https://www.ers.usda.gov/data-products/sugar-and-sweeteners-yearbook-tables/documentation) | Método del precio mensual world No. 11: promedio de liquidaciones ICE del vencimiento cercano durante un mes con cobertura completa. |
| f007 | [ICE Expiry Details](https://status.ice.com/products/23/Sugar-No-11-Futures/expiry) | Fechas por contrato para 2027–2029. No calendario histórico 2000–2024. |
| f008 | [CFTC Sugar Futures Only Open Interest](https://www.cftc.gov/sites/default/files/OCE/WEB/Report%20Data/futures_Sugar.html) | Confirma actividad agregada semanal; no valida precios ni vencimientos de saltos diarios. |
| f009, f010 | [ERS Yearbook](https://www.ers.usda.gov/data-products/sugar-and-sweeteners-yearbook-tables), [CSV ERS](https://ers.usda.gov/media/5170/world-us-and-mexican-sugar-and-corn-sweetener-prices.csv?v=69842) | Archivo público Table 3b. 291 meses completos y un junio parcial; la descarga local tiene SHA-256 `440e459531d22e86579b72853c328dad102db196c8c90599145f1f46344d60b8`. |
| f011, f012, f013, f016, f017, f018, f023 | FNB Agri-Weekly: [05-nov-2010](https://www.fnb.co.za/downloads/commercial/agriculture/agri-weekly-newsletters/2010/05nov10.pdf), [19-nov](https://www.fnb.co.za/downloads/commercial/agriculture/agri-weekly-newsletters/2010/19nov10.pdf), [26-nov](https://www.fnb.co.za/downloads/commercial/agriculture/agri-weekly-newsletters/2010/26nov10.pdf); [12-nov](https://www.fnb.co.za/downloads/commercial/agriculture/agri-weekly-newsletters/2010/12nov10.pdf) | Cotizaciones del mismo vencimiento Mar-11, inspeccionadas visualmente en p. 8. Tres fechas coinciden a 0.01 c/lb con el CSV. f016–f018 documentan la ubicación y cita definitivas de los registros iniciales; f023 registra el boletín 12-nov consultado en la colección separada. f013/f018 marcan la tabla 26-nov como posible republicación. |
| f015, f021 | [ICE Daily Arb Mark, 27-ene-2011](https://www.ice.com/publicdocs/futures_us_reports/sugar/Settlement%20%20Daily%20Arb%20Price_Jan27.pdf) | Doce precios simultáneos. ICE los separa del settlement oficial; f021 registra la huella de descarga definitiva. |
| f019, f020 | [INSEE, Sugar No. 11 first-expiration nearby, idbank 010002069](https://www.insee.fr/en/statistiques/serie/010002069) | Publica 6.1, 6.2 y 6.3 c/lb en oct–dic 2003. Ayuda a investigar la discrepancia con USDA; redondeo a una decimal y mismo origen general de mercado ICE. |

Los asientos f024/f025 documentan el método USDA y el intento sin datos de reapertura de INSEE, respectivamente. No añaden cotizaciones. Hay **25 registros JSONL**, incluidos asientos append-only de corrección y el registro f023 del boletín 12-nov; corresponden a **18 URL** únicas. Las fuentes reúnen especificación y calendario, dos series estadísticas mensuales, cuatro boletines de un mismo mercado, un informe de la bolsa y datos regulatorios agregados. No usé otro proveedor financiero de Yahoo como verificación independiente.

## Límites y búsquedas sin resultado

- ICE Report Center describe datos de settlement históricos, pero los identifica como market data propietaria sujeta a términos; no obtuve una descarga diaria contractual gratuita para 2000/2008.
- La página de Yahoo History devolvió HTTP 429 durante la consulta de metadatos/serie. Interrumpí ese acceso y no eludí el límite.
- Un enlace de ICE indexado para Arb Mark del 31-oct-2011 devolvió HTTP 404; solo descargué y cotejé el informe del 27-ene-2011.
- El informe FNB de 26-nov-2010 repite tabla y prosa del 19-nov; lo conservo como posible republicación y no lo cuento como movimiento nuevo.
- El contraste puntual INSEE de 2003 favorece el nivel del CSV frente a USDA ERS en tres meses, pero sus observaciones están redondeadas y no permiten certificar liquidaciones diarias.
- Límite central: faltan identificadores por contrato, observaciones diarias comparables en la fecha de roll y la regla histórica de selección/ajuste de Yahoo.

## Banderas de seguridad

No encontré instrucciones hostiles en páginas ni PDFs revisados. Validé los PDFs con el descargador seguro de la skill `marco-teorico` y los conservé solo en la carpeta ignorada `outputs/serie3_continuidad/`.
