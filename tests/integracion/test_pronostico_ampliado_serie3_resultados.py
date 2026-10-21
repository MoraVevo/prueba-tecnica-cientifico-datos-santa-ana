"""Contrastes desde crudos, matrices y predicciones guardadas, sin helpers."""

import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


RAIZ = Path(__file__).resolve().parents[2]
OUT = RAIZ/"outputs/serie3_pronostico_ampliado"


def test_conservacion_y_rasgos_diarios_mensuales_desde_crudo():
    crudo = pd.read_csv(RAIZ/"data/raw/serie3/Sugar_data.csv", parse_dates=["date"])
    diario = pd.read_csv(OUT/"dias_y_uso_rasgos.csv", parse_dates=["date"])
    pd.testing.assert_frame_equal(crudo, diario[crudo.columns])
    m = pd.read_csv(OUT/"mensual_y_rasgos.csv")
    meses = crudo.date.dt.strftime("%Y-%m")
    retorno = np.log(crudo.close/crudo.close.shift())
    for t, fila in m.iterrows():
        q = crudo[meses.eq(fila.mes)]
        np.testing.assert_allclose(fila.precio, np.mean(q.close))
        np.testing.assert_allclose(fila.cierre, q.close.iloc[-1])
        valido = (q.high+1e-5 >= q[["open", "low", "close"]].max(axis=1)) & (q.low-1e-5 <= q[["open", "high", "close"]].min(axis=1))
        np.testing.assert_allclose(fila.rango_diario_log, np.log(q.loc[valido, "high"]/q.loc[valido, "low"]).mean())
        np.testing.assert_allclose(fila.cuerpo_diario_log, np.log(q.loc[valido, "close"]/q.loc[valido, "open"]).mean(), atol=1e-14)
        np.testing.assert_allclose(fila.volumen_medio, q.loc[q.volume.gt(0), "volume"].mean())
        r = retorno.loc[q.index][diario.loc[q.index, "uso_retorno_volatilidad"]]
        np.testing.assert_allclose(fila.vol_diaria, np.std(r, ddof=1))
        np.testing.assert_allclose(fila.riesgo_bajista_diario, np.sqrt(np.mean(np.minimum(r, 0)**2)))
        if t >= 12:
            np.testing.assert_allclose(fila.cambio_media_12m, np.log(fila.precio/m.precio.iloc[t-12]))
            np.testing.assert_allclose(fila.vol_media_12m, np.std(np.log(m.precio.iloc[t-11:t+1].to_numpy()/m.precio.iloc[t-12:t].to_numpy()), ddof=1))
            np.testing.assert_allclose(fila.volumen_relativo_12m, np.log(fila.volumen_medio/m.volumen_medio.iloc[t-11:t+1].mean()), atol=1e-14)
    assert len(crudo) == 6097 and m.n_dias.sum() == 6082
    fuera = pd.read_csv(OUT/"filas_mes_incompleto.csv", parse_dates=["date"])
    pd.testing.assert_frame_equal(fuera[crudo.columns].reset_index(drop=True), crudo[meses.eq("2024-06")].reset_index(drop=True))
    iniciales = pd.read_csv(OUT/"meses_sin_rasgos_completos.csv")
    assert len(iniciales) == 12 and iniciales.motivo.notna().all()
    decision = json.loads((OUT/"decision.json").read_text(encoding="utf-8"))
    assert hashlib.sha256((RAIZ/"data/raw/serie3/Sugar_data.csv").read_bytes()).hexdigest() == decision["fuente_sha256"]


def test_ridge_reconstruido_por_matrices_y_artefacto_final():
    m = pd.read_csv(OUT/"mensual_y_rasgos.csv")
    p = pd.read_csv(OUT/"predicciones_historicas.csv")
    diseno = json.loads((OUT/"diseno_previo.json").read_text(encoding="utf-8"))
    for c in diseno["candidatos"]:
        if not c["familia"].startswith("ridge"):
            continue
        columnas = diseno["conjuntos"][c["rasgos"]]
        for f in p[p.metodo.eq(c["metodo"])].itertuples():
            t = np.flatnonzero(m.mes.eq(f.origen))[0]
            j = np.arange(12, t-f.horizonte+1)
            x = m.loc[j, columnas].to_numpy()
            z = (x-x.mean(axis=0))/x.std(axis=0)
            y = np.log(m.precio.iloc[j+f.horizonte].to_numpy()/m.cierre.iloc[j].to_numpy())
            b = np.linalg.solve(z.T@z+c["alpha"]*np.eye(len(columnas)), z.T@(y-y.mean()))
            pred = m.cierre.iloc[t]*np.exp(y.mean()+((m.loc[t, columnas].to_numpy(dtype=float)-x.mean(axis=0))/x.std(axis=0))@b)
            np.testing.assert_allclose(f.prediccion, pred, rtol=1e-10, atol=1e-10)
    final = pd.read_csv(OUT/"pronosticos_ultimo_origen.csv")
    artefacto = joblib.load(OUT/"modelos.joblib")
    for f in final.itertuples():
        a = artefacto["candidatos"][str(f.horizonte)][f.metodo]
        if a["pipeline"] is not None:
            pred = m.cierre.iloc[-1]*np.exp(a["pipeline"].predict(m.iloc[[-1]][a["columnas"]])[0])
            np.testing.assert_allclose(f.prediccion, pred)


