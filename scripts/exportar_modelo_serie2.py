"""Exporta la campeona de Serie II a un contrato JSON pequeño y verificable.

El artefacto de la API no contiene datos crudos ni un objeto pickle. Conserva
los parámetros necesarios para reproducir la ecuación de Ridge y los límites
observados en el ajuste, de modo que el contenedor no necesite scikit-learn.
"""

import hashlib
import json
import math
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from experimentos.rezagos_serie2 import PRESIONES, construir_rezagos
from scripts.modelado_serie2 import OBJETIVO


DESCRIPCIONES = {
    "PT_8313C.AV_0#": "Presión en la zona de combustión; unidad no certificada.",
    "PT_8313D.AV_0#": "Presión en la zona de combustión; unidad no certificada.",
    "PT_8313F.AV_0#": "Presión en la zona de combustión; unidad no certificada.",
    "PTCA_8322A.AV_0#": "Presión del circuito de agua/vapor; unidad no certificada.",
    "PTCA_8324.AV_0#": "Presión del circuito de agua/vapor; unidad no certificada.",
    "TE_8313B.AV_0#": "Temperatura de gases/hogar; unidad no certificada.",
    "TE_8304.AV_0#": "Temperatura de aire; unidad no certificada.",
    "TV_8329ZC.AV_0#": "Señal de válvula de atemperación; unidad no certificada.",
    "FT_8302.AV_0#": "Flujo de aire secundario; unidad no certificada.",
    "AIR_8301A.AV_0#": "Oxígeno en gases, lado A; unidad no certificada.",
    "AIR_8301B.AV_0#": "Oxígeno en gases, lado B; unidad no certificada.",
    "YFJ3_AI.AV_0#": "Corriente del ventilador de tiro inducido; unidad no certificada.",
    "SXLTCYY.AV_0#": "Presión diferencial; unidad no certificada.",
    "ZCLCCY.AV_0#": "Presión diferencial; unidad no certificada.",
    "YJJWSLL.AV_0#": "Señal de agua de atemperación; unidad no certificada.",
    "PTCA_8322A.AV_0#__pasado_30s": "Presión PTCA_8322A treinta segundos antes; unidad no certificada.",
    "PTCA_8324.AV_0#__pasado_30s": "Presión PTCA_8324 treinta segundos antes; unidad no certificada.",
}

CAMPOS = {
    "PT_8313C.AV_0#": "presion_8313c",
    "PT_8313D.AV_0#": "presion_8313d",
    "PT_8313F.AV_0#": "presion_8313f",
    "PTCA_8322A.AV_0#": "presion_ptca_8322a",
    "PTCA_8324.AV_0#": "presion_ptca_8324",
    "TE_8313B.AV_0#": "temperatura_8313b",
    "TE_8304.AV_0#": "temperatura_8304",
    "TV_8329ZC.AV_0#": "valvula_8329zc",
    "FT_8302.AV_0#": "flujo_aire_8302",
    "AIR_8301A.AV_0#": "oxigeno_8301a",
    "AIR_8301B.AV_0#": "oxigeno_8301b",
    "YFJ3_AI.AV_0#": "corriente_yfj3_ai",
    "SXLTCYY.AV_0#": "diferencial_sxltcyy",
    "ZCLCCY.AV_0#": "diferencial_zclccy",
    "YJJWSLL.AV_0#": "agua_yjjwsll",
    "PTCA_8322A.AV_0#__pasado_30s": "presion_ptca_8322a_30s",
    "PTCA_8324.AV_0#__pasado_30s": "presion_ptca_8324_30s",
}

LIMITACIONES = [
    "La validación es histórica y reutilizada; no es un test independiente.",
    "El quinto día no se evaluó durante la promoción de esta versión.",
    "La unidad del caudal objetivo y de las entradas no está certificada.",
    "El linaje del caudal compensado y las latencias instrumentales no están confirmados.",
    "El modelo no garantiza funcionamiento ante una falla del caudalímetro ni independencia instrumental.",
    "Los rangos de entrada son empíricos y no límites de seguridad o de instrumentación.",
    "La salida es una estimación consultiva; no debe usarse para control automático.",
    "No se calculan intervalos de incertidumbre.",
]


