# Continuidad de precios del azúcar No. 11

## Resultado y alcance

El archivo de `Sugar_data.csv` sigue el nivel mensual del mercado Sugar No. 11 con alta proximidad en la mayoría de los meses observados. Tres tablas contemporáneas cotejan el mismo vencimiento Mar-11 con los cierres del archivo. Esto aporta corroboración parcial de que hay movimientos reales del mercado en la serie, pero no certifica su enlace diario entre vencimientos ni permite atribuir cada salto de 2000 o 2008 a un contrato específico.

Recomiendo conservar el dato original y usarlo para describir el mercado con sensibilidades visibles. Las estimaciones de volatilidad diaria, extremos y pérdidas potenciales deben tratarse como dependientes de la continuidad de Yahoo. No conviene convertir esos valores directamente en una regla de cobertura o presupuesto del ingenio mientras no se conozca el vencimiento diario y el método de cambio entre contratos.

## Método y procedencia

El CSV conserva **6,097 filas** entre 2000-03-01 y 2024-06-24, con precios en centavos de dólar por libra. Sus metadatos de Kaggle declaran Yahoo Finance como proveedor y su descripción general enumera OHLCV. La tabla entregada no incluye identificador diario de contrato ni una regla de roll. La página vigente de Yahoo presenta `SB=F` como azúcar No. 11 del contrato activo y señala ICE Futures como fuente de cotización retrasada. Eso identifica el ticker actual, pero no prueba que Kaggle usara ese ticker específico ni explica su serie histórica. La página de histórico de Yahoo respondió HTTP 429 en la consulta; no sorteé ese límite. [Metadatos de Kaggle](https://www.kaggle.com/datasets/guillemservera/agricultural-futures), [cotización actual de Yahoo Finance](https://finance.yahoo.com/quote/SB%3DF/).

La ficha de ICE describe el No. 11 como benchmark mundial de azúcar cruda, contrato físico de 112,000 libras y cotización en centavos por libra. Sus reglas enumeran vencimientos de marzo, mayo, julio y octubre en la serie regular actual; el reglamento también conserva evidencia histórica de enero y sus enmiendas, incluida una efectiva el 13 de marzo de 2008. El calendario vigente de vencimientos detalla fechas por contrato para 2027–2029, pero no proporciona el calendario histórico completo de 2000–2024. No aplico el calendario actual como si certificara los cambios del proveedor. [Especificación ICE](https://www.ice.com/products/23/), [reglamento Sugar No. 11](https://www.ice.com/publicdocs/rulebooks/futures_us/11_Sugar_11.pdf), [calendario ICE](https://status.ice.com/products/23/Sugar-No-11-Futures/expiry).

La documentación de USDA ERS define su precio mundial mensual como promedio de liquidaciones diarias ICE No. 11 del vencimiento cercano para un mes entero. Comparo esa serie con la media aritmética de los cierres diarios del CSV. Son estadísticas de frecuencia y definición distintas: la coincidencia entre medias mensuales no confirma cada cierre diario ni el contrato que Yahoo mostraba en cada fecha. [Método USDA ERS](https://www.ers.usda.gov/data-products/sugar-and-sweeteners-yearbook-tables/documentation).

## Contrastes

### Niveles mensuales

El archivo termina el 24 de junio de 2024. Por eso la comparación principal usa **291 meses completos**; junio de 2024 queda en una fila parcial separada, con 15 sesiones. El archivo USDA descargado presenta estos valores con tres decimales.

| Métrica, meses completos | Resultado |
|---|---:|
| Meses cotejados | 291 |
| Mediana de la diferencia porcentual absoluta entre medias | 0.00543 % |
| Percentil 90 de esa diferencia | 0.14998 % |
| Meses a ≤0.0011 centavos/libra de la cifra ERS descargada | 158 / 291 |
| Meses con diferencia absoluta >1 % | 14 / 291 |

En **2008**, las doce medias mensuales del CSV están a menos de 0.018 % de ERS. Para **2000**, abril–junio también están cerca; julio difiere −0.065 centavos/libra (−0.67 %). Esta coincidencia apoya el orden de magnitud y la evolución mensual en esas ventanas, no una trayectoria de un solo contrato.

Hay divergencias mensuales que no deben ocultarse. ERS informa 5.696, 5.574 y 4.667 centavos/libra entre octubre y diciembre de 2003, mientras las medias de cierre del CSV son 6.098, 6.191 y 6.344. Una serie pública mensual de INSEE, descrita como azúcar No. 11 del primer vencimiento cercano ICE Nueva York, publica 6.1, 6.2 y 6.3, redondeados a una decimal. Para esos tres meses INSEE queda más cerca del CSV. Esto apunta a revisar la fuente ERS o una diferencia en sus definiciones; no determina cuál representa el settlement diario exacto, porque ambas estadísticas están agregadas y redondeadas. USDA ERS e INSEE son publicaciones distintas, pero ambas se refieren a precios derivados del mismo mercado ICE y no constituyen proveedores de mercado independientes. [Serie mensual INSEE, idbank 010002069](https://www.insee.fr/en/statistiques/serie/010002069).

También observo otros once meses completos con discrepancia mayor a 1 %, entre ellos octubre–noviembre de 2002, 2010-10, 2011-07 y 2012-02. La salida reproducible enumera los catorce meses y sus diferencias, sin tratarlas como error probado ni corregirlas.

### Cotizaciones de un vencimiento identificado

Las tablas de FNB para el contrato **Mar-11** publican 31.76 centavos/libra el 5 de noviembre, 26.21 el 12 y 26.15 el 19 de noviembre de 2010. Los tres valores coinciden a 0.01 centavos/libra con el cierre del CSV en la misma fecha. Los cambios entre observaciones semanales son −17.47 % en siete días calendario y −0.23 % en los siguientes siete días. El primer movimiento muestra que el mercado tuvo una variación de magnitud parecida a la que presenta la serie, pero el boletín no certifica la serie diaria completa. El boletín del 26 de noviembre repite exactamente tabla y texto de la semana del 19; lo conservo marcado como posible republicación y no cuenta como un nuevo cotejo. [FNB, 5 de noviembre](https://www.fnb.co.za/downloads/commercial/agriculture/agri-weekly-newsletters/2010/05nov10.pdf), [12 de noviembre](https://www.fnb.co.za/downloads/commercial/agriculture/agri-weekly-newsletters/2010/12nov10.pdf), [19 de noviembre](https://www.fnb.co.za/downloads/commercial/agriculture/agri-weekly-newsletters/2010/19nov10.pdf), [26 de noviembre](https://www.fnb.co.za/downloads/commercial/agriculture/agri-weekly-newsletters/2010/26nov10.pdf).

Un informe de ICE del 27 de enero de 2011 publica precios Arb Mark simultáneos para doce vencimientos, con curva descendente entre Mar-11 y Mar-13. El informe explica que estas marcas siguen procedimientos de liquidación, pero se forman con operaciones/ofertas de 12:28 a 12:30 p. m. y son informativas; la liquidación oficial se determina más tarde. Acredita que había varios precios contractuales consultables en una fecha, no el settlement ni una historia completa gratuita. [ICE Sugar No. 11 Daily Arb Mark, 27 de enero de 2011](https://www.ice.com/publicdocs/futures_us_reports/sugar/Settlement%20%20Daily%20Arb%20Price_Jan27.pdf).

### Saltos y calidad diaria

Las **11 filas OHLC incoherentes** del archivo coinciden con la ventana de calendario usada como proxy de posible enlace. Esa coincidencia apoya la revisión prioritaria, pero la ventana no demuestra que el proveedor cambiara de contrato en esas fechas. Conservo todas las filas y no calculo valores sustitutos.

En 2000-04-28 el cierre cae 16.50 % y el volumen informado es cero; el 2000-05-01 el cierre sube 26.55 %. La media mensual de mayo está muy cerca de ERS, pero no informa qué vencimiento se usó en cada jornada. En 2008-06-30 el cierre (12.04) supera el máximo OHLC publicado (11.59); al día siguiente el cierre pasa a 13.72, un cambio de 13.95 %. También aparecen movimientos de −10.71 % el 17 de marzo y +12.70 % el 1 de octubre de 2008. El promedio mensual de 2008 sigue de cerca ERS, pero no puede resolver si estos saltos diarios son movimiento de mercado, diferencial entre vencimientos o ambos.

Los registros semanales de interés abierto de CFTC confirman actividad agregada del mercado en 2008, no el precio ni el contrato detrás de cada salto. No los uso para validar retornos diarios. El registro de fuentes mantiene esta distinción.

## Cobertura y limitaciones

La evidencia permite clasificar el inciso como **parcialmente verificado**:

- **Corroboración puntual por vencimiento:** tres cotizaciones Mar-11 publicadas el mismo día coinciden con el cierre CSV; el movimiento observado entre dos referencias semanales tiene apoyo directo en el mercado citado.
- **Coincidencia de proveedor/definición agregada:** comparo 291 medias mensuales con USDA ERS; 14 divergen más de 1 %. INSEE ofrece una segunda publicación oficial mensual que ayuda a esclarecer tres diferencias de 2003, pero también deriva de ICE y redondea a una decimal.
- **Certificación contractual completa:** pendiente. Necesito identificadores diarios de vencimiento para el CSV, liquidaciones o cierres oficiales diarios por contrato, calendario histórico de roll y documentación del algoritmo de Yahoo/Kaggle. La página de reportes ICE señala que la data histórica de mercado es propietaria y sujeta a términos; no tengo acceso gratuito a una descarga diaria completa. [ICE Report Center](https://www.ice.com/report-center).

Por tanto, los saltos de 2000/2008 siguen siendo **movimientos observados en el archivo** con contexto y contraste mensual, no movimientos certificados de un vencimiento individual. No fabrico una serie corregida ni estimo un ajuste de roll sin precios simultáneos por contrato.

**Evaluación gerencial.** Es razonable mantener el análisis histórico como escenario de riesgo del mercado de azúcar No. 11, siempre que las volatilidades y extremos se presenten como sensibles a la construcción de la serie. No debe transformarse en una cotización diaria contractual ni en un precio local recibido por Santa Ana. Para decisiones de presupuesto, exposición o cobertura, primero necesito cerrar el linaje del vencimiento o presentar las métricas como aproximaciones del mercado continuo, con certeza moderada para niveles mensuales y baja para los saltos diarios específicos.

## Reproducción y evidencia

El script descarga la tabla CSV pública de ERS a una ruta ignorada solo si aún no está disponible; la descarga usada fue de 10,901,118 bytes, HTTP 200, SHA-256 `440e459531d22e86579b72853c328dad102db196c8c90599145f1f46344d60b8`. El CSV original permanece íntegro y valido su SHA-256 antes de analizarlo. Expongo los cotejos manuales con fuente, contrato, fecha y estado de republicación.

```powershell
.\.venv\Scripts\python.exe scripts\verificar_continuidad_serie3.py
.\.venv\Scripts\python.exe -m pytest tests\unitarias\test_continuidad_serie3.py tests\integracion\test_continuidad_serie3_resultados.py -q
.\.venv\Scripts\python.exe -m nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=600 notebooks\19_continuidad_precios_serie3.ipynb
```

El [notebook 19](../notebooks/19_continuidad_precios_serie3.ipynb) muestra las tablas y gráficos. El [script reproducible](../scripts/verificar_continuidad_serie3.py) genera contrastes mensuales, comparación INSEE 2003, movimientos Mar-11 y filas marcadas de 2000/2008. Las seis pruebas focales contrastan descarga en frío con cabecera entrecomillada, caché, conservación de crudos, cambio semanal, mes parcial, discrepancia INSEE y resultados materializados. Conservo los meses fuera de la comparación principal con motivo en `meses_fuera_comparacion_principal.csv`. Mantengo las salidas y los PDF públicos descargados en `outputs/serie3_continuidad/`, ignorado por Git. [Registro de fuentes](fuentes-continuidad-serie-III/indice.md).
