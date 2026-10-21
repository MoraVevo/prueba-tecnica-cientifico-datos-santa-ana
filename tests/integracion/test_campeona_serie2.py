"""Verifica ajuste final de la campeona vigente con ecuación independiente."""
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


def test_campeona17_solo_pasado_y_prediccion_reconstruida():
    raiz = Path(__file__).resolve().parents[2]
    salida = raiz / "outputs/campeona_serie2"
    guardado = joblib.load(salida / "sensor_virtual.joblib")
    d = json.loads((salida / "decision.json").read_text(encoding="utf-8"))
    crudo = pd.read_csv(raiz / "data/raw/serie2/data.csv", parse_dates=["date"])
    datos = crudo.iloc[::2].set_index("date")
    inicio = crudo.date.iloc[0]
    mascara = ((datos.index >= inicio + pd.Timedelta(seconds=660)) &
               (datos.index < inicio + pd.Timedelta(days=4) - pd.Timedelta(minutes=5)))
    actual = datos.loc[mascara, d["sensores"]]
    a = actual.to_numpy()
    for c in d["rezagos_s"]:
        anterior = datos[c].reindex(actual.index - pd.Timedelta(seconds=30)).to_numpy()
        a = np.column_stack([a, anterior])
    a = np.where(np.isnan(a), np.nanmedian(a, axis=0), a)
    media, escala = a.mean(axis=0), a.std(axis=0)
    z = (a - media) / escala
    y = datos.loc[mascara, "ZZQBCHLL.AV_0#"].to_numpy()
    coef = np.linalg.solve(z.T @ z + 100 * np.eye(17), z.T @ (y - y.mean()))
    modelo = guardado["modelo"]
    np.testing.assert_allclose(modelo[-1].coef_, coef, atol=1e-9)
    matriz = pd.DataFrame(a, index=actual.index, columns=guardado["columnas"])
    np.testing.assert_allclose(modelo.predict(matriz.iloc[:100]), y.mean() + z[:100] @ coef, atol=1e-9)
    assert len(d["entradas"]) == 17 and d["n_ajuste"] == mascara.sum() == 34464
    assert not d["dia5_evaluado_en_promocion"]
    traza = pd.read_csv(salida / "papeles_ajuste.csv")
    fuera = pd.read_csv(salida / "filas_fuera_ajuste.csv")
    ids = traza.loc[traza.papel == "ajuste", "fila_original"]
    assert len(ids) + len(fuera) == len(crudo)
    assert not set(ids).intersection(fuera.fila_original)
    pd.testing.assert_frame_equal(crudo.iloc[fuera.fila_original].reset_index(drop=True),
                                  fuera[crudo.columns].assign(date=lambda f: pd.to_datetime(f.date)))
    assert fuera.motivo.notna().all()
