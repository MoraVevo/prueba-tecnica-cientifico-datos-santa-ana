"""Ajusta la campeona de 17 entradas aprobada después del estudio de rezagos."""

import hashlib
import json
from pathlib import Path

import joblib
import pandas as pd

from experimentos.rezagos_serie2 import PRESIONES, construir_rezagos
from scripts.modelado_serie2 import OBJETIVO, crear_modelos


def entrenar(raiz):
    """Congela quince señales actuales y dos presiones a 30 s, sin evaluar día 5."""
    raiz = Path(raiz)
    salida = raiz / "outputs/campeona_serie2"
    salida.mkdir(parents=True, exist_ok=True)
    anterior = raiz / "outputs/serie2_sensor_virtual.joblib"
    huella_anterior = hashlib.sha256(anterior.read_bytes()).hexdigest()
    columnas = joblib.load(anterior)["columnas"]
    assert len(columnas) == 15 and set(PRESIONES).issubset(columnas)
    datos = pd.read_csv(raiz / "data/raw/serie2/data.csv", parse_dates=["date"])
    datos.insert(0, "fila_original", range(len(datos)))
    fase = datos.iloc[::2].set_index("date")
    inicio = datos.date.iloc[0]
    limite = inicio + pd.Timedelta(days=4) - pd.Timedelta(minutes=5)
    mascara = (fase.index >= inicio + pd.Timedelta(seconds=660)) & (fase.index < limite)
    x = pd.concat([fase[columnas], construir_rezagos(fase[list(PRESIONES)], 30)], axis=1)
    modelo = crear_modelos()["Ridge"].fit(x.loc[mascara], fase.loc[mascara, OBJETIVO])
    resumen = pd.read_csv(raiz / "outputs/rezagos/resumen.csv")
    m = resumen.set_index("variante").loc["15 actuales + historia dos presiones"]
    decision = {
        "modelo": "Ridge", "variante": "17 entradas: 15 actuales y dos presiones a 30 s",
        "alpha": 100, "sensores": columnas, "entradas": x.columns.tolist(),
        "rezagos_s": {c: 30 for c in PRESIONES},
        "MAE_validacion": float(m.MAE_medio), "WAPE_validacion_pct": float(m.WAPE_agregado),
        "peor_MAE_validacion": float(m.peor_MAE_diario),
        "validacion_independiente": False, "dia5_evaluado_en_promocion": False,
        "n_ajuste": int(mascara.sum()), "inicio_ajuste": str(fase.index[mascara].min()),
        "fin_ajuste": str(fase.index[mascara].max()),
        "seleccion_actuales": "quince del ajuste original en los primeros cuatro días",
        "criterio": "promoción solicitada por usuario; mejora tres días y parsimonia",
        "huella_referencia15": huella_anterior,
    }
    joblib.dump({"modelo": modelo, "columnas": x.columns.tolist(), "decision": decision},
                salida / "sensor_virtual.joblib")
    (salida / "decision.json").write_text(json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8")
    traza = datos[["fila_original", "date"]].copy()
    traza["papel"] = "fuera_del_ajuste"
    traza["motivo"] = "segunda_fase_de_10s"
    traza.loc[traza.date >= inicio + pd.Timedelta(days=4), "motivo"] = "quinto_dia_no_usado"
    traza.loc[(traza.date >= limite) & (traza.date < inicio + pd.Timedelta(days=4)), "motivo"] = "separacion_5min"
    traza.loc[traza.date < inicio + pd.Timedelta(seconds=660), "motivo"] = "sin_historia_comun_de_660s"
    ids = fase.loc[mascara, "fila_original"]
    traza.loc[traza.fila_original.isin(ids), ["papel", "motivo"]] = ["ajuste", ""]
    traza.to_csv(salida / "papeles_ajuste.csv", index=False)
    fuera = datos.loc[~datos.fila_original.isin(ids)].merge(traza[["fila_original", "motivo"]], on="fila_original")
    fuera.to_csv(salida / "filas_fuera_ajuste.csv", index=False)
    assert hashlib.sha256(anterior.read_bytes()).hexdigest() == huella_anterior
    return decision


if __name__ == "__main__":
    print(json.dumps(entrenar(Path(__file__).resolve().parents[1]), ensure_ascii=False, indent=2))
