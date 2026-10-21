"""Construye el EDA auditado de FAOSTAT y sus decisiones previas al ETL."""
from pathlib import Path

import nbformat as nbf


raiz = Path(__file__).resolve().parents[1]
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
nb = nbf.v4.new_notebook()
nb.cells = [
    md("""# Serie III · Auditoría del EDA de FAOSTAT, caña

Este análisis responde a la calidad y comparabilidad del inciso 1 antes de segmentar.
El periodo requerido es **1961–2023**; la fuente contiene también 2024, que se conserva fuera del análisis.
Todas las exclusiones de ámbito se exportan con valores, flags, código, año y motivo. Ningún extremo se elimina por su magnitud.
El generador anterior y notebook original quedan como respaldo local en outputs/serie3_eda/revision/respaldo/."""),
    code("""from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display

raiz = Path.cwd()
if raiz.name == 'notebooks':
    raiz = raiz.parent
if str(raiz) not in sys.path:
    sys.path.insert(0, str(raiz))
from scripts.auditar_faostat_serie3 import auditar
resultado = auditar(raiz)
resumen = resultado['resumen']
paises, cobertura = resultado['paises'], resultado['cobertura']
calidad, coherencia = resultado['calidad'], resultado['coherencia']
salida = raiz / 'outputs/serie3_eda/revision'
display(pd.Series({k:v for k,v in resumen.items() if k not in ['huellas_fuentes','anos_en_fuente']}, name='Auditoría'))"""),
    md("""## Ámbito, unidades y fuentes

Se comprueba clave área/elemento única, códigos presentes en diccionario, kg/ha para rendimiento, ha para área y t para producción. La versión NOFLAG coincide numéricamente con la versión de flags en todas las celdas de caña, incluidas ausencias; no se completa una usando la otra.

Una sola selección de países/territorios se utiliza para cobertura, calidad, extremos y gráficos: códigos menores de 5000, sin China agregado ni entidades históricas. Los componentes de China permanecen por separado. No se empalma Sudán/Etiopía con predecesores como si fuesen un país inmutable. Para comprobar el balance mundial histórico sí se consideran predecesores en sus años, manteniendo una vista distinta y explícita. No se interpreta exclusión de ámbito como dato erróneo."""),
    code("""fuera = pd.read_csv(salida / 'filas_fuera_ambito.csv')
display(fuera.groupby('motivo_fuera_ambito').agg(celdas=('valor','size'), areas=('area','nunique')))
display(cobertura[cobertura.baja_cobertura])
print('Áreas con algún indicador de baja cobertura:', cobertura.loc[cobertura.baja_cobertura, 'area'].nunique())
fig, axes = plt.subplots(1, 2, figsize=(11, 3.6), constrained_layout=True)
for elemento, g in cobertura.groupby('elemento'):
    axes[0].hist(g.n_anos, bins=[0,10,20,30,40,50,60,64], histtype='step', label=elemento)
axes[0].set(xlabel='Años observados por área e indicador', ylabel='Áreas', title='Cobertura 1961–2023')
axes[0].legend(fontsize=8)
axes[1].plot(calidad.ano, 100*calidad.proporcion_no_oficial)
axes[1].set(xlabel='Año', ylabel='% entre valores observados', title='Producción con flag E/I/X')
fig.savefig(salida / 'cobertura_calidad.png', dpi=150)
plt.show()
display(calidad.iloc[[0,-1]])"""),
    md("""## Calidad: denominador y ausencia

La proporción E/I/X se calcula **sobre producción con valor observado**, sin convertir NaN a texto. Se reportan observados, ausentes y valores sin flag por separado. El flag M significa que el dato falta/no puede existir según el diccionario; no se convierte en cero ni se asume ausencia aleatoria. Se conserva el código de flag original.

Menos de diez años marca baja cobertura para revisión, sin excluir por ahora esas áreas. La selección final de ventanas comunes y cobertura mínima pertenece a la segmentación; no se rellena con ceros o interpolación para forzar 63 observaciones por país."""),
    code("""balance = pd.read_csv(salida / 'balance_mundial.csv')
balance_periodo = balance[balance.ano.between(1961,2023)]
print('Máxima diferencia relativa mundial 1961–2023:', balance_periodo.diferencia_relativa.abs().max())
print('Máxima diferencia China/componentes:', balance_periodo.china_menos_componentes_t.abs().max())
display(balance.tail(3))
produccion = paises[paises.elemento.eq('Production')]
top = produccion[produccion.ano.eq(2023)].nlargest(8,'valor').area
assert 'China' not in top.values
fig, ax = plt.subplots(figsize=(10,4), constrained_layout=True)
for area in top:
    g = produccion[produccion.area.eq(area)]
    ax.plot(g.ano,g.valor/1e6,label=area)
ax.set(xlabel='Año',ylabel='Millones de toneladas',title='Principales productores de 2023 · mismo ámbito en toda la figura')
ax.legend(fontsize=8)
fig.savefig(salida / 'productores_sin_solapamientos.png',dpi=150)
plt.show()"""),
    md("""## Consistencia aritmética y extremos

La identidad esperada es producción (t) = área (ha) × rendimiento (kg/ha) / 1000. Se conservan tripletas incompletas y se distinguen de las comparables. Una discrepancia >1 % sirve para priorizar revisión, **sin definir invalidez**.

En áreas pequeñas, redondear hectáreas a enteros puede generar diferencias relativas grandes. Se calcula el área implícita producción×1000/rendimiento y su distancia al área publicada. Una distancia ≤0.5 ha es compatible con ese supuesto de redondeo, sin demostrar que ése sea el protocolo utilizado. El percentil 99 de rendimiento solo marca observaciones; ni E/I ni un extremo prueban un error. No se sustituyen ceros por faltantes de forma automática."""),
    code("""marcas = coherencia[coherencia.en_ambito_paises & coherencia.revisar]
display(marcas.groupby('area').agg(casos=('ano','size'), max_error_relativo=('error_relativo','max'), compatibles_redondeo=('compatible_redondeo_area_1ha','sum')))
display(marcas[['area','ano','Area harvested','Production','Yield','error_relativo','distancia_area_implicita_ha']].head(12))
extremos = pd.read_csv(salida / 'extremos_rendimiento.csv')
display(extremos[['area','ano','valor','flag']].nlargest(10,'valor'))
print('Exclusiones por error demostrado:',resumen['exclusiones_por_error'])"""),
    md("""## Guatemala y preparación para segmentar

La trayectoria se muestra en las unidades confirmadas de la fuente y en el periodo requerido. Aún no se identifican pares ni se eligen variables/clusters: para ello se definirán ventanas comparables y sensibilidad a calidad/cobertura, conservando las marcas anteriores. La identidad producción/área/rendimiento también advierte que las tres dimensiones no son independientes."""),
    code("""guatemala = paises[paises.area.eq('Guatemala')]
display(guatemala[guatemala.ano.eq(2023)][['elemento','unidad','valor','flag']])
fig, axes = plt.subplots(1,3,figsize=(12,3.5),constrained_layout=True)
for ax, elemento, unidad in zip(axes,['Area harvested','Yield','Production'],['ha','kg/ha','t']):
    g = guatemala[guatemala.elemento.eq(elemento)]
    ax.plot(g.ano,g.valor,color='#087e8b')
    ax.set(title=elemento,xlabel='Año',ylabel=unidad)
fig.suptitle('Guatemala · 1961–2023')
fig.savefig(salida / 'guatemala_trayectoria.png',dpi=150)
plt.show()
assert resumen['celdas_paises'] + resumen['celdas_fuera_ambito'] == resumen['celdas_totales']
assert resumen['NOFLAG_coincide'] and resumen['flags_revisar'] == 0"""),
    md("""## Conclusión y decisión para avanzar

Se corrigieron el conteo de países de baja cobertura, el denominador de calidad, los filtros inconsistentes y la inclusión involuntaria de 2024. Se verificaron unidades, identidad de las dos versiones, conservación y agregación mundial. El resultado permite continuar con **ETL y segmentación exploratoria**, usando el ámbito explícito y un análisis de cobertura/flags; no certifica exactitud agronómica de cada dato.

Se conservan ceros, ausencias y extremos con sus marcas. La próxima unidad es definir una representación comparable de países y ubicar Guatemala, sin sumar territorios solapados ni completar trayectorias artificialmente. No se infiere renovación o causalidad a partir de estas series nacionales.

Para precios, la descarga está completa pero el enlace/ajuste de contratos de Sugar_data.csv sigue pendiente de auditoría específica antes de interpretar saltos o entrenar pronósticos. Los outputs anteriores a esta revisión se consideran históricos; la evidencia vigente de este EDA está en **outputs/serie3_eda/revision/**."""),
]
nb.metadata = {"kernelspec": {"display_name": "Python (prueba-santa-ana)", "language": "python", "name": "prueba-santa-ana"}, "language_info": {"name": "python", "version": "3.13.14"}}
nbf.write(nb, raiz / "notebooks/13_eda_faostat_serie3.ipynb")
