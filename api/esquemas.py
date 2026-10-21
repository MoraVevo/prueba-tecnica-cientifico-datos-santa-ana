"""Contratos Pydantic de la API del sensor virtual."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from api.modelo import ModeloSensorVirtual


MODELO = ModeloSensorVirtual.cargar()


def campo(nombre: str) -> Any:
    """Construye un campo obligatorio con alias, rango y descripción del JSON."""
    entrada = MODELO.por_nombre[nombre]
    return Field(
        ...,
        alias=entrada.nombre,
        title=entrada.nombre,
        ge=entrada.minimo_entrenamiento,
        le=entrada.maximo_entrenamiento,
        description=entrada.descripcion,
    )


class EntradaSensorVirtual(BaseModel):
    """Las 17 columnas ya preparadas que recibe el pipeline de Ridge."""

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    presion_8313c: float = campo("PT_8313C.AV_0#")
    presion_8313d: float = campo("PT_8313D.AV_0#")
    presion_8313f: float = campo("PT_8313F.AV_0#")
    presion_ptca_8322a: float = campo("PTCA_8322A.AV_0#")
    presion_ptca_8324: float = campo("PTCA_8324.AV_0#")
    temperatura_8313b: float = campo("TE_8313B.AV_0#")
    temperatura_8304: float = campo("TE_8304.AV_0#")
    valvula_8329zc: float = campo("TV_8329ZC.AV_0#")
    flujo_aire_8302: float = campo("FT_8302.AV_0#")
    oxigeno_8301a: float = campo("AIR_8301A.AV_0#")
    oxigeno_8301b: float = campo("AIR_8301B.AV_0#")
    corriente_yfj3_ai: float = campo("YFJ3_AI.AV_0#")
    diferencial_sxltcyy: float = campo("SXLTCYY.AV_0#")
    diferencial_zclccy: float = campo("ZCLCCY.AV_0#")
    agua_yjjwsll: float = campo("YJJWSLL.AV_0#")
    presion_ptca_8322a_30s: float = campo("PTCA_8322A.AV_0#__pasado_30s")
    presion_ptca_8324_30s: float = campo("PTCA_8324.AV_0#__pasado_30s")

    @field_validator("*", mode="before")
    @classmethod
    def rechazar_texto_y_booleanos(cls, valor: Any) -> Any:
        """Acepta números JSON; rechaza cadenas y booleanos antes de convertirlos."""
        if isinstance(valor, (str, bool)):
            raise ValueError("debe ser un número")
        return valor


class SaludRespuesta(BaseModel):
    """Respuesta mínima para el healthcheck del contenedor."""

    estado: str
    modelo_cargado: bool
    version: str


class EntrenamientoFicha(BaseModel):
    """Procedencia y métricas históricas del ajuste."""

    n_ajuste: int
    n_faltantes_imputados: int
    inicio: str
    fin: str
    validacion_independiente: bool
    dia5_evaluado: bool
    mae_validacion: float
    wape_validacion_pct: float
    peor_mae_validacion: float


class EntradaFicha(BaseModel):
    """Parámetros publicados de cada entrada."""

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


class ModeloRespuesta(BaseModel):
    """Ficha del modelo para clientes y para la documentación OpenAPI."""

    schema_version: int
    modelo: str
    version: str
    algoritmo: str
    alpha: float
    objetivo: str
    unidad_objetivo: str
    descripcion: str
    ecuacion: str
    entrenamiento: EntrenamientoFicha
    entradas: list[EntradaFicha]
    limitaciones: list[str]
    fuente_artefacto: str
    huella_joblib_sha256: str


class PrediccionRespuesta(BaseModel):
    """Resultado de una estimación puntual; no incluye intervalos no validados."""

    prediccion: float = Field(description="Estimación en la escala nativa del objetivo.")
    modelo: str
    version: str
    objetivo: str
    unidad: str
    advertencia: str
