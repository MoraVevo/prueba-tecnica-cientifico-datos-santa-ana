"""API REST del sensor virtual de Serie II."""

from __future__ import annotations

import csv
import io
from pathlib import Path

from fastapi import Body, Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import ValidationError

from api.archivos import ErrorArchivo, leer_escenario
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
    salida_csv_ejemplo = io.StringIO(newline="")
    escritor_csv_ejemplo = csv.writer(salida_csv_ejemplo, lineterminator="\n")
    escritor_csv_ejemplo.writerow(entrada.nombre for entrada in modelo.entradas)
    escritor_csv_ejemplo.writerow(entrada.mediana_imputacion for entrada in modelo.entradas)

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

    @aplicacion.exception_handler(RequestValidationError)
    async def responder_validacion(
        solicitud: Request,
        error: RequestValidationError,
    ) -> JSONResponse:
        """Devuelve diagnósticos seguros incluso si el JSON contenía NaN o infinito."""
        errores = [
            {
                "loc": list(item.get("loc", ())),
                "msg": item.get("msg", "Entrada inválida."),
                "type": item.get("type", "value_error"),
            }
            for item in error.errors()
        ]
        return JSONResponse(status_code=422, content={"detail": errores})

    @aplicacion.get(
        "/app",
        include_in_schema=False,
        response_class=FileResponse,
    )
    def interfaz_local() -> FileResponse:
        """Sirve la interfaz local de carga de un escenario preparado."""
        return FileResponse(Path(__file__).with_name("interfaz.html"), media_type="text/html")

    @aplicacion.get(
        "/template.csv",
        response_class=Response,
        tags=["Modelo"],
        summary="Descargar la plantilla CSV de entradas",
        response_description="CSV UTF-8 con los diecisiete encabezados originales y sin valores de ejemplo.",
    )
    def plantilla_csv(
        modelo_cargado: ModeloSensorVirtual = Depends(obtener_modelo),
    ) -> Response:
        """Genera la plantilla directamente desde las entradas del artefacto."""
        salida = io.StringIO(newline="")
        csv.writer(salida, lineterminator="\r\n").writerow(
            entrada.nombre for entrada in modelo_cargado.entradas
        )
        return Response(
            content=salida.getvalue(),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": 'attachment; filename="plantilla_escenario_sensor_virtual.csv"'},
        )

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
        return respuesta_prediccion(entrada, modelo_cargado)

    @aplicacion.post(
        "/predict/file",
        response_model=PrediccionRespuesta,
        tags=["Predicción"],
        summary="Estimar desde un escenario CSV o JSON de una fila",
        response_description="Predicción puntual tras validar el archivo completo.",
        openapi_extra={
            "requestBody": {
                "required": True,
                "content": {
                    "text/csv": {
                        "schema": {"type": "string", "format": "binary"},
                        "examples": {
                            "escenario_sintetico": {
                                "summary": "Medianas del ajuste (escenario sintético)",
                                "description": "No representa una observación real.",
                                "value": salida_csv_ejemplo.getvalue(),
                            }
                        },
                    },
                    "application/json": {
                        "schema": EntradaSensorVirtual.model_json_schema(by_alias=True),
                    },
                },
            }
        },
    )
    async def predecir_archivo(
        solicitud: Request,
        modelo_cargado: ModeloSensorVirtual = Depends(obtener_modelo),
    ) -> PrediccionRespuesta:
        """Recibe un objeto JSON o un CSV con exactamente una fila de datos."""
        contenido = await solicitud.body()
        if len(contenido) > 100_000:
            raise HTTPException(status_code=413, detail="El archivo supera el límite de 100 KB.")
        tipo = solicitud.headers.get("content-type", "").split(";", 1)[0].strip().lower()
        try:
            valores = leer_escenario(
                contenido,
                tipo,
                [entrada.nombre for entrada in modelo_cargado.entradas],
            )
            entrada = EntradaSensorVirtual.model_validate(valores)
        except ErrorArchivo as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except ValidationError as exc:
            detalles = [
                f"{'.'.join(str(parte) for parte in error['loc'])}: {error['msg']}"
                for error in exc.errors()
            ]
            raise HTTPException(status_code=422, detail=detalles) from exc
        return respuesta_prediccion(entrada, modelo_cargado)

    def respuesta_prediccion(
        entrada: EntradaSensorVirtual,
        modelo_cargado: ModeloSensorVirtual,
    ) -> PrediccionRespuesta:
        """Aplica la misma ecuación y respuesta a ambos contratos de entrada."""
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
