"""Prepara una copia analítica provisional de la Serie I sin alterar el CSV original."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


RAIZ_PROYECTO = Path(__file__).resolve().parents[1]
RUTA_ENTRADA = RAIZ_PROYECTO / "data" / "raw" / "louisiana_sugarcane_2010_2021.csv"
DIRECTORIO_SALIDA = RAIZ_PROYECTO / "data" / "processed"
RUTA_SALIDA = DIRECTORIO_SALIDA / "serie1_etl_provisional.csv"
RUTA_REPORTE = DIRECTORIO_SALIDA / "serie1_resumen_calidad.json"
RUTA_REVISION = DIRECTORIO_SALIDA / "serie1_filas_revision.csv"
SHA256_ESPERADO = "5e7b13de6bda8aed51479c5fdfc3de4a28e71ccbb45e4761b6688a34b7cff4b0"

COLUMNAS_NUMERICAS = [
    "YEAR", "CROP", "REP", "T_SPACRE", "TCA", "POPN", "MSTWT", "FIBER"
]
CLAVE_CANDIDATA = ["CLONE", "YEAR", "STAGE", "LOC", "CROP", "REP"]


def leer_fuente_validada() -> tuple[pd.DataFrame, str]:
    """Comprueba la versión del archivo y lo carga como texto."""
    if not RUTA_ENTRADA.exists():
        raise SystemExit(
            "No se encontró el CSV. Ejecuta primero: "
            "python scripts/descargar_serie1.py"
        )

    sha256 = hashlib.sha256(RUTA_ENTRADA.read_bytes()).hexdigest()
    if sha256 != SHA256_ESPERADO:
        raise SystemExit(
            "El CSV no coincide con la versión auditada. No se procesó. "
            f"Esperado: {SHA256_ESPERADO}; recibido: {sha256}"
        )

    fuente = pd.read_csv(RUTA_ENTRADA, dtype="string", keep_default_na=False)
    return fuente, sha256


def convertir_mediciones(fuente: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Conserva cada valor original y añade sus columnas analíticas."""
    datos = fuente.copy()
    datos.insert(0, "FILA_CSV", range(2, len(fuente) + 2))
    columnas_error = []

    # Conserva el texto original junto al valor numérico. Los blancos y puntos
    # pasan a ser faltantes solo en la columna analítica.
    for columna in COLUMNAS_NUMERICAS:
        texto = fuente[columna].astype("string")
        datos[f"{columna}_raw"] = texto
        limpio = texto.str.strip().replace({"": pd.NA, ".": pd.NA})
        numero = pd.to_numeric(limpio, errors="coerce")
        columna_error = f"ERROR_PARSE_{columna}"
        datos[columna_error] = limpio.notna() & numero.isna()
        columnas_error.append(columna_error)

        if columna in {"YEAR", "CROP", "REP"}:
            datos[columna] = numero.astype("Int64")
        else:
            datos[columna] = numero.astype("Float64")

    # Algunas celdas de TRS_TON tienen dos números. Se guardan ambos sin
    # interpretar el prefijo; el último se usa solo como candidato provisional.
    texto_trs = fuente["TRS_TON"].astype("string")
    datos["TRS_TON_raw"] = texto_trs
    partes = texto_trs.str.strip().replace({"": pd.NA, ".": pd.NA}).str.extract(
        r"^(?:(?P<prefijo>\d+)\s+)?(?P<componente_final>\d+(?:\.\d+)?)$"
    )
    datos["TRS_TON_prefijo_sin_interpretar"] = pd.to_numeric(
        partes["prefijo"], errors="coerce"
    ).astype("Float64")
    datos["TRS_TON_candidato"] = pd.to_numeric(
        partes["componente_final"], errors="coerce"
    ).astype("Float64")
    datos["TRS_TON_formato"] = "vacio_o_formato_no_reconocido"
    datos.loc[partes["componente_final"].notna(), "TRS_TON_formato"] = "numero_simple"
    datos.loc[partes["prefijo"].notna(), "TRS_TON_formato"] = "dos_componentes"

    limpio_trs = texto_trs.str.strip().replace({"": pd.NA, ".": pd.NA})
    datos["ERROR_PARSE_TRS_TON"] = limpio_trs.notna() & partes["componente_final"].isna()
    columnas_error.append("ERROR_PARSE_TRS_TON")

    # Retiene las columnas auxiliares, incluidas las seis anotaciones sueltas.
    auxiliares = [columna for columna in fuente.columns if columna.startswith("Unnamed:")]
    datos = datos.rename(
        columns={
            columna: f"AUX_{indice}"
            for indice, columna in enumerate(auxiliares, start=1)
        }
    )
    return datos, columnas_error


