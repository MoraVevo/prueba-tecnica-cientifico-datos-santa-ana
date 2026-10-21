"""Lectura estricta de escenarios CSV y JSON de una sola observación."""

from __future__ import annotations

import csv
import io
import json
import math
from typing import Any


class ErrorArchivo(ValueError):
    """El archivo no cumple el contrato de una observación del modelo."""


def leer_escenario(contenido: bytes, tipo: str, nombres_esperados: list[str]) -> dict[str, Any]:
    """Lee un objeto JSON o una fila CSV y conserva los nombres originales."""
    try:
        texto = contenido.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ErrorArchivo("El archivo debe estar codificado en UTF-8.") from exc
    if not texto.strip():
        raise ErrorArchivo("El archivo está vacío.")

    if tipo == "application/json" or tipo.endswith("+json"):
        datos = _leer_json(texto)
    elif tipo in {"text/csv", "application/csv", "application/vnd.ms-excel"}:
        datos = _leer_csv(texto, nombres_esperados)
    else:
        raise ErrorArchivo("Formato no compatible: usa CSV o JSON.")

    if not isinstance(datos, dict):
        raise ErrorArchivo("El archivo debe representar un único objeto con las entradas del modelo.")
    _validar_columnas(datos, nombres_esperados)
    return datos


def _leer_json(texto: str) -> Any:
    def sin_constantes_no_finitas(valor: str) -> None:
        raise ErrorArchivo(f"El JSON contiene el valor no finito {valor}.")

    def sin_claves_duplicadas(pares: list[tuple[str, Any]]) -> dict[str, Any]:
        objeto: dict[str, Any] = {}
        for clave, valor in pares:
            if clave in objeto:
                raise ErrorArchivo(f"El JSON repite la columna {clave}.")
            objeto[clave] = valor
        return objeto

    try:
        return json.loads(
            texto,
            parse_constant=sin_constantes_no_finitas,
            object_pairs_hook=sin_claves_duplicadas,
        )
    except json.JSONDecodeError as exc:
        raise ErrorArchivo(f"El JSON no es válido: {exc.msg}.") from exc


def _leer_csv(texto: str, nombres_esperados: list[str]) -> dict[str, float]:
    try:
        filas = list(csv.reader(io.StringIO(texto, newline=""), strict=True))
    except csv.Error as exc:
        raise ErrorArchivo(f"El CSV no es válido: {exc}.") from exc
    # Ignora líneas físicamente vacías; conserva las filas de celdas vacías para
    # que se rechacen como registros incompletos, no como si no existieran.
    filas = [fila for fila in filas if fila]
    if not filas:
        raise ErrorArchivo("El CSV no contiene encabezados ni datos.")

    encabezados = filas[0]
    _validar_columnas(encabezados, nombres_esperados)
    filas_datos = filas[1:]
    if len(filas_datos) != 1:
        raise ErrorArchivo(
            f"El CSV debe contener exactamente una fila de datos; se encontraron {len(filas_datos)}."
        )
    valores = filas_datos[0]
    if len(valores) != len(encabezados):
        raise ErrorArchivo(
            f"La fila tiene {len(valores)} valores para {len(encabezados)} columnas."
        )

    resultado: dict[str, float] = {}
    for nombre, texto_valor in zip(encabezados, valores):
        try:
            valor = float(texto_valor.strip())
        except ValueError as exc:
            raise ErrorArchivo(f"La columna {nombre} debe contener un número.") from exc
        if not math.isfinite(valor):
            raise ErrorArchivo(f"La columna {nombre} contiene un valor no finito.")
        resultado[nombre] = valor
    return resultado


def _validar_columnas(datos: dict[str, Any] | list[str], nombres_esperados: list[str]) -> None:
    columnas = list(datos)
    if len(set(columnas)) != len(columnas):
        raise ErrorArchivo("El archivo contiene encabezados duplicados.")
    faltantes = [nombre for nombre in nombres_esperados if nombre not in columnas]
    extras = [nombre for nombre in columnas if nombre not in nombres_esperados]
    if faltantes or extras:
        partes = []
        if faltantes:
            partes.append("faltan: " + ", ".join(faltantes))
        if extras:
            partes.append("sobran: " + ", ".join(extras))
        raise ErrorArchivo("Las columnas no coinciden con el contrato; " + "; ".join(partes) + ".")
