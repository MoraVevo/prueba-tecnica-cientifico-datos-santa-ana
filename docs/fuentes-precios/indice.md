# Fuentes: azúcar No. 11, continuidad, pronóstico y oferta

Registro de evidencia para los incisos 2–4 de Serie III. Las fuentes respaldan especificaciones, procedencia, contrastes puntuales y criterios metodológicos; ninguna certifica por sí sola toda la serie de Kaggle.

| ID | Fuente y localización | Aporte | Límite |
|---|---|---|---|
| f001 | [ICE, Sugar No. 11 Futures](https://www.ice.com/products/23/), Market Specifications | Centavos de USD/libra, 112,000 lb, meses actuales y último día de negociación. | La especificación vigente no reconstruye el calendario histórico ni el enlace del proveedor. |
| f002 | [TradingView, back-adjustment](https://www.tradingview.com/support/solutions/43000685266-how-can-i-enable-backadjustment-for-continuous-futures/), explicación inicial | El cambio de contrato puede introducir diferencias de precio entre contratos; un ajuste necesita ambos precios. | Explica la mecánica general; no describe Yahoo ni prueba cómo se construyó el CSV. |
| f003 | [ICE, aviso de enero 2010](https://www.ice.com/publicdocs/futures_us/exchange_notices/exnot100109S11Jan.pdf), p. 1 | Existieron contratos de enero; excepción de último día el 22-12-2009. | No confirma que Yahoo utilizara ese contrato. Se consulta en web, sin descarga local. |
| f004 | [Kaggle, versión 188](https://www.kaggle.com/datasets/guillemservera/agricultural-futures), metadatos API | El autor declara Yahoo Finance como fuente; actualización 25-06-2024. | No documenta regla de enlace, ajuste ni significado de cierre frente a liquidación. |
| f005 | [FNB Agri-Weekly, 12-11-2010](fuentes/f005_fnb_12nov2010.pdf), p. 8, tabla ICE Sugar Futures | Publica 26.21 centavos/libra para Mar-11, coincidente con el CSV. | Es un informe bancario contemporáneo, no un archivo completo de liquidaciones oficiales. |
| f006 | [Reuters, 23-02-2016](https://www.brecorder.com/news/280393/sugar-soars-over-7pc-as-supply-concerns-take-hold), cotización a 1431 GMT | Respalda un repunte del azúcar y noticias de revisión del déficit ese día. | Es mayo e intradía: no certifica el cierre del CSV ni su variación exacta. |
| f007 | [Bloomberg, publicación 13-11-2010 IST](https://economictimes.indiatimes.com/markets/commodities/white-sugar-drops-most-in-a-year-on-exports-from-europe/articleshow/6916921.cms), cotización del viernes en Nueva York | Marzo cotiza 27.98 tras caer 1.68: cierre anterior implícito 29.66, coincidente con 11-11-2010. | Cotejo indirecto de un cierre previo, mediante noticia contemporánea. |
| f008 | [Hyndman y Athanasopoulos, FPP3, capítulo 5](https://otexts.com/fpp3/toolbox.html), secciones 5.2, 5.5, 5.9 y 5.10 | Referencia ingenua, orígenes móviles y evaluación de intervalos mediante cobertura, amplitud y Winkler. | El diseño mensual y la calibración empírica son decisiones del ejercicio. No establece garantía de cobertura bajo dependencia temporal. |
| f009 | [Hyndman y Athanasopoulos, FPP3, capítulo 7](https://otexts.com/fpp3/regression.html), secciones 7.3, 7.4 y 7.8 | Tendencias compartidas, rezagos distribuidos y diferencia entre predicción y causalidad. | La diferenciación no prueba estacionariedad; no identifica respuesta causal con esta muestra. |
| f010 | [FAO, Thailand](https://www.fao.org/4/x0513e/x0513e24.htm), Production | Caso histórico donde calendario, socas, precios, políticas, capacidad y clima acompañan expansión. | No establece calendario ni elasticidad de Guatemala; sin importar cifras al modelo. |

El [registro JSONL](fuentes.jsonl) conserva URL, localización, cita breve, fecha de consulta, alcance y huella del PDF descargado. Reúne diez fuentes para los incisos 2–4; un PDF descargado mediante el script seguro de la skill de recolección, con tabla FNB inspeccionada visualmente. No se observaron instrucciones hostiles en las fuentes revisadas.

## Evidencia pendiente para certificar continuidad

Faltan identificadores diarios de contrato, precios simultáneos de vencimientos adyacentes, fechas/reglas de cambio del proveedor, método de ajuste y definición de cierre/liquidación. Sin ellos no puede separarse exactamente un movimiento de mercado de un diferencial entre contratos. Las ventanas de calendario son indicadores de revisión y sensibilidades; no correcciones demostradas.