def marcar_duplicados(fuente: pd.DataFrame, datos: pd.DataFrame) -> int:
    """Marca duplicados y cuenta grupos con mediciones distintas."""
    datos["DUPLICADO_EXACTO"] = fuente.duplicated(keep=False)
    datos["CLAVE_CANDIDATA_REPETIDA"] = fuente.duplicated(
        CLAVE_CANDIDATA, keep=False
    )

    clave_repetida = fuente.duplicated(CLAVE_CANDIDATA, keep=False)
    mediciones_por_clave = (
        fuente.loc[clave_repetida]
        .groupby(CLAVE_CANDIDATA, dropna=False)[COLUMNAS_NUMERICAS + ["TRS_TON"]]
        .nunique(dropna=False)
    )
    grupos_con_mediciones_distintas = int(
        mediciones_por_clave.gt(1).any(axis=1).sum()
    )
    return grupos_con_mediciones_distintas


def evaluar_relacion_dimensional(datos: pd.DataFrame) -> None:
    """Compara el azúcar por acre con TCA por TRS_TON candidato."""
    filas_positivas = (
        datos["T_SPACRE"].gt(0)
        & datos["TCA"].gt(0)
        & datos["TRS_TON_candidato"].gt(0)
    )
    ratio_observado = datos.loc[filas_positivas, "T_SPACRE"] / (
        datos.loc[filas_positivas, "TCA"]
        * datos.loc[filas_positivas, "TRS_TON_candidato"]
    )
    dentro_tolerancia = ratio_observado.sub(1).abs().le(0.01)

    datos["RATIO_T_SPACRE_SOBRE_ESPERADO"] = pd.Series(
        pd.NA, index=datos.index, dtype="Float64"
    )
    datos.loc[filas_positivas, "RATIO_T_SPACRE_SOBRE_ESPERADO"] = ratio_observado
    datos["ESTADO_RELACION_DIMENSIONAL"] = "sin_mediciones_completas"
    datos.loc[ratio_observado.index, "ESTADO_RELACION_DIMENSIONAL"] = (
        "dentro_1_por_ciento"
    )
    datos.loc[ratio_observado.index[~dentro_tolerancia], "ESTADO_RELACION_DIMENSIONAL"] = (
        "fuera_1_por_ciento"
    )


def marcar_revision(datos: pd.DataFrame, columnas_error: list[str]) -> None:
    """Asigna motivos legibles y señala qué filas requieren revisión."""
    errores_parseo = datos[columnas_error].any(axis=1)
    fuera_tolerancia = datos["ESTADO_RELACION_DIMENSIONAL"].eq(
        "fuera_1_por_ciento"
    )
    motivos = pd.DataFrame(
        {
            "prefijo_TRS_sin_explicar": datos[
                "TRS_TON_prefijo_sin_interpretar"
            ].notna(),
            "duplicado_exacto": datos["DUPLICADO_EXACTO"],
            "clave_candidata_repetida": datos["CLAVE_CANDIDATA_REPETIDA"],
            "error_de_parseo": errores_parseo,
            "fuera_de_tolerancia_dimensional": fuera_tolerancia,
        },
        index=datos.index,
    )
    datos["MOTIVOS_REVISION"] = motivos.apply(
        lambda fila: ";".join(fila.index[fila]), axis=1
    )
    datos["REQUIERE_REVISION"] = (
        datos["TRS_TON_prefijo_sin_interpretar"].notna()
        | datos["DUPLICADO_EXACTO"]
        | datos["CLAVE_CANDIDATA_REPETIDA"]
        | errores_parseo
        | fuera_tolerancia
    )


