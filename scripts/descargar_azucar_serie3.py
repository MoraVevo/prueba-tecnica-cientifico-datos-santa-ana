"""Descarga el CSV de azúcar del dataset Kaggle indicado en la Serie III."""

import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen
from zipfile import ZipFile, is_zipfile

import pandas as pd


DATASET = "guillemservera/agricultural-futures"
ARCHIVO = "individual_data/Sugar_data.csv"
BASE = "https://www.kaggle.com/api/v1/datasets"


def descargar():
    raiz = Path(__file__).resolve().parents[1]
    destino = raiz / "data/raw/serie3"
    destino.mkdir(parents=True, exist_ok=True)
    inventario_url = f"{BASE}/list/{DATASET}"
    with urlopen(inventario_url, timeout=30) as respuesta:
        inventario = json.load(respuesta)
    entrada = next(f for f in inventario["datasetFiles"] if f["name"] == ARCHIVO)
    url = f"{BASE}/download/{DATASET}/{quote(ARCHIVO, safe='')}"
    with urlopen(url, timeout=60) as respuesta:
        contenido = respuesta.read(5_000_001)
    assert len(contenido) <= 5_000_000, "Respuesta mayor que el CSV esperado."
    # Kaggle puede devolver directamente el CSV o un ZIP de un solo archivo.
    if is_zipfile(io.BytesIO(contenido)):
        with ZipFile(io.BytesIO(contenido)) as archivo:
            nombres = [n for n in archivo.namelist() if Path(n).name == "Sugar_data.csv"]
            assert len(nombres) == 1
            contenido = archivo.read(nombres[0])
    assert len(contenido) == entrada["totalBytes"], "Tamaño distinto del inventario público."
    df = pd.read_csv(io.BytesIO(contenido))
    assert {"date", "open", "high", "low", "close", "volume"}.issubset(df.columns), df.columns.tolist()
    fechas = pd.to_datetime(df["date"], utc=True)
    ruta = destino / "Sugar_data.csv"
    if ruta.exists() and ruta.read_bytes() != contenido:
        raise FileExistsError("Ya existe otra versión: conservarla y revisar antes de reemplazar.")
    ruta.write_bytes(contenido)
    procedencia = {
        "dataset": DATASET, "pagina": f"https://www.kaggle.com/datasets/{DATASET}",
        "archivo_en_dataset": ARCHIVO, "url_descarga": url,
        "url_inventario": inventario_url, "fecha_utc": datetime.now(timezone.utc).isoformat(),
        "bytes": len(contenido), "sha256": hashlib.sha256(contenido).hexdigest(),
        "filas": len(df), "columnas": df.columns.tolist(),
        "fecha_min": str(fechas.min()), "fecha_max": str(fechas.max()),
        "fechas_repetidas": int(fechas.duplicated().sum()),
        "faltantes_por_columna": df.isna().sum().to_dict(),
        "orden_fecha_ascendente": bool(fechas.is_monotonic_increasing),
        "filas_volumen_cero": int(df.volume.eq(0).sum()),
        "filas_desigualdad_ohlc": int(((df.high < df[["open", "low", "close"]].max(axis=1)) |
                                        (df.low > df[["open", "high", "close"]].min(axis=1))).sum()),
        "revision": "Estructura y procedencia verificadas; ajustes y continuidad de contratos pendientes.",
    }
    (destino / "fuente_sugar.json").write_text(
        json.dumps(procedencia, ensure_ascii=False, indent=2), encoding="utf-8")
    return procedencia


if __name__ == "__main__":
    print(json.dumps(descargar(), ensure_ascii=True, indent=2))
