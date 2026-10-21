"""Ejecuta y guarda resultados dentro del notebook 13 desde cualquier carpeta."""
from pathlib import Path

import nbformat
from nbclient import NotebookClient


raiz = Path(__file__).resolve().parents[1]
ruta = raiz / "notebooks/13_eda_faostat_serie3.ipynb"
nb = nbformat.read(ruta, as_version=4)
NotebookClient(nb, timeout=600, kernel_name="prueba-santa-ana",
               resources={"metadata": {"path": str(ruta.parent)}}).execute()
nbformat.write(nb, ruta)
print("Notebook 13 ejecutado y guardado con sus resultados.")
