"""Prepara una copia analítica provisional de Serie I sin alterar el CSV original."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "raw" / "louisiana_sugarcane_2010_2021.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_PATH = OUTPUT_DIR / "serie1_etl_provisional.csv"
REPORT_PATH = OUTPUT_DIR / "serie1_resumen_calidad.json"
REVIEW_PATH = OUTPUT_DIR / "serie1_filas_revision.csv"
EXPECTED_SHA256 = "5e7b13de6bda8aed51479c5fdfc3de4a28e71ccbb45e4761b6688a34b7cff4b0"

NUMERIC_COLUMNS = [
    "YEAR", "CROP", "REP", "T_SPACRE", "TCA", "POPN", "MSTWT", "FIBER"
]
KEY_CANDIDATE = ["CLONE", "YEAR", "STAGE", "LOC", "CROP", "REP"]


def main() -> None:
    """Valida la fuente, añade campos tipados y emite banderas de calidad."""
    if not INPUT_PATH.exists():
        raise SystemExit(
            "No se encontró el CSV. Ejecuta primero: "
            "python scripts/descargar_serie1.py"
        )

    source_hash = hashlib.sha256(INPUT_PATH.read_bytes()).hexdigest()
    if source_hash != EXPECTED_SHA256:
        raise SystemExit(
            "El CSV no coincide con la versión auditada. No se procesó. "
            f"Esperado: {EXPECTED_SHA256}; recibido: {source_hash}"
        )

    raw = pd.read_csv(INPUT_PATH, dtype="string", keep_default_na=False)
    prepared = raw.copy()
    prepared.insert(0, "FILA_CSV", range(2, len(raw) + 2))
    parse_error_columns: list[str] = []

    # Preserve the source text beside each parsed numeric field. Blank and '.'
    # become missing values only in the analytical column.
    for column in NUMERIC_COLUMNS:
        source_text = raw[column].astype("string")
        prepared[f"{column}_raw"] = source_text
        cleaned = source_text.str.strip().replace({"": pd.NA, ".": pd.NA})
        parsed = pd.to_numeric(cleaned, errors="coerce")
        error_column = f"ERROR_PARSE_{column}"
        prepared[error_column] = cleaned.notna() & parsed.isna()
        parse_error_columns.append(error_column)
        if column in {"YEAR", "CROP", "REP"}:
            prepared[column] = parsed.astype("Int64")
        else:
            prepared[column] = parsed.astype("Float64")

    # The field has two numeric components in many rows. Keep the original and
    # expose both components; the last one is explicitly provisional.
    trs_text = raw["TRS_TON"].astype("string")
    prepared["TRS_TON_raw"] = trs_text
    parts = trs_text.str.strip().replace({"": pd.NA, ".": pd.NA}).str.extract(
        r"^(?:(?P<prefijo>\d+)\s+)?(?P<componente_final>\d+(?:\.\d+)?)$"
    )
    prepared["TRS_TON_prefijo_sin_interpretar"] = pd.to_numeric(
        parts["prefijo"], errors="coerce"
    ).astype("Float64")
    prepared["TRS_TON_candidato"] = pd.to_numeric(
        parts["componente_final"], errors="coerce"
    ).astype("Float64")
    prepared["TRS_TON_formato"] = "vacio_o_formato_no_reconocido"
    prepared.loc[parts["componente_final"].notna(), "TRS_TON_formato"] = "numero_simple"
    prepared.loc[parts["prefijo"].notna(), "TRS_TON_formato"] = "dos_componentes"
    prepared["ERROR_PARSE_TRS_TON"] = trs_text.str.strip().replace(
        {"": pd.NA, ".": pd.NA}
    ).notna() & parts["componente_final"].isna()
    parse_error_columns.append("ERROR_PARSE_TRS_TON")

    # Preserve the auxiliary fields, including the six loose annotations.
    auxiliary = [column for column in raw.columns if column.startswith("Unnamed:")]
    prepared = prepared.rename(
        columns={column: f"AUX_{index}" for index, column in enumerate(auxiliary, start=1)}
    )

    prepared["DUPLICADO_EXACTO"] = raw.duplicated(keep=False)
    prepared["CLAVE_CANDIDATA_REPETIDA"] = raw.duplicated(
        KEY_CANDIDATE, keep=False
    )

    repeated_key = raw.duplicated(KEY_CANDIDATE, keep=False)
    repeated_key_measurements = (
        raw.loc[repeated_key]
        .groupby(KEY_CANDIDATE, dropna=False)[NUMERIC_COLUMNS + ["TRS_TON"]]
        .nunique(dropna=False)
    )
    repeated_groups_with_different_measurements = int(
        repeated_key_measurements.gt(1).any(axis=1).sum()
    )

    positive = (
        prepared["T_SPACRE"].gt(0)
        & prepared["TCA"].gt(0)
        & prepared["TRS_TON_candidato"].gt(0)
    )
    observed_ratio = prepared.loc[positive, "T_SPACRE"] / (
        prepared.loc[positive, "TCA"] * prepared.loc[positive, "TRS_TON_candidato"]
    )
    within_tolerance = observed_ratio.sub(1).abs().le(0.01)
    prepared["RATIO_T_SPACRE_SOBRE_ESPERADO"] = pd.Series(
        pd.NA, index=prepared.index, dtype="Float64"
    )
    prepared.loc[positive, "RATIO_T_SPACRE_SOBRE_ESPERADO"] = observed_ratio
    prepared["ESTADO_RELACION_DIMENSIONAL"] = "sin_mediciones_completas"
    prepared.loc[observed_ratio.index, "ESTADO_RELACION_DIMENSIONAL"] = "dentro_1_por_ciento"
    prepared.loc[observed_ratio.index[~within_tolerance], "ESTADO_RELACION_DIMENSIONAL"] = "fuera_1_por_ciento"

    parse_errors = prepared[parse_error_columns].any(axis=1)
    formula_outlier = prepared["ESTADO_RELACION_DIMENSIONAL"].eq("fuera_1_por_ciento")
    review_reasons = pd.DataFrame(
        {
            "prefijo_TRS_sin_explicar": prepared["TRS_TON_prefijo_sin_interpretar"].notna(),
            "duplicado_exacto": prepared["DUPLICADO_EXACTO"],
            "clave_candidata_repetida": prepared["CLAVE_CANDIDATA_REPETIDA"],
            "error_de_parseo": parse_errors,
            "fuera_de_tolerancia_dimensional": formula_outlier,
        },
        index=prepared.index,
    )
    prepared["MOTIVOS_REVISION"] = review_reasons.apply(
        lambda row: ";".join(row.index[row].tolist()), axis=1
    )
    needs_review = (
        prepared["TRS_TON_prefijo_sin_interpretar"].notna()
        | prepared["DUPLICADO_EXACTO"]
        | prepared["CLAVE_CANDIDATA_REPETIDA"]
        | parse_errors
        | formula_outlier
    )
    prepared["REQUIERE_REVISION"] = needs_review
    review_rows = prepared.loc[needs_review].copy()

    crop_summary = (
        prepared.groupby("CROP", dropna=False)["T_SPACRE"]
        .agg(n="count", media="mean", mediana="median")
        .reset_index()
        .to_dict(orient="records")
    )
    quality_report = {
        "source_file": INPUT_PATH.name,
        "source_sha256": source_hash,
        "rows": int(len(raw)),
        "source_columns": list(raw.columns),
        "missing_markers": {
            column: {
                "blank": int(raw[column].str.strip().eq("").sum()),
                "dot": int(raw[column].str.strip().eq(".").sum()),
            }
            for column in raw.columns
        },
        "trs_ton_format_counts": {
            str(key): int(value)
            for key, value in prepared["TRS_TON_formato"].value_counts(dropna=False).items()
        },
        "exact_duplicate_rows_including_first_copy": int(
            prepared["DUPLICADO_EXACTO"].sum()
        ),
        "exact_duplicate_extra_copies": int(raw.duplicated(keep="first").sum()),
        "candidate_key_repeated_rows_including_first_copy": int(
            prepared["CLAVE_CANDIDATA_REPETIDA"].sum()
        ),
        "candidate_key_groups_with_different_measurements": repeated_groups_with_different_measurements,
        "numeric_parse_errors": {
            column.removeprefix("ERROR_PARSE_"): int(prepared[column].sum())
            for column in parse_error_columns
        },
        "positive_complete_formula_rows": int(positive.sum()),
        "formula_rows_within_1_percent": int(within_tolerance.sum()),
        "formula_rows_outside_1_percent": int((~within_tolerance).sum()),
        "formula_median_observed_over_expected": float(observed_ratio.median()),
        "rows_requiring_review": int(needs_review.sum()),
        "rows_dropped": 0,
        "crop_t_spacre_summary": crop_summary,
        "decisions": [
            "The raw source fields are preserved in *_raw columns.",
            "Blank and dot markers become missing only in parsed analytical columns.",
            "TRS_TON_candidato is the final numeric component; its prefix is retained without interpretation.",
            "No rows are deleted, imputed, or aggregated.",
            "The three unnamed source columns are retained as AUX_1, AUX_2, AUX_3.",
            "Potentially problematic rows are also written to a separate review file; they remain in the provisional dataset.",
        ],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    prepared.to_csv(OUTPUT_PATH, index=False, na_rep="", encoding="utf-8")
    review_rows.to_csv(REVIEW_PATH, index=False, na_rep="", encoding="utf-8")
    REPORT_PATH.write_text(
        json.dumps(quality_report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"Registros preparados: {len(prepared):,}")
    print(f"TRS_TON por formato: {quality_report['trs_ton_format_counts']}")
    print(
        "Relación dimensional: "
        f"{int(within_tolerance.sum()):,}/{int(positive.sum()):,} dentro del 1 %"
    )
    print(f"CSV provisional: {OUTPUT_PATH.relative_to(PROJECT_ROOT)}")
    print(f"Filas marcadas para revisión: {len(review_rows):,}")
    print(f"CSV de revisión: {REVIEW_PATH.relative_to(PROJECT_ROOT)}")
    print(f"Reporte: {REPORT_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
