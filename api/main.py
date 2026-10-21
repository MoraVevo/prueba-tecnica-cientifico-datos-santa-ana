"""API REST del sensor virtual de Serie II."""

from __future__ import annotations

from pathlib import Path

from fastapi import Body, Depends, FastAPI, HTTPException, Request

from api.esquemas import (
    EntradaSensorVirtual,
    ModeloRespuesta,
    PrediccionRespuesta,
    SaludRespuesta,
)
from api.modelo import ModeloSensorVirtual, RUTA_MODELO


ADVERTENCIA = (
    "Estimación histórica consultiva; no certifica unidad, independencia "
    "instrumental ni uso para control automático."
)


def obtener_modelo(request: Request) -> ModeloSensorVirtual:
    """Recupera la instancia cargada al crear la aplicación."""
    return request.app.state.modelo


def crear_app(ruta_modelo: str | Path | None = None) -> FastAPI:
    """Crea la aplicación y falla al arrancar si el modelo no es válido."""
    modelo = ModeloSensorVirtual.cargar(ruta_modelo or RUTA_MODELO)
    ejemplo = {entrada.nombre: entrada.mediana_imputacion for entrada in modelo.entradas}

    aplicacion = FastAPI(
        title="Sensor virtual de Serie II",
        version=modelo.version,
        description=(
            "API de demostración para estimar el caudal de vapor principal "
            "`ZZQBCHLL.AV_0#` con el modelo Ridge de diecisiete entradas de "
            "Serie II. La API recibe las diecisiete columnas ya preparadas, "
            "incluidas las dos presiones treinta segundos antes. No certifica "
            "unidades, independencia instrumental ni uso en control."
        ),
        openapi_tags=[
            {"name": "Salud", "description": "Estado del servicio."},
            {"name": "Modelo", "description": "Ficha, procedencia y límites."},
            {"name": "Predicción", "description": "Estimación puntual del caudal."},
        ],
    )
    aplicacion.state.modelo = modelo

    @aplicacion.get(
        "/health",
        response_model=SaludRespuesta,
        tags=["Salud"],
        summary="Comprobar el servicio",
        response_description="Estado del modelo cargado.",
    )
    def salud(modelo_cargado: ModeloSensorVirtual = Depends(obtener_modelo)) -> SaludRespuesta:
        return SaludRespuesta(
            estado="ok",
            modelo_cargado=True,
            version=modelo_cargado.version,
        )

    @aplicacion.get(
        "/model",
        response_model=ModeloRespuesta,
        tags=["Modelo"],
        summary="Consultar la ficha del modelo",
        response_description="Procedencia, entradas, métricas y limitaciones.",
    )
    def ficha(modelo_cargado: ModeloSensorVirtual = Depends(obtener_modelo)) -> ModeloRespuesta:
        return ModeloRespuesta(**modelo_cargado.ficha())

    @aplicacion.post(
        "/predict",
        response_model=PrediccionRespuesta,
        tags=["Predicción"],
        summary="Estimar el caudal de vapor",
        response_description="Predicción puntual en la escala nativa del objetivo.",
    )
    def predecir(
        entrada: EntradaSensorVirtual = Body(
            ...,
            openapi_examples={
                "medianas_del_ajuste": {
                    "summary": "Medianas del ajuste",
                    "description": "Valores centrales de las diecisiete entradas.",
                    "value": ejemplo,
                }
            },
        ),
        modelo_cargado: ModeloSensorVirtual = Depends(obtener_modelo),
    ) -> PrediccionRespuesta:
        try:
            prediccion = modelo_cargado.predecir(entrada.model_dump(by_alias=True))
        except ValueError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        return PrediccionRespuesta(
            prediccion=prediccion,
            modelo=modelo_cargado.modelo,
            version=modelo_cargado.version,
            objetivo=modelo_cargado.objetivo,
            unidad=modelo_cargado.unidad_objetivo,
            advertencia=ADVERTENCIA,
        )

    return aplicacion


app = crear_app()
