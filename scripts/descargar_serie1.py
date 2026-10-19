"""Descarga el CSV de ensayos varietales desde la fuente oficial USDA/Ag Data Commons."""

from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path


SOURCE_URL = "https://ndownloader.figshare.com/files/49874100"
EXPECTED_SHA256 = "5e7b13de6bda8aed51479c5fdfc3de4a28e71ccbb45e4761b6688a34b7cff4b0"
OUTPUT_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "raw"
    / "louisiana_sugarcane_2010_2021.csv"
)


def main() -> None:
    """Descarga una versión fija y valida su integridad antes de guardarla."""
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    if OUTPUT_PATH.exists():
        current_hash = hashlib.sha256(OUTPUT_PATH.read_bytes()).hexdigest()
        if current_hash == EXPECTED_SHA256:
            print(f"El archivo ya está descargado y verificado: {OUTPUT_PATH}")
            return
        raise SystemExit(
            "El archivo local existe, pero no coincide con la versión USDA esperada. "
            f"Revísalo o renómbralo antes de descargar otra copia: {OUTPUT_PATH}"
        )

    request = urllib.request.Request(
        SOURCE_URL,
        headers={"User-Agent": "PruebaSantaAna/1.0 (reproducible data download)"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read()

    actual_hash = hashlib.sha256(data).hexdigest()
    if actual_hash != EXPECTED_SHA256:
        raise SystemExit(
            "La descarga no coincide con el SHA-256 de la versión documentada. "
            f"Esperado: {EXPECTED_SHA256}; recibido: {actual_hash}. No se guardó el archivo."
        )

    temporary_path = OUTPUT_PATH.with_suffix(".csv.tmp")
    temporary_path.write_bytes(data)
    temporary_path.replace(OUTPUT_PATH)
    print(f"Descarga verificada: {OUTPUT_PATH}")
    print(f"Bytes: {len(data):,}")
    print(f"SHA-256: {actual_hash}")


if __name__ == "__main__":
    main()