def resumir_calidad(
    fuente: pd.DataFrame,
    datos: pd.DataFrame,
    sha256: str,
    columnas_error: list[str],
    grupos_con_mediciones_distintas: int,
) -> dict:
    """Resume la calidad de la fuente y las decisiones aplicadas."""
    filas_completas = datos["ESTADO_RELACION_DIMENSIONAL"].ne(
        "sin_mediciones_completas"
    )
    filas_dentro = datos["ESTADO_RELACION_DIMENSIONAL"].eq("dentro_1_por_ciento")
    ratios = datos["RATIO_T_SPACRE_SOBRE_ESPERADO"].dropna()
    resumen_cosecha = (
        datos.groupby("CROP", dropna=False)["T_SPACRE"]
        .agg(n="count", media="mean", mediana="median")
        .reset_index()
        .to_dict(orient="records")
    )

    return {
        "archivo_fuente": RUTA_ENTRADA.name,
        "sha256_fuente": sha256,
        "total_filas": int(len(fuente)),
        "columnas_fuente": list(fuente.columns),
        "marcadores_faltantes": {
            columna: {
                "en_blanco": int(fuente[columna].str.strip().eq("").sum()),
                "punto": int(fuente[columna].str.strip().eq(".").sum()),
            }
            for columna in fuente.columns
        },
        "conteo_formato_trs_ton": {
            str(clave): int(valor)
            for clave, valor in datos["TRS_TON_formato"].value_counts(
                dropna=False
            ).items()
        },
        "filas_duplicadas_exactas_incluida_primera": int(
            datos["DUPLICADO_EXACTO"].sum()
        ),
        "copias_duplicadas_adicionales": int(fuente.duplicated(keep="first").sum()),
        "filas_con_clave_candidata_repetida": int(
            datos["CLAVE_CANDIDATA_REPETIDA"].sum()
        ),
        "grupos_con_mediciones_distintas": grupos_con_mediciones_distintas,
        "errores_parseo_numerico": {
            columna.removeprefix("ERROR_PARSE_"): int(datos[columna].sum())
            for columna in columnas_error
        },
        "filas_completas_positivas": int(filas_completas.sum()),
        "filas_dentro_del_1_por_ciento": int(filas_dentro.sum()),
        "filas_fuera_del_1_por_ciento": int((filas_completas & ~filas_dentro).sum()),
        "mediana_ratio_observado_esperado": float(ratios.median()),
        "filas_marcadas_para_revision": int(datos["REQUIERE_REVISION"].sum()),
        "filas_descartadas": 0,
        "resumen_t_spacre_por_cosecha": resumen_cosecha,
        "decisiones": [
            "Los campos originales se conservan en columnas terminadas en _raw.",
            "Blancos y puntos se convierten en faltantes solo en columnas analíticas.",
            "TRS_TON_candidato usa el último componente numérico; conserva el prefijo sin interpretarlo.",
            "No se eliminan, imputan ni agregan filas.",
            "Las tres columnas sin nombre se conservan como AUX_1, AUX_2 y AUX_3.",
            "Las filas con alertas se copian a un archivo de revisión y permanecen en el dataset provisional.",
        ],
    }


def guardar_resultados(datos: pd.DataFrame, resumen: dict) -> None:
    """Guarda la tabla provisional, el subconjunto de revisión y el reporte."""
    DIRECTORIO_SALIDA.mkdir(parents=True, exist_ok=True)
    filas_revision = datos.loc[datos["REQUIERE_REVISION"]].copy()
    datos.to_csv(RUTA_SALIDA, index=False, na_rep="", encoding="utf-8")
    filas_revision.to_csv(RUTA_REVISION, index=False, na_rep="", encoding="utf-8")
    RUTA_REPORTE.write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main() -> None:
    """Ejecuta el ETL en pasos breves y ordenados."""
    fuente, sha256 = leer_fuente_validada()
    datos, columnas_error = convertir_mediciones(fuente)
    grupos_distintos = marcar_duplicados(fuente, datos)
    evaluar_relacion_dimensional(datos)
    marcar_revision(datos, columnas_error)
    resumen = resumir_calidad(
        fuente, datos, sha256, columnas_error, grupos_distintos
    )
    guardar_resultados(datos, resumen)

    print(f"Registros preparados: {len(datos):,}")
    print(f"TRS_TON por formato: {resumen['conteo_formato_trs_ton']}")
    print(
        "Relación dimensional: "
        f"{resumen['filas_dentro_del_1_por_ciento']:,}/"
        f"{resumen['filas_completas_positivas']:,} dentro del 1 %"
    )
    print(f"CSV provisional: {RUTA_SALIDA.relative_to(RAIZ_PROYECTO)}")
    print(f"Filas marcadas para revisión: {resumen['filas_marcadas_para_revision']:,}")
    print(f"CSV de revisión: {RUTA_REVISION.relative_to(RAIZ_PROYECTO)}")
    print(f"Reporte: {RUTA_REPORTE.relative_to(RAIZ_PROYECTO)}")


if __name__ == "__main__":
    main()
