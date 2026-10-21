"""Carga y evaluación del modelo exportado del sensor virtual de Serie II."""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


RUTA_MODELO = Path(__file__).resolve().parents[1] / "models" / "serie2_sensor_virtual.json"


@dataclass(frozen=True)
class EntradaModelo:
    """Parámetros de una entrada en el orden del pipeline original."""

    nombre: str
    campo: str
    descripcion: str
    mediana_imputacion: float
    media_escalado: float
    escala: float
    coeficiente_estandarizado: float
    minimo_entrenamiento: float
    maximo_entrenamiento: float
    p01_entrenamiento: float
    p99_entrenamiento: float
    n_faltantes_entrenamiento: int


@dataclass(frozen=True)
class ModeloSensorVirtual:
    """Modelo lineal exportado; no depende de scikit-learn en tiempo de ejecución."""

    schema_version: int
    modelo: str
    version: str
    algoritmo: str
    alpha: float
    objetivo: str
    unidad_objetivo: str
    descripcion: str
    ecuacion: str
    intercepto: float
    entrenamiento: dict[str, Any]
    entradas: tuple[EntradaModelo, ...]
    limitaciones: tuple[str, ...]
    fuente_artefacto: str
    huella_joblib_sha256: str

    @property
    def por_nombre(self) -> dict[str, EntradaModelo]:
        """Devuelve las entradas indexadas por el nombre original del sensor."""
        return {entrada.nombre: entrada for entrada in self.entradas}

    @classmethod
    def cargar(cls, ruta: str | Path = RUTA_MODELO) -> "ModeloSensorVirtual":
        """Lee y valida el contrato JSON antes de exponer el modelo."""
        ruta = Path(ruta)
        if not ruta.exists():
            raise FileNotFoundError(f"No existe el modelo exportado: {ruta}")
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        if datos.get("schema_version") != 1:
            raise ValueError("La versión del esquema del modelo no es compatible.")

        campos_texto = (
            "modelo", "version", "algoritmo", "objetivo", "unidad_objetivo",
            "descripcion", "ecuacion",
        )
        for campo in campos_texto:
            if not isinstance(datos.get(campo), str) or not datos[campo]:
                raise ValueError(f"El campo {campo} del modelo no es válido.")

        try:
            alpha = float(datos.get("alpha"))
            intercepto = float(datos.get("intercepto"))
        except (TypeError, ValueError) as exc:
            raise ValueError("alpha e intercepto deben ser números.") from exc
        if not math.isfinite(alpha) or not math.isfinite(intercepto):
            raise ValueError("alpha e intercepto deben ser finitos.")

        entrenamiento = datos.get("entrenamiento")
        if not isinstance(entrenamiento, dict):
            raise ValueError("Falta el bloque de entrenamiento.")
        for clave in (
            "n_ajuste", "n_faltantes_imputados", "inicio", "fin",
            "validacion_independiente", "dia5_evaluado", "mae_validacion",
            "wape_validacion_pct", "peor_mae_validacion",
        ):
            if clave not in entrenamiento:
                raise ValueError(f"Falta {clave} en el bloque de entrenamiento.")

        entradas_crudas = datos.get("entradas")
        if not isinstance(entradas_crudas, list) or len(entradas_crudas) != 17:
            raise ValueError("El modelo debe contener exactamente 17 entradas.")
        entradas = tuple(cls._leer_entrada(item) for item in entradas_crudas)
        nombres = [entrada.nombre for entrada in entradas]
        if len(set(nombres)) != 17:
            raise ValueError("Las entradas del modelo están repetidas.")
        if datos["objetivo"] in nombres:
            raise ValueError("El objetivo no puede aparecer como entrada.")

        limitaciones = datos.get("limitaciones")
        if not isinstance(limitaciones, list) or not limitaciones or not all(
            isinstance(item, str) and item for item in limitaciones
        ):
            raise ValueError("El modelo debe declarar sus limitaciones.")
        huella = datos.get("huella_joblib_sha256")
        if not isinstance(huella, str) or len(huella) != 64:
            raise ValueError("La huella del artefacto no es válida.")
        fuente = datos.get("fuente_artefacto")
        if not isinstance(fuente, str) or not fuente:
            raise ValueError("Falta la fuente del artefacto.")

        return cls(
            schema_version=1,
            modelo=datos["modelo"],
            version=datos["version"],
            algoritmo=datos["algoritmo"],
            alpha=alpha,
            objetivo=datos["objetivo"],
            unidad_objetivo=datos["unidad_objetivo"],
            descripcion=datos["descripcion"],
            ecuacion=datos["ecuacion"],
            intercepto=intercepto,
            entrenamiento=dict(entrenamiento),
            entradas=entradas,
            limitaciones=tuple(limitaciones),
            fuente_artefacto=fuente,
            huella_joblib_sha256=huella,
        )

    @staticmethod
    def _leer_entrada(item: Any) -> EntradaModelo:
        if not isinstance(item, dict):
            raise ValueError("Cada entrada debe ser un objeto.")
        try:
            entrada = EntradaModelo(
                nombre=str(item["nombre"]),
                campo=str(item["campo"]),
                descripcion=str(item["descripcion"]),
                mediana_imputacion=float(item["mediana_imputacion"]),
                media_escalado=float(item["media_escalado"]),
                escala=float(item["escala"]),
                coeficiente_estandarizado=float(item["coeficiente_estandarizado"]),
                minimo_entrenamiento=float(item["minimo_entrenamiento"]),
                maximo_entrenamiento=float(item["maximo_entrenamiento"]),
                p01_entrenamiento=float(item["p01_entrenamiento"]),
                p99_entrenamiento=float(item["p99_entrenamiento"]),
                n_faltantes_entrenamiento=int(item["n_faltantes_entrenamiento"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Entrada incompleta o inválida: {exc}") from exc
        valores = (
            entrada.mediana_imputacion, entrada.media_escalado, entrada.escala,
            entrada.coeficiente_estandarizado, entrada.minimo_entrenamiento,
            entrada.maximo_entrenamiento, entrada.p01_entrenamiento, entrada.p99_entrenamiento,
        )
        if not all(math.isfinite(valor) for valor in valores):
            raise ValueError(f"La entrada {entrada.nombre} contiene valores no finitos.")
        if not entrada.nombre or not entrada.campo.isidentifier() or not entrada.descripcion:
            raise ValueError("Cada entrada necesita nombre, campo Python y descripción.")
        if entrada.escala <= 0:
            raise ValueError(f"La escala de {entrada.nombre} debe ser positiva.")
        if entrada.minimo_entrenamiento > entrada.maximo_entrenamiento:
            raise ValueError(f"El rango de {entrada.nombre} está invertido.")
        if not (entrada.minimo_entrenamiento <= entrada.p01_entrenamiento <= entrada.p99_entrenamiento <= entrada.maximo_entrenamiento):
            raise ValueError(f"Los percentiles de {entrada.nombre} están fuera del rango.")
        if entrada.n_faltantes_entrenamiento < 0:
            raise ValueError(f"El conteo de faltantes de {entrada.nombre} es negativo.")
        return entrada

    def predecir(self, valores: dict[str, float]) -> float:
        """Aplica la ecuación exportada; el llamador ya validó las 17 entradas."""
        terminos = []
        for entrada in self.entradas:
            if entrada.nombre not in valores:
                raise ValueError(f"Falta la entrada {entrada.nombre}.")
            valor = float(valores[entrada.nombre])
            if not math.isfinite(valor):
                raise ValueError(f"La entrada {entrada.nombre} no es finita.")
            terminos.append(
                entrada.coeficiente_estandarizado
                * ((valor - entrada.media_escalado) / entrada.escala)
            )
        prediccion = math.fsum([self.intercepto, *terminos])
        if not math.isfinite(prediccion):
            raise ValueError("La predicción no es un número finito.")
        return prediccion

    def ficha(self) -> dict[str, Any]:
        """Resume el modelo sin exponer los datos de ajuste."""
        return {
            "schema_version": self.schema_version,
            "modelo": self.modelo,
            "version": self.version,
            "algoritmo": self.algoritmo,
            "alpha": self.alpha,
            "objetivo": self.objetivo,
            "unidad_objetivo": self.unidad_objetivo,
            "descripcion": self.descripcion,
            "ecuacion": self.ecuacion,
            "entrenamiento": dict(self.entrenamiento),
            "entradas": [asdict(entrada) for entrada in self.entradas],
            "limitaciones": list(self.limitaciones),
            "fuente_artefacto": self.fuente_artefacto,
            "huella_joblib_sha256": self.huella_joblib_sha256,
        }