def _cargar_guardado(raiz):
    ruta = Path(raiz) / "outputs/campeona_serie2/sensor_virtual.joblib"
    if not ruta.exists():
        raise FileNotFoundError(
            f"No existe {ruta}. Ejecutar el notebook 12 o scripts.entrenar_campeona_serie2."
        )
    guardado = joblib.load(ruta)
    if not {"modelo", "columnas", "decision"}.issubset(guardado):
        raise ValueError("El artefacto no contiene modelo, columnas y decisión.")
    return guardado, ruta


def _preparar_entrenamiento(raiz, guardado):
    ruta_datos = Path(raiz) / "data/raw/serie2/data.csv"
    if not ruta_datos.exists():
        raise FileNotFoundError(f"No existe {ruta_datos}.")
    datos = pd.read_csv(ruta_datos, parse_dates=["date"])
    fase = datos.iloc[::2].set_index("date")
    inicio = datos.date.iloc[0]
    limite = inicio + pd.Timedelta(days=4) - pd.Timedelta(minutes=5)
    mascara = (fase.index >= inicio + pd.Timedelta(seconds=660)) & (fase.index < limite)

    columnas = list(guardado["columnas"])
    actuales = [c for c in columnas if not c.endswith("__pasado_30s")]
    anteriores = [c for c in columnas if c.endswith("__pasado_30s")]
    if len(columnas) != 17 or len(actuales) != 15 or len(anteriores) != 2:
        raise ValueError("El artefacto no tiene las 15 señales actuales y dos rezagos esperados.")
    if set(anteriores) != {f"{c}__pasado_30s" for c in PRESIONES}:
        raise ValueError("Los rezagos del artefacto no corresponden a las dos presiones documentadas.")

    x = pd.concat([fase[actuales], construir_rezagos(fase[list(PRESIONES)], 30)], axis=1)
    if x.columns.tolist() != columnas:
        raise ValueError("El orden de columnas reconstruido no coincide con el artefacto.")
    x = x.loc[mascara]
    y = fase.loc[mascara, OBJETIVO]
    if len(x) != guardado["decision"]["n_ajuste"]:
        raise ValueError("El número de filas de ajuste no coincide con la decisión guardada.")
    if y.isna().any():
        raise ValueError("El objetivo del ajuste contiene faltantes inesperados.")
    if OBJETIVO in x.columns:
        raise ValueError("El objetivo no puede ser una entrada del modelo.")
    return x, y, guardado["decision"]


def _extraer_parametros(modelo):
    pasos = getattr(modelo, "named_steps", {})
    if not {"simpleimputer", "standardscaler", "ridge"}.issubset(pasos):
        raise ValueError("El pipeline no tiene imputador, escalador y Ridge.")
    imputador = pasos["simpleimputer"]
    escalador = pasos["standardscaler"]
    ridge = pasos["ridge"]
    mediana = np.asarray(imputador.statistics_, dtype=float)
    media = np.asarray(escalador.mean_, dtype=float)
    escala = np.asarray(escalador.scale_, dtype=float)
    coeficientes = np.asarray(ridge.coef_, dtype=float)
    intercepto = float(ridge.intercept_)
    if not all(len(a) == 17 for a in (mediana, media, escala, coeficientes)):
        raise ValueError("Los parámetros del pipeline no tienen 17 posiciones.")
    if not all(np.isfinite(a).all() for a in (mediana, media, escala, coeficientes)):
        raise ValueError("Los parámetros del pipeline contienen valores no finitos.")
    if (escala <= 0).any():
        raise ValueError("La escala estandarizada debe ser positiva.")
    if not math.isfinite(intercepto):
        raise ValueError("El intercepto no es finito.")
    return mediana, media, escala, coeficientes, intercepto


def _verificar_ecuacion(x, mediana, media, escala, coeficientes, intercepto, modelo):
    matriz = x.to_numpy(dtype=float)
    matriz = np.where(np.isnan(matriz), mediana, matriz)
    z = (matriz - media) / escala
    reconstruida = intercepto + z @ coeficientes
    observada = np.asarray(modelo.predict(x), dtype=float)
    np.testing.assert_allclose(observada, reconstruida, rtol=0, atol=1e-9)