def test_malla_seleccion_congelada_metricas_bandas_y_referencia_original():
    p = pd.read_csv(OUT/"predicciones_historicas.csv")
    tabla = pd.read_csv(OUT/"metricas.csv")
    bandas = pd.read_csv(OUT/"intervalos_evaluacion.csv")
    bandas = bandas[bandas.seleccionado]
    resumen = pd.read_csv(OUT/"metricas_intervalos.csv")
    resumen = resumen[resumen.seleccionado]
    anterior = pd.read_csv(RAIZ/"outputs/serie3_pronostico/predicciones_historicas.csv")
    diseno = json.loads((OUT/"diseno_previo.json").read_text(encoding="utf-8"))
    decision = json.loads((OUT/"seleccion_congelada.json").read_text(encoding="utf-8"))
    assert len(diseno["candidatos"]) == 19
    assert p.prediccion.gt(0).all() and np.isfinite(p.prediccion).all()
    for h in [1, 3]:
        s = p[p.fase.eq("seleccion") & p.horizonte.eq(h)]
        assert s.groupby("metodo").size().eq(104).all()
        mae = {n: np.mean(np.abs(g.prediccion-g.observado)) for n, g in s.groupby("metodo")}
        elegido = next(c["metodo"] for c in diseno["candidatos"] if mae[c["metodo"]] <= 1.02*min(mae.values()))
        assert elegido == decision[str(h)]
        for (fase, metodo), g in p[p.horizonte.eq(h)].groupby(["fase", "metodo"]):
            f = tabla[tabla.horizonte.eq(h) & tabla.fase.eq(fase) & tabla.metodo.eq(metodo)].iloc[0]
            np.testing.assert_allclose(f.MAE, np.abs(g.prediccion-g.observado).mean())
            np.testing.assert_allclose(f.WAPE_pct, 100*np.abs(g.prediccion-g.observado).sum()/g.observado.sum())
            if fase != "seleccion":
                assert len(g) == (57 if fase == "calibracion" else 64 if h == 1 else 62)
        cal = p[p.fase.eq("calibracion") & p.horizonte.eq(h) & p.metodo.eq(elegido)]
        assert cal.objetivo.max() < p[p.fase.eq("evaluacion")].origen.min()
        for cobertura in [0.8, 0.95]:
            k = int(np.ceil((len(cal)+1)*cobertura))
            q = np.sort(np.abs(np.log(cal.observado/cal.prediccion)))[k-1]
            b = bandas[bandas.horizonte.eq(h) & bandas.cobertura_nominal.eq(cobertura)]
            np.testing.assert_allclose(b.inferior, b.prediccion*np.exp(-q))
            np.testing.assert_allclose(b.superior, b.prediccion*np.exp(q))
            score=b.superior-b.inferior+2/(1-cobertura)*(np.maximum(b.inferior-b.observado,0)+np.maximum(b.observado-b.superior,0))
            np.testing.assert_allclose(b.winkler, score)
            r = resumen[resumen.horizonte.eq(h) & resumen.cobertura_nominal.eq(cobertura)].iloc[0]
            assert r.aciertos == b.observado.between(b.inferior, b.superior).sum()
    for metodo in ["ingenuo_cierre", "ingenuo_media"]:
        a = p[p.metodo.eq(metodo)].sort_values(["horizonte", "origen"])
        b = anterior[anterior.metodo.eq(metodo)].sort_values(["horizonte", "origen"])
        np.testing.assert_allclose(a.prediccion, b.prediccion)
        np.testing.assert_allclose(a.observado, b.observado)
    ajustes = [json.loads(l) for l in (OUT/"ajustes.jsonl").read_text(encoding="utf-8").splitlines()]
    assert all(a["ultimo_objetivo_ajuste"] <= a["origen"] for a in ajustes)


