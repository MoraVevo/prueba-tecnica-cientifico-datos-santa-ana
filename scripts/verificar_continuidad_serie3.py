"""Contrastes públicos para la continuidad del Sugar No. 11 (Serie III.2).

No reconstruye ni ajusta contratos: el CSV no identifica el vencimiento diario.
Compara promedios mensuales con USDA ERS y cotejos puntuales por contrato.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from urllib.request import urlopen

import numpy as np
import pandas as pd


URL_USDA = "https://ers.usda.gov/media/5170/world-us-and-mexican-sugar-and-corn-sweetener-prices.csv?v=69842"
NOMBRE_USDA = "ers_precios_azucar_world_2026-10-20.csv"
FUENTE_CSV_SHA256 = "944471f40adce9a236bc992e3824f8c07f8f87b0f1aa7a5e50c47c888dcd52d1"
FUENTE_USDA_SHA256 = "440e459531d22e86579b72853c328dad102db196c8c90599145f1f46344d60b8"

# Valores transcritos y cotejados visualmente en tablas FNB contemporáneas.
# Las tablas de 19 y 26 Nov publican el mismo precio; el segundo boletín parece
# repetir contenido y se conserva como control, no como una cuarta observación.
COTIZACIONES_FNB = [
    {"fecha": "2010-11-05", "contrato": "Mar-11", "referencia": 31.76,
     "fuente": "f016", "estado": "cotejo_publicado"},
    {"fecha": "2010-11-12", "contrato": "Mar-11", "referencia": 26.21,
     "fuente": "f023", "estado": "cotejo_publicado"},
    {"fecha": "2010-11-19", "contrato": "Mar-11", "referencia": 26.15,
     "fuente": "f017", "estado": "cotejo_publicado"},
    {"fecha": "2010-11-26", "contrato": "Mar-11", "referencia": 26.15,
     "fuente": "f018", "estado": "posible_republicacion_obsoleta"},
]

# Valores de la serie estadística oficial INSEE 010002069, redondeados a 0.1.
INSEE_2003 = [
    {"mes": "2003-10", "insee_cercano": 6.1},
    {"mes": "2003-11", "insee_cercano": 6.2},
    {"mes": "2003-12", "insee_cercano": 6.3},
]


def sha256(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def cargar_usda(ruta: Path) -> pd.DataFrame:
    """Lee el archivo cacheado o lo obtiene de USDA ERS y valida el formato."""
    if not ruta.exists():
        ruta.parent.mkdir(parents=True, exist_ok=True)
        with urlopen(URL_USDA, timeout=60) as respuesta:
            datos = respuesta.read()
        cabecera = datos.removeprefix(b"\xef\xbb\xbf")
        if not cabecera.startswith((b"Table_number,", b'"Table_number",')):
            raise ValueError("USDA no devolvió el CSV esperado")
        ruta.write_bytes(datos)
    if sha256(ruta) != FUENTE_USDA_SHA256:
        raise ValueError("La huella del CSV USDA cambió; se requiere revisión antes de compararlo")
    datos = pd.read_csv(ruta, low_memory=False)
    requeridas = {"Table_number", "Year_cat", "Period_cat", "Year", "Period", "Value"}
    if not requeridas.issubset(datos.columns):
        raise ValueError("El archivo USDA no contiene las columnas esperadas")
    return datos


def preparar_mensual(crudo: pd.DataFrame, usda: pd.DataFrame) -> pd.DataFrame:
    """Compara medias de cierres diarios íntegros con la liquidación cercana mensual."""
    d = crudo.copy(deep=True)
    d["date"] = pd.to_datetime(d["date"])
    d["mes"] = d.date.dt.to_period("M")
    mensual = d.groupby("mes", as_index=False).agg(
        sesiones=("close", "size"), cierre_medio=("close", "mean"),
        cierre_inicio=("close", "first"), cierre_fin=("close", "last"),
    )
    primera_fecha, ultima_fecha = d.date.min(), d.date.max()
    primer_mes, ultimo_mes = primera_fecha.to_period("M"), ultima_fecha.to_period("M")
    mensual["mes"] = mensual.mes.astype(str)
    periodos = pd.PeriodIndex(mensual.mes, freq="M")
    mensual["mes_completo_en_archivo"] = (
        ((periodos != primer_mes) | (primera_fecha == primer_mes.start_time))
        & ((periodos != ultimo_mes) | (ultima_fecha == ultimo_mes.end_time.normalize()))
    )

    e = usda.loc[
        usda.Table_number.astype(str).eq("3b")
        & usda.Year_cat.eq("Calendar")
        & usda.Period_cat.eq("Month")
    ].copy()
    e["mes"] = e.Year.astype(int).astype(str) + "-" + e.Period.astype(int).astype(str).str.zfill(2)
    e = e[["mes", "Value"]].rename(columns={"Value": "usda_cercano_mensual"})
    z = mensual.merge(e, on="mes", how="left", validate="one_to_one")
    motivos = pd.Series("", index=z.index)
    motivos.loc[~z.mes_completo_en_archivo] += "mes_parcial_en_fuente;"
    motivos.loc[z.usda_cercano_mensual.isna()] += "sin_referencia_USDA;"
    z["motivo_fuera_comparacion_principal"] = motivos.str.rstrip(";")
    z["diferencia_centavos"] = z.cierre_medio - z.usda_cercano_mensual
    z["diferencia_pct"] = 100 * z.diferencia_centavos / z.usda_cercano_mensual
    return z


def preparar_fnb(crudo: pd.DataFrame) -> pd.DataFrame:
    """Coteja las mismas fechas y conserva explícito el reporte republicado."""
    d = crudo.copy(deep=True)
    d["date"] = pd.to_datetime(d.date)
    r = pd.DataFrame(COTIZACIONES_FNB)
    r["date"] = pd.to_datetime(r.fecha)
    r["horizonte_dias_desde_cotejo_anterior"] = r.date.diff().dt.days
    r = r.merge(d[["date", "close", "volume"]], on="date", how="left", validate="one_to_one")
    r["diferencia_csv_centavos"] = r.close - r.referencia
    r["coincide_a_centavo"] = r.diferencia_csv_centavos.abs().lt(0.005)
    r["retorno_contrato_vs_cotejo_pct"] = 100 * r.referencia.pct_change()
    return r


def preparar_insee(mensual: pd.DataFrame) -> pd.DataFrame:
    """Contrasta la discrepancia 2003 con INSEE, reportada a una decimal."""
    r = pd.DataFrame(INSEE_2003)
    r = r.merge(mensual, on="mes", how="left", validate="one_to_one")
    r["diferencia_csv_centavos"] = r.cierre_medio - r.insee_cercano
    r["diferencia_ers_centavos"] = r.usda_cercano_mensual - r.insee_cercano
    return r


def preparar_revision(crudo: pd.DataFrame) -> pd.DataFrame:
    """Marca saltos y calidad en años focales; no excluye ni corrige filas."""
    d = crudo.copy(deep=True)
    d["date"] = pd.to_datetime(d.date)
    d["retorno_pct"] = 100 * d.close.pct_change()
    d["retorno_log_pct"] = 100 * np.log(d.close / d.close.shift())
    d["ohlc_incoherente"] = (
        (d.high + 1e-5 < d[["open", "low", "close"]].max(axis=1))
        | (d.low - 1e-5 > d[["open", "high", "close"]].min(axis=1))
    )
    d["volumen_cero"] = d.volume.eq(0)
    d["fecha_anterior"] = d.date.shift()
    d["cierre_anterior"] = d.close.shift()
    d["dias_desde_anterior"] = d.date.diff().dt.days
    focal = d.date.dt.year.isin([2000, 2008])
    umbral = d.loc[d.retorno_log_pct.notna(), "retorno_log_pct"].abs().quantile(.99)
    extremos = focal & d.retorno_log_pct.abs().ge(umbral)
    incoherentes = d.ohlc_incoherente
    return d.loc[extremos | incoherentes, [
        "date", "fecha_anterior", "dias_desde_anterior", "open", "high", "low", "close",
        "cierre_anterior", "retorno_pct", "retorno_log_pct", "volume", "ohlc_incoherente",
        "volumen_cero",
    ]].sort_values("date").reset_index(drop=True)


def ejecutar(raiz: Path) -> dict:
    raiz = Path(raiz)
    salida = raiz / "outputs/serie3_continuidad"
    salida.mkdir(parents=True, exist_ok=True)
    ruta_crudo = raiz / "data/raw/serie3/Sugar_data.csv"
    ruta_usda = salida / NOMBRE_USDA
    crudo = pd.read_csv(ruta_crudo)
    if sha256(ruta_crudo) != FUENTE_CSV_SHA256:
        raise ValueError("La huella del CSV crudo cambió; no se sustituye silenciosamente")
    usda = cargar_usda(ruta_usda)
    mensual = preparar_mensual(crudo, usda)
    fnb = preparar_fnb(crudo)
    insee = preparar_insee(mensual)
    revision = preparar_revision(crudo)
    # Permite ejecutar el archivo directamente desde la raíz del proyecto,
    # además de importarlo durante las pruebas.
    raiz_texto = str(raiz.resolve())
    if raiz_texto not in sys.path:
        sys.path.insert(0, raiz_texto)
    from scripts.analizar_precios_serie3 import ventana_enlace
    fechas = pd.to_datetime(crudo.date)
    ohlc_mascara = (
        (crudo.high + 1e-5 < crudo[["open", "low", "close"]].max(axis=1))
        | (crudo.low - 1e-5 > crudo[["open", "high", "close"]].min(axis=1))
    )
    proxy = ventana_enlace(fechas)

    comparables = mensual.loc[mensual.mes_completo_en_archivo].dropna(subset=["usda_cercano_mensual"]).copy()
    parcial = mensual.loc[~mensual.mes_completo_en_archivo].dropna(subset=["usda_cercano_mensual"]).copy()
    comparables["abs_diferencia_pct"] = comparables.diferencia_pct.abs()
    por_mes = mensual.set_index("mes")
    foco = {}
    for ano, meses in {"2000": ["2000-04", "2000-05", "2000-06", "2000-07"],
                       "2008": [f"2008-{m:02d}" for m in range(1, 13)]}.items():
        foco[ano] = [
            {"mes": mes, "cierre_medio": float(por_mes.loc[mes, "cierre_medio"]),
             "usda": float(por_mes.loc[mes, "usda_cercano_mensual"]),
             "diferencia": float(por_mes.loc[mes, "diferencia_centavos"]),
             "diferencia_pct": float(por_mes.loc[mes, "diferencia_pct"])}
            for mes in meses if mes in por_mes.index and pd.notna(por_mes.loc[mes, "usda_cercano_mensual"])
        ]

    mensual.to_csv(salida / "contraste_mensual_usda.csv", index=False)
    mensual[mensual.motivo_fuera_comparacion_principal.ne("")].to_csv(
        salida / "meses_fuera_comparacion_principal.csv", index=False)
    fnb.to_csv(salida / "movimientos_mismo_vencimiento_fnb.csv", index=False)
    insee.to_csv(salida / "divergencia_2003_insee.csv", index=False)
    revision.to_csv(salida / "revision_extremos_2000_2008.csv", index=False)
    decision = {
        "csv_crudo_sha256": sha256(ruta_crudo), "filas_crudas_conservadas": len(crudo),
        "usda_url": URL_USDA, "usda_sha256": sha256(ruta_usda),
        "usda_filas_contraste": len(mensual.dropna(subset=["usda_cercano_mensual"])),
        "usda_meses_completos_contraste": len(comparables),
        "usda_meses_parciales_separados": int(len(parcial)),
        "usda_meses_parciales_detalle": parcial[["mes", "sesiones", "cierre_medio", "usda_cercano_mensual", "diferencia_pct"]].to_dict("records"),
        "usda_mediana_abs_diferencia_pct": float(comparables.abs_diferencia_pct.median()),
        "usda_p90_abs_diferencia_pct": float(comparables.abs_diferencia_pct.quantile(.90)),
        "usda_meses_diferencia_abs_menor_igual_0_0011_centavos": int(comparables.diferencia_centavos.abs().le(.0011).sum()),
        "usda_meses_completos_diferencia_abs_mayor_1_pct": comparables.loc[
            comparables.abs_diferencia_pct.gt(1), ["mes", "cierre_medio", "usda_cercano_mensual", "diferencia_pct"]
        ].to_dict("records"),
        "usda_meses_2000_2008_comprobados": foco,
        "fnb_fechas_mismo_contrato": int(fnb.estado.eq("cotejo_publicado").sum()),
        "fnb_coincidencias_csv_a_centavo": int(fnb.loc[fnb.estado.eq("cotejo_publicado"), "coincide_a_centavo"].sum()),
        "fnb_fechas_republicacion_sospechada": int(fnb.estado.eq("posible_republicacion_obsoleta").sum()),
        "fnb_movimientos_mar11": fnb.loc[fnb.estado.eq("cotejo_publicado"), ["fecha", "horizonte_dias_desde_cotejo_anterior", "referencia", "retorno_contrato_vs_cotejo_pct"]].replace({np.nan: None}).to_dict("records"),
        "insee_2003_contraste": insee[["mes", "cierre_medio", "usda_cercano_mensual", "insee_cercano", "diferencia_csv_centavos", "diferencia_ers_centavos"]].to_dict("records"),
        "ohlc_incoherentes_sin_exclusion": int(ohlc_mascara.sum()),
        "ohlc_incoherentes_dentro_proxy_enlace": int((ohlc_mascara & proxy).sum()),
        "revision_filas_marcadas_sin_exclusion": len(revision),
        "reconstruccion_de_ticker_yahoo_confirmada": False,
        "precios_diarios_oficiales_historicos_gratuitos_completos": False,
        "roll_ajustado_o_corregido": False,
        "conclusion": "La alineación frecuente de niveles mensuales y los cotejos por vencimiento apoyan que el archivo siga el mercado No. 11; INSEE discrepa con USDA ERS en tres meses de 2003 y se aproxima más al CSV. Persisten contratos diarios no identificados, divergencias entre fuentes mensuales y una regla de roll histórica no documentada; no se certifican retornos continuos ni se corrigen saltos.",
    }
    (salida / "decision_continuidad.json").write_text(json.dumps(decision, ensure_ascii=False, indent=2, default=str, allow_nan=False), encoding="utf-8")
    return decision


if __name__ == "__main__":
    print(json.dumps(ejecutar(Path(__file__).resolve().parents[1]), ensure_ascii=False, indent=2, default=str))