def construir_especificacion(raiz):
    """Construye el JSON reproducible a partir del joblib y del ajuste original."""
    raiz = Path(raiz)
    guardado, ruta_joblib = _cargar_guardado(raiz)
    x, _, decision = _preparar_entrenamiento(raiz, guardado)
    mediana, media, escala, coeficientes, intercepto = _extraer_parametros(guardado["modelo"])
    _verificar_ecuacion(x, mediana, media, escala, coeficientes, intercepto, guardado["modelo"])

    entradas = []
    for i, nombre in enumerate(x.columns):
        if nombre not in DESCRIPCIONES or nombre not in CAMPOS:
            raise ValueError(f"Falta la descripción o el nombre de campo para {nombre}.")
        valores = x[nombre]
        entradas.append(
            {
                "nombre": nombre,
                "campo": CAMPOS[nombre],
                "descripcion": DESCRIPCIONES[nombre],
                "mediana_imputacion": float(mediana[i]),
                "media_escalado": float(media[i]),
                "escala": float(escala[i]),
                "coeficiente_estandarizado": float(coeficientes[i]),
                "minimo_entrenamiento": float(valores.min()),
                "maximo_entrenamiento": float(valores.max()),
                "p01_entrenamiento": float(valores.quantile(0.01)),
                "p99_entrenamiento": float(valores.quantile(0.99)),
                "n_faltantes_entrenamiento": int(valores.isna().sum()),
            }
        )

    especificacion = {
        "schema_version": 1,
        "modelo": "serie2_sensor_virtual_ridge_17",
        "version": "1.0.0",
        "algoritmo": "Ridge",
        "alpha": float(guardado["modelo"].named_steps["ridge"].alpha),
        "objetivo": OBJETIVO,
        "unidad_objetivo": "unidad nativa de ZZQBCHLL.AV_0# (no certificada)",
        "descripcion": (
            "Sensor virtual Ridge para estimar el caudal de vapor principal "
            "ZZQBCHLL.AV_0# a partir de 17 señales de proceso. La API recibe las "
            "17 columnas ya preparadas, incluidas dos presiones treinta segundos antes."
        ),
        "ecuacion": (
            "prediccion = intercepto + suma(coeficiente_estandarizado * "
            "(x - media_escalado) / escala)"
        ),
        "intercepto": intercepto,
        "entrenamiento": {
            "n_ajuste": int(decision["n_ajuste"]),
            "n_faltantes_imputados": int(x.isna().sum().sum()),
            "inicio": str(decision["inicio_ajuste"]),
            "fin": str(decision["fin_ajuste"]),
            "validacion_independiente": bool(decision["validacion_independiente"]),
            "dia5_evaluado": bool(decision["dia5_evaluado_en_promocion"]),
            "mae_validacion": float(decision["MAE_validacion"]),
            "wape_validacion_pct": float(decision["WAPE_validacion_pct"]),
            "peor_mae_validacion": float(decision["peor_MAE_validacion"]),
        },
        "entradas": entradas,
        "limitaciones": LIMITACIONES,
        "fuente_artefacto": "outputs/campeona_serie2/sensor_virtual.joblib",
        "huella_joblib_sha256": hashlib.sha256(ruta_joblib.read_bytes()).hexdigest(),
    }

    if len(especificacion["entradas"]) != 17:
        raise ValueError("La especificación debe contener exactamente 17 entradas.")
    texto = json.dumps(especificacion, ensure_ascii=False, allow_nan=False)
    for prohibida in ("usuario", "solicitada", "promoción solicitada"):
        if prohibida in texto.lower():
            raise ValueError(f"El JSON contiene lenguaje de proceso no permitido: {prohibida}.")
    return especificacion


def main():
    raiz = Path(__file__).resolve().parents[1]
    especificacion = construir_especificacion(raiz)
    ruta = raiz / "models/serie2_sensor_virtual.json"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(
        json.dumps(especificacion, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(f"Modelo exportado en {ruta}")
    print(f"Entradas: {len(especificacion['entradas'])}; ajuste: {especificacion['entrenamiento']['n_ajuste']} filas")


if __name__ == "__main__":
    main()
