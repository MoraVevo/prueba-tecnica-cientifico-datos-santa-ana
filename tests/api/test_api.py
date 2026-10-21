"""Pruebas de contrato de la API del sensor virtual de Serie II."""

import json
import math
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import app, crear_app
from api.modelo import ModeloSensorVirtual


@pytest.fixture(scope="module")
def modelo():
    return ModeloSensorVirtual.cargar()


@pytest.fixture(scope="module")
def cliente():
    with TestClient(app) as prueba:
        yield prueba


@pytest.fixture(scope="module")
def payload(modelo):
    return {entrada.nombre: entrada.mediana_imputacion for entrada in modelo.entradas}


def test_health_responde_con_el_modelo_cargado(cliente, modelo):
    respuesta = cliente.get("/health")
    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "estado": "ok",
        "modelo_cargado": True,
        "version": modelo.version,
    }


def test_ficha_expone_las_diecisiete_entradas_y_sus_limites(cliente, modelo):
    respuesta = cliente.get("/model")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["modelo"] == modelo.modelo
    assert datos["version"] == modelo.version
    assert len(datos["entradas"]) == 17
    assert [entrada["nombre"] for entrada in datos["entradas"]] == [
        entrada.nombre for entrada in modelo.entradas
    ]
    assert datos["objetivo"] not in {entrada["nombre"] for entrada in datos["entradas"]}
    assert datos["entrenamiento"]["n_ajuste"] == 34464
    assert datos["entrenamiento"]["n_faltantes_imputados"] == 15
    assert datos["entrenamiento"]["validacion_independiente"] is False
    assert datos["entrenamiento"]["dia5_evaluado"] is False
    for entrada in datos["entradas"]:
        assert entrada["minimo_entrenamiento"] <= entrada["p01_entrenamiento"]
        assert entrada["p01_entrenamiento"] <= entrada["p99_entrenamiento"]
        assert entrada["p99_entrenamiento"] <= entrada["maximo_entrenamiento"]
    texto = respuesta.text.lower()
    assert "usuario" not in texto
    assert "solicitada" not in texto


def test_prediccion_valida_es_finita_y_reproducible(cliente, modelo, payload):
    primera = cliente.post("/predict", json=payload)
    segunda = cliente.post("/predict", json=payload)
    assert primera.status_code == 200
    assert segunda.status_code == 200
    assert primera.json() == segunda.json()
    datos = primera.json()
    assert math.isfinite(datos["prediccion"])
    assert datos["prediccion"] == pytest.approx(modelo.predecir(payload), abs=1e-12)
    assert datos["modelo"] == modelo.modelo
    assert datos["version"] == modelo.version
    assert datos["objetivo"] == modelo.objetivo
    assert "no certificada" in datos["unidad"]
    assert "consultiva" in datos["advertencia"]


def test_limites_de_entrenamiento_son_aceptados(cliente, modelo):
    minimo = {entrada.nombre: entrada.minimo_entrenamiento for entrada in modelo.entradas}
    maximo = {entrada.nombre: entrada.maximo_entrenamiento for entrada in modelo.entradas}
    for valores in (minimo, maximo):
        respuesta = cliente.post("/predict", json=valores)
        assert respuesta.status_code == 200
        assert math.isfinite(respuesta.json()["prediccion"])


def test_falta_una_entrada_devuelve_422(cliente, payload):
    incompleto = dict(payload)
    incompleto.pop("PT_8313C.AV_0#")
    respuesta = cliente.post("/predict", json=incompleto)
    assert respuesta.status_code == 422
    detalle = respuesta.json()["detail"]
    assert any("PT_8313C.AV_0#" in str(item["loc"]) for item in detalle)


def test_campo_extra_devuelve_422(cliente, payload):
    respuesta = cliente.post("/predict", json={**payload, "entrada_extra": 1.0})
    assert respuesta.status_code == 422
    assert any(item["type"] == "extra_forbidden" for item in respuesta.json()["detail"])


def test_tipo_texto_devuelve_422(cliente, payload):
    respuesta = cliente.post("/predict", json={**payload, "PT_8313C.AV_0#": "-149.67"})
    assert respuesta.status_code == 422


def test_booleano_devuelve_422(cliente, payload):
    respuesta = cliente.post("/predict", json={**payload, "PT_8313C.AV_0#": True})
    assert respuesta.status_code == 422


def test_fuera_de_rango_devuelve_422(cliente, modelo, payload):
    limite = modelo.por_nombre["PT_8313C.AV_0#"].maximo_entrenamiento
    respuesta = cliente.post("/predict", json={**payload, "PT_8313C.AV_0#": limite + 1})
    assert respuesta.status_code == 422
    assert any(item["type"] == "less_than_equal" for item in respuesta.json()["detail"])


def test_openapi_publica_el_contrato_completo(cliente, modelo):
    respuesta = cliente.get("/openapi.json")
    assert respuesta.status_code == 200
    esquema = respuesta.json()
    assert {"/health", "/model", "/predict"}.issubset(esquema["paths"])
    entrada = esquema["components"]["schemas"]["EntradaSensorVirtual"]
    assert entrada["additionalProperties"] is False
    assert set(entrada["required"]) == {item.nombre for item in modelo.entradas}
    assert set(entrada["properties"]) == {item.nombre for item in modelo.entradas}
    for item in modelo.entradas:
        propiedad = entrada["properties"][item.nombre]
        assert propiedad["minimum"] == pytest.approx(item.minimo_entrenamiento)
        assert propiedad["maximum"] == pytest.approx(item.maximo_entrenamiento)
    assert "medianas_del_ajuste" in esquema["paths"]["/predict"]["post"]["requestBody"]["content"]["application/json"]["examples"]


def test_docs_responde(cliente):
    respuesta = cliente.get("/docs")
    assert respuesta.status_code == 200
    assert "swagger" in respuesta.text.lower()


def test_modelo_ausente_falla_al_crear_la_aplicacion(tmp_path):
    with pytest.raises(FileNotFoundError):
        crear_app(tmp_path / "modelo_ausente.json")


def test_modelo_invalido_falla_al_crear_la_aplicacion(tmp_path):
    ruta = tmp_path / "modelo.json"
    ruta.write_text(json.dumps({"schema_version": 1}), encoding="utf-8")
    with pytest.raises(ValueError):
        crear_app(ruta)