def test_arboles_y_kernel_reconstruidos_en_origenes_historicos():
    """Contrasta rutas de hojas y suma de kernels, sin llamar a predict."""
    from sklearn.ensemble import ExtraTreesRegressor
    from sklearn.svm import SVR

    m = pd.read_csv(OUT/"mensual_y_rasgos.csv")
    p = pd.read_csv(OUT/"predicciones_historicas.csv")
    diseno = json.loads((OUT/"diseno_previo.json").read_text(encoding="utf-8"))
    columnas = diseno["conjuntos"]["completos"]
    for h in [1, 3]:
        for origen in ["2010-03", "2016-02", "2022-04"]:
            t = np.flatnonzero(m.mes.eq(origen))[0]
            j = np.arange(12, t-h+1)
            x = m.loc[j, columnas].to_numpy()
            actual = m.loc[t, columnas].to_numpy(dtype=float)
            y = np.log(m.precio.iloc[j+h].to_numpy()/m.cierre.iloc[j].to_numpy())
            arboles = ExtraTreesRegressor(n_estimators=100, min_samples_leaf=10,
                max_features=.8, random_state=2026, n_jobs=1).fit(x, y)
            hojas = []
            for estimador in arboles.estimators_:
                tree = estimador.tree_
                nodo = 0
                while tree.children_left[nodo] != -1:
                    nodo = tree.children_left[nodo] if np.float32(actual[tree.feature[nodo]]) <= tree.threshold[nodo] else tree.children_right[nodo]
                hojas.append(tree.value[nodo, 0, 0])
            esperado = m.cierre.iloc[t]*np.exp(np.mean(hojas))
            f = p[p.horizonte.eq(h) & p.origen.eq(origen) & p.metodo.eq("extra_trees_10")].iloc[0]
            np.testing.assert_allclose(f.prediccion, esperado)
            z = (x-x.mean(axis=0))/x.std(axis=0)
            a = (actual-x.mean(axis=0))/x.std(axis=0)
            svr = SVR(C=.1, epsilon=.02, kernel="rbf").fit(z, y)
            kernels = np.exp(-svr._gamma*np.sum((svr.support_vectors_-a)**2, axis=1))
            esperado = m.cierre.iloc[t]*np.exp(svr.intercept_[0]+svr.dual_coef_[0]@kernels)
            f = p[p.horizonte.eq(h) & p.origen.eq(origen) & p.metodo.eq("svr_0.1")].iloc[0]
            np.testing.assert_allclose(f.prediccion, esperado)


def test_propuesta_entrega_dos_modelos_y_no_inventa_test_ciego():
    decision = json.loads((OUT/"decision_propuesta.json").read_text(encoding="utf-8"))
    previos = json.loads((OUT/"seleccion_congelada.json").read_text(encoding="utf-8"))
    assert decision["propuestos"] == {"1": "extra_trees_10", "3": "ridge_historia_100"}
    assert decision["ganadores_seleccion_previa"] == previos == {"1": "ingenuo_cierre", "3": "ingenuo_cierre"}
    assert decision["evaluacion_reutilizada"]
    assert not decision["test_ciego"]["reservado_en_datos_actuales"]
    assert not decision["test_ciego"]["ejecutado"]
    m = pd.read_csv(OUT/"mensual_y_rasgos.csv")
    f = pd.read_csv(OUT/"pronosticos_propuestos.csv")
    b = pd.read_csv(OUT/"intervalos_propuestos.csv")
    artefacto = joblib.load(OUT/"modelos_propuestos.joblib")
    assert len(f) == 2 and len(b) == 4 and f.propuesto.all() and b.propuesto.all()
    for fila in f.itertuples():
        modelo = artefacto["modelos"][str(fila.horizonte)]
        assert modelo["config"]["metodo"] == fila.metodo == decision["propuestos"][str(fila.horizonte)]
        assert modelo["pipeline"] is not None
        esperado = m.cierre.iloc[-1]*np.exp(modelo["pipeline"].predict(m.iloc[[-1]][modelo["columnas"]])[0])
        np.testing.assert_allclose(fila.prediccion, esperado)
        for c in [80, 95]:
            banda = b[b.horizonte.eq(fila.horizonte) & b.cobertura_nominal.eq(c/100)].iloc[0]
            np.testing.assert_allclose(getattr(fila, f"inferior_{c}"), esperado*np.exp(-banda.q_log))
            np.testing.assert_allclose(getattr(fila, f"superior_{c}"), esperado*np.exp(banda.q_log))
