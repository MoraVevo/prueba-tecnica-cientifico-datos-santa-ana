"""Contraste independiente de selección, contexto y conservación de extremos."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "outputs/revision_termica"


def test_revision_termica_conserva_y_reconstruye_episodios_y_contexto():
    assert (SALIDA / "verificacion.json").exists(), "Ejecutar notebook 11 antes de esta integración."
    d = pd.read_csv(RAIZ / "data/raw/serie2/data.csv", parse_dates=["date"])
    f = pd.read_csv(SALIDA / "decision_por_fila.csv", parse_dates=["date"])
    controles = pd.read_csv(SALIDA / "episodios_revisados.csv", parse_dates=["inicio", "fin_lectura", "fecha_extremo"])
    comparaciones = pd.read_csv(SALIDA / "comparaciones_contexto.csv")
    contexto = pd.read_csv(SALIDA / "contextos_completos.csv", parse_dates=["date"])
    revisadas = pd.read_csv(SALIDA / "filas_revisadas.csv", parse_dates=["date"])
    excluidas = pd.read_csv(SALIDA / "filas_excluidas.csv")
    v = json.loads((SALIDA / "verificacion.json").read_text(encoding="utf-8"))
    assert len(d) == len(f) == v["filas_despues"] == v["filas_antes"] == 86400
    np.testing.assert_array_equal(f.fila_fuente, np.arange(len(d)))
    pd.testing.assert_series_equal(f.date, d.date)
    assert not f.excluir.any() and len(excluidas) == v["filas_excluidas"] == 0
    assert "motivo_exclusion" in excluidas.columns
    temp = d["TE_8332A.AV_0#"].to_numpy()
    distancia = np.round(np.maximum(530-temp, 0)+np.maximum(temp-545, 0), 2)
    np.testing.assert_allclose(f.distancia_banda_C, distancia, rtol=0, atol=1e-12)
    np.testing.assert_array_equal(f.extremo_mayor_5C, distancia > 5)
    fuera = (temp < 530) | (temp > 545)
    # Bordes por diferencias booleanas, sin usar el resumidor del notebook.
    inicios = np.flatnonzero(fuera & ~np.r_[False, fuera[:-1]])
    finales = np.flatnonzero(fuera & ~np.r_[fuera[1:], False])
    elegidos = [(a, b) for a, b in zip(inicios, finales) if distancia[a:b+1].max() > 5]
    esperada = np.zeros(len(d), dtype=int)
    assert len(elegidos) == len(controles) == v["episodios"] == 4
    for numero, (a, b) in enumerate(elegidos, 1):
        esperada[a:b+1] = numero
        r = controles.loc[controles.episodio.eq(numero)].iloc[0]
        assert r.inicio == d.date.iloc[a] and r.fin_lectura == d.date.iloc[b]
        assert r.lecturas_episodio == b-a+1 and r.cobertura_s == (b-a+1)*5
        ie = a+np.argmax(distancia[a:b+1])
        assert r.fecha_extremo == d.date.iloc[ie]
        assert np.isclose(r.temperatura_extremo_C, temp[ie])
        assert np.isclose(r.max_paso_abs_C_5s, np.abs(np.diff(temp)[a-1:b]).max())
        assert r.lecturas_mayor5C == (distancia[a:b+1] > 5).sum()
        muestra = contexto[contexto.episodio.eq(numero)]
        indices = np.flatnonzero(d.date.between(d.date.iloc[a]-pd.Timedelta(minutes=20),
                                              d.date.iloc[b]+pd.Timedelta(minutes=20)))
        np.testing.assert_array_equal(muestra.fila_fuente, indices)
        np.testing.assert_allclose(muestra[d.columns.drop("date")], d.iloc[indices].drop(columns="date"), rtol=0, atol=1e-12)
        assert r.ausencias_contexto_30_sensores == r.infinitos_contexto_30_sensores == 0
        for tag in comparaciones.tag.unique():
            mascaras = {
                "previa10min": d.date.ge(d.date.iloc[a]-pd.Timedelta(minutes=10)) & d.date.lt(d.date.iloc[a]),
                "episodio": d.index.to_series().between(a, b),
                "posterior10min": d.date.gt(d.date.iloc[b]) & d.date.le(d.date.iloc[b]+pd.Timedelta(minutes=10)),
            }
            for fase, mascara in mascaras.items():
                x = d.loc[mascara, tag].to_numpy()
                g = comparaciones[(comparaciones.episodio == numero) & (comparaciones.tag == tag) & (comparaciones.fase == fase)].iloc[0]
                assert g.lecturas == len(x)
                np.testing.assert_allclose([g.mediana, g.minimo, g.maximo], [np.median(x), x.min(), x.max()], rtol=0, atol=1e-10)
    np.testing.assert_array_equal(f.episodio_revision, esperada)
    assert (esperada > 0).sum() == len(revisadas) == v["filas_revisadas"] == 696
    np.testing.assert_array_equal(revisadas.fila_fuente, np.flatnonzero(esperada))
    np.testing.assert_allclose(revisadas[d.columns.drop("date")], d.loc[esperada > 0].drop(columns="date"), rtol=0, atol=1e-12)
    assert not v["exposicion_modelo"]["temperatura_en_quince_finales"]
    for ruta, h in v["huellas_protegidas"].items():
        assert hashlib.sha256((RAIZ/ruta).read_bytes()).hexdigest() == h
