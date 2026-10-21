"""Pruebas de contrato de la API del sensor virtual de Serie II."""

import json
import math
import csv
import io

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


def test_app_local_explica_el_modelo_y_ofrece_archivo_y_ejemplo(cliente):
    respuesta = cliente.get("/app")
    assert respuesta.status_code == 200
    assert "text/html" in respuesta.headers["content-type"]
    for texto in (
        "Cargar archivo CSV o JSON",
        "Probar escenario sintético",
        "Descargar plantilla CSV",
        "href=\"/template.csv\"",
        "ZZQBCHLL.AV_0#",
        "/predict/file",
        "no diagnostica fallas",
        "30 segundos",
    ):
        assert texto in respuesta.text


def test_plantilla_csv_http_conserva_los_nombres_originales_incluido_hash(cliente, modelo):
    respuesta = cliente.get("/template.csv")
    assert respuesta.status_code == 200
    assert "text/csv" in respuesta.headers["content-type"]
    assert "attachment" in respuesta.headers["content-disposition"]
    filas = list(csv.reader(io.StringIO(respuesta.text)))
    assert len(filas) == 1
    assert filas[0] == [entrada.nombre for entrada in modelo.entradas]
    assert "PTCA_8322A.AV_0#__pasado_30s" in filas[0]


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


@pytest.mark.parametrize("valor", [None, float("nan"), float("inf"), -float("inf")])
def test_nulos_y_no_finitos_devuelven_422(cliente, payload, valor):
    cuerpo = json.dumps(
        {**payload, "PT_8313C.AV_0#": valor},
        allow_nan=True,
    )
    respuesta = cliente.post(
        "/predict",
        content=cuerpo,
        headers={"Content-Type": "application/json"},
    )
    assert respuesta.status_code == 422


def test_csv_de_una_fila_con_encabezados_originales_reproduce_la_api(cliente, modelo, payload):
    salida = io.StringIO(newline="")
    escritor = csv.writer(salida, lineterminator="\n")
    escritor.writerow([entrada.nombre for entrada in modelo.entradas])
    escritor.writerow([payload[entrada.nombre] for entrada in modelo.entradas])
    archivo = salida.getvalue()

    respuesta_archivo = cliente.post(
        "/predict/file",
        content=archivo,
        headers={"Content-Type": "text/csv; charset=utf-8"},
    )
    respuesta_api = cliente.post("/predict", json=payload)
    assert respuesta_archivo.status_code == 200
    assert respuesta_archivo.json() == respuesta_api.json()


def test_json_de_un_objeto_reproduce_la_api(cliente, payload):
    respuesta = cliente.post(
        "/predict/file",
        json=payload,
        headers={"Content-Type": "application/json"},
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["prediccion"] == pytest.approx(59.33003888712712)


def test_json_archivo_fuera_de_rango_devuelve_422(cliente, modelo, payload):
    limite = modelo.por_nombre["PT_8313C.AV_0#"].maximo_entrenamiento
    respuesta = cliente.post(
        "/predict/file",
        json={**payload, "PT_8313C.AV_0#": limite + 1},
        headers={"Content-Type": "application/json"},
    )
    assert respuesta.status_code == 422
    assert "less than or equal" in str(respuesta.json()["detail"])


def test_archivo_rechaza_csv_con_mas_de_una_fila(cliente, modelo, payload):
    salida = io.StringIO(newline="")
    escritor = csv.writer(salida, lineterminator="\n")
    escritor.writerow([entrada.nombre for entrada in modelo.entradas])
    fila = [payload[entrada.nombre] for entrada in modelo.entradas]
    escritor.writerow(fila)
    escritor.writerow(fila)
    respuesta = cliente.post(
        "/predict/file",
        content=salida.getvalue(),
        headers={"Content-Type": "text/csv"},
    )
    assert respuesta.status_code == 422
    assert "exactamente una fila" in respuesta.json()["detail"]


def test_archivo_no_ignora_una_fila_de_valores_vacios(cliente, modelo, payload):
    salida = io.StringIO(newline="")
    escritor = csv.writer(salida, lineterminator="\n")
    escritor.writerow([entrada.nombre for entrada in modelo.entradas])
    escritor.writerow([payload[entrada.nombre] for entrada in modelo.entradas])
    escritor.writerow([""] * len(modelo.entradas))
    respuesta = cliente.post(
        "/predict/file",
        content=salida.getvalue(),
        headers={"Content-Type": "text/csv"},
    )
    assert respuesta.status_code == 422
    assert "exactamente una fila" in respuesta.json()["detail"]


def test_archivo_rechaza_columnas_ausentes_y_extra(cliente, modelo, payload):
    encabezados = [entrada.nombre for entrada in modelo.entradas]
    fila = [payload[nombre] for nombre in encabezados]
    for nombres, valores in (
        (encabezados[:-1], fila[:-1]),
        (encabezados + ["sensor_extra"], fila + [1.0]),
    ):
        salida = io.StringIO(newline="")
        escritor = csv.writer(salida, lineterminator="\n")
        escritor.writerow(nombres)
        escritor.writerow(valores)
        respuesta = cliente.post(
            "/predict/file",
            content=salida.getvalue(),
            headers={"Content-Type": "text/csv"},
        )
        assert respuesta.status_code == 422
        assert "columnas no coinciden" in respuesta.json()["detail"]


@pytest.mark.parametrize("contenido", [
    '{"PT_8313C.AV_0#": NaN}',
    '{"PT_8313C.AV_0#": Infinity}',
    '{"PT_8313C.AV_0#": -Infinity}',
])
def test_archivo_json_rechaza_valores_no_finitos(cliente, contenido):
    respuesta = cliente.post(
        "/predict/file",
        content=contenido,
        headers={"Content-Type": "application/json"},
    )
    assert respuesta.status_code == 422
    assert "no finito" in respuesta.json()["detail"]


def test_openapi_publica_el_contrato_completo(cliente, modelo):
    respuesta = cliente.get("/openapi.json")
    assert respuesta.status_code == 200
    esquema = respuesta.json()
    assert {"/health", "/model", "/predict", "/predict/file", "/template.csv"}.issubset(esquema["paths"])
    entrada = esquema["components"]["schemas"]["EntradaSensorVirtual"]
    assert entrada["additionalProperties"] is False
    assert set(entrada["required"]) == {item.nombre for item in modelo.entradas}
    assert set(entrada["properties"]) == {item.nombre for item in modelo.entradas}
    for item in modelo.entradas:
        propiedad = entrada["properties"][item.nombre]
        assert propiedad["minimum"] == pytest.approx(item.minimo_entrenamiento)
        assert propiedad["maximum"] == pytest.approx(item.maximo_entrenamiento)
    assert "medianas_del_ajuste" in esquema["paths"]["/predict"]["post"]["requestBody"]["content"]["application/json"]["examples"]
    assert {"text/csv", "application/json"}.issubset(
        esquema["paths"]["/predict/file"]["post"]["requestBody"]["content"]
    )
    esquema_archivo = esquema["paths"]["/predict/file"]["post"]["requestBody"]["content"]["application/json"]["schema"]
    assert set(esquema_archivo["required"]) == {entrada.nombre for entrada in modelo.entradas}
    assert set(esquema_archivo["properties"]) == {entrada.nombre for entrada in modelo.entradas}


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
