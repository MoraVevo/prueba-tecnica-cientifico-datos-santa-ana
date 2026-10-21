"""Serie III.3: pronóstico mensual con selección, calibración y evaluación temporal."""

import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from scripts.analizar_precios_serie3 import preparar


RASGOS = ["log_cierre_sobre_media", "cambio_media_1m", "cambio_media_3m"]
PRIORIDAD = ["ingenuo_cierre", "ingenuo_media", "ridge_100", "ridge_10", "ridge_1"]
HORIZONTES = [1, 3]
ULTIMO_COMPLETO = "2024-05"  # Junio termina el día 24 en la fuente del ejercicio.


def mensualizar(crudo, ultimo_completo=ULTIMO_COMPLETO):
    """Promedios observados, sin borrar marcas de calidad ni ajustar contratos."""
    p = preparar(crudo)
    p["mes"] = p.date.dt.to_period("M")
    p["marca_calidad"] = p.ohlc_incoherente | p.volumen_cero
    fuera = p[p.mes > pd.Period(ultimo_completo, freq="M")].copy()
    fuera["motivo"] = "mes_incompleto_en_fuente"
    incluidos = p[p.mes <= pd.Period(ultimo_completo, freq="M")]
    m = incluidos.groupby("mes").agg(precio=("close", "mean"), cierre=("close", "last"),
        n_dias=("close", "size"), ultimo_dia_observado=("date", "max"),
        n_marcas_calidad=("marca_calidad", "sum"))
    assert m.index.equals(pd.period_range(m.index.min(), m.index.max(), freq="M", name="mes"))
    m["log_cierre_sobre_media"] = np.log(m.cierre / m.precio)
    m["cambio_media_1m"] = np.log(m.precio / m.precio.shift(1))
    m["cambio_media_3m"] = np.log(m.precio / m.precio.shift(3))
    return m, fuera


def predecir(m, origen, h, metodo):
    """Cada etiqueta de ajuste debe haber madurado al emitir el pronóstico."""
    actual = m.iloc[origen]
    if metodo in ["ingenuo_cierre", "ingenuo_media"]:
        return float(actual.cierre if metodo == "ingenuo_cierre" else actual.precio), {}, None
    alpha = int(metodo.split("_")[1])
    # j+h <= origen. Se excluyen solo los tres meses iniciales sin rezagos.
    j = np.arange(3, origen-h+1)
    x = m.iloc[j][RASGOS]
    y = np.log(m.precio.iloc[j+h].to_numpy() / m.cierre.iloc[j].to_numpy())
    modelo = make_pipeline(StandardScaler(), Ridge(alpha=alpha))
    modelo.fit(x, y)
    pred = float(actual.cierre * np.exp(modelo.predict(m.iloc[[origen]][RASGOS])[0]))
    escala, ridge = modelo.steps[0][1], modelo.steps[1][1]
    detalle = {"n_ajuste": len(j), "ultimo_origen_ajuste": str(m.index[j[-1]]),
        "ultimo_objetivo_ajuste": str(m.index[j[-1]+h]),
        "media": escala.mean_.tolist(), "escala": escala.scale_.tolist(),
        "coeficiente": ridge.coef_.tolist(), "intercepto": float(ridge.intercept_)}
    return pred, detalle, modelo


def fase_origen(mes, posicion, h, n):
    if posicion < 59:
        return "historia_inicial"
    if posicion+h >= n:
        return "sin_objetivo_completo"
    if pd.Period("2005-02", "M") <= mes <= pd.Period("2013-09", "M"):
        return "seleccion"
    if pd.Period("2014-01", "M") <= mes <= pd.Period("2018-09", "M"):
        return "calibracion"
    if mes >= pd.Period("2019-01", "M"):
        return "evaluacion"
    return "separacion_entre_fases"


def metricas(g):
    error = g.prediccion - g.observado
    return {"n": len(g), "MAE": error.abs().mean(), "RMSE": np.sqrt(error.pow(2).mean()),
            "WAPE_pct": 100*error.abs().sum()/g.observado.sum(), "sesgo": error.mean()}


def seleccionar(predicciones):
    """Solo selección: menor complejidad a <=2 % del menor MAE por horizonte."""
    elegidos = {}
    for h in HORIZONTES:
        s = predicciones[predicciones.fase.eq("seleccion") & predicciones.horizonte.eq(h)]
        mae = s.groupby("metodo").apply(lambda g: (g.prediccion-g.observado).abs().mean(), include_groups=False)
        admisibles = mae[mae <= 1.02*mae.min()].index
        elegidos[str(h)] = next(nombre for nombre in PRIORIDAD if nombre in admisibles)
    return elegidos


def cuantil_banda(errores, cobertura):
    """Orden conservador de errores absolutos logarítmicos fuera de muestra.

    No se ofrece garantía conformal: hay dependencia y cambios de distribución.
    """
    ordenados = np.sort(np.asarray(errores))
    k = int(np.ceil((len(ordenados)+1)*cobertura))
    assert 1 <= k <= len(ordenados), "Calibración insuficiente para este nivel."
    return float(ordenados[k-1]), k


def puntuar_intervalo(observado, inferior, superior, cobertura):
    """Winkler: amplitud más penalización por quedar fuera; menor es mejor."""
    alpha = 1-cobertura
    return (superior-inferior + 2/alpha*np.maximum(inferior-observado, 0) +
            2/alpha*np.maximum(observado-superior, 0))


def ejecutar(raiz):
    raiz = Path(raiz)
    salida = raiz / "outputs/serie3_pronostico"
    salida.mkdir(parents=True, exist_ok=True)
    fuente = raiz / "data/raw/serie3/Sugar_data.csv"
    huella = hashlib.sha256(fuente.read_bytes()).hexdigest()
    m, fuera = mensualizar(pd.read_csv(fuente))
    m.to_csv(salida / "mensual.csv")
    fuera.to_csv(salida / "filas_fuera_mensual.csv", index=False)
    papeles, filas, ajustes = [], [], []
    for h in HORIZONTES:
        for i, mes in enumerate(m.index):
            fase = fase_origen(mes, i, h, len(m))
            papeles.append({"origen": str(mes), "objetivo": str(mes+h), "horizonte": h, "fase": fase})
            if fase not in ["seleccion", "calibracion", "evaluacion"]:
                continue
            for metodo in PRIORIDAD:
                pred, detalle, _ = predecir(m, i, h, metodo)
                filas.append({"origen": str(mes), "objetivo": str(m.index[i+h]), "horizonte": h,
                    "fase": fase, "metodo": metodo, "observado": float(m.precio.iloc[i+h]),
                    "prediccion": pred, "sin_marcas_calidad": bool(m.n_marcas_calidad.iloc[[i,i+h]].eq(0).all())})
                if detalle:
                    ajustes.append({"origen": str(mes), "horizonte": h, "fase": fase, "metodo": metodo, **detalle})
    pd.DataFrame(papeles).to_csv(salida / "origenes_y_papeles.csv", index=False)
    (salida / "parametros_ajustes.jsonl").write_text(
        "\n".join(json.dumps(f,ensure_ascii=False) for f in ajustes)+"\n", encoding="utf-8")
    p = pd.DataFrame(filas)
    elegidos = seleccionar(p)
    p["seleccionado"] = [metodo == elegidos[str(h)] for h,metodo in zip(p.horizonte,p.metodo)]
    p["error_abs_log"] = np.log(p.observado/p.prediccion).abs()
    resumen = [{"fase": fase, "horizonte": h, "metodo": metodo, **metricas(g)}
               for (fase,h,metodo),g in p.groupby(["fase","horizonte","metodo"])]
    pd.DataFrame(resumen).to_csv(salida / "metricas_puntuales.csv", index=False)
    bandas, cuantiles, medidas = [], [], []
    for (h,metodo),g in p[p.fase.eq("calibracion")].groupby(["horizonte","metodo"]):
        for cobertura in [.8,.95]:
            q, k = cuantil_banda(g.error_abs_log, cobertura)
            cuantiles.append({"horizonte": h, "metodo": metodo, "cobertura_nominal": cobertura,
                "n_calibracion": len(g), "orden": k, "q_log": q,
                "ultimo_objetivo_calibracion": g.objetivo.max()})
            test = p[p.fase.eq("evaluacion") & p.horizonte.eq(h) & p.metodo.eq(metodo)].copy()
            test["cobertura_nominal"] = cobertura
            test["inferior"] = test.prediccion * np.exp(-q)
            test["superior"] = test.prediccion * np.exp(q)
            test["cubierto"] = test.observado.between(test.inferior,test.superior)
            test["winkler"] = puntuar_intervalo(test.observado,test.inferior,test.superior,cobertura)
            bandas.append(test)
            medidas.append({"horizonte": h, "metodo": metodo, "cobertura_nominal": cobertura,
                "n": len(test), "aciertos": int(test.cubierto.sum()), "cobertura_real_pct":100*test.cubierto.mean(),
                "amplitud_media": (test.superior-test.inferior).mean(), "Winkler_medio":test.winkler.mean()})
    qtabla = pd.DataFrame(cuantiles)
    qtabla.to_csv(salida / "cuantiles_calibracion.csv", index=False)
    pd.concat(bandas).to_csv(salida / "intervalos_evaluacion.csv", index=False)
    pd.DataFrame(medidas).to_csv(salida / "metricas_intervalos.csv", index=False)
    p.to_csv(salida / "predicciones_historicas.csv", index=False)
    test = p[p.fase.eq("evaluacion")].copy()
    test["ano_objetivo"] = test.objetivo.str[:4].astype(int)
    pd.DataFrame([{"horizonte":h,"metodo":metodo,"ano_objetivo":ano,**metricas(g)}
        for (h,metodo,ano),g in test.groupby(["horizonte","metodo","ano_objetivo"])]).to_csv(
        salida / "metricas_por_ano.csv",index=False)
    revision = test[~test.sin_marcas_calidad].copy()
    revision["motivo"] = "mes_origen_u_objetivo_con_OHLC_incoherente_o_volumen_cero"
    revision.to_csv(salida / "evaluacion_fuera_sensibilidad_calidad.csv",index=False)
    pd.DataFrame([{"horizonte":h,"metodo":metodo,**metricas(g)}
        for (h,metodo),g in test[test.sin_marcas_calidad].groupby(["horizonte","metodo"])]).to_csv(
        salida / "sensibilidad_calidad.csv",index=False)
    finales, modelos, muestras = [], {}, []
    for h in HORIZONTES:
        for metodo in PRIORIDAD:
            pred, detalle, modelo = predecir(m,len(m)-1,h,metodo)
            fila = {"origen":str(m.index[-1]),"objetivo":str(m.index[-1]+h),"horizonte":h,
                    "metodo":metodo,"seleccionado":metodo==elegidos[str(h)],"prediccion":pred}
            for cobertura in [.8,.95]:
                q = qtabla[qtabla.horizonte.eq(h) & qtabla.metodo.eq(metodo) & qtabla.cobertura_nominal.eq(cobertura)].q_log.iloc[0]
                fila[f"inferior_{int(cobertura*100)}"] = pred*np.exp(-q)
                fila[f"superior_{int(cobertura*100)}"] = pred*np.exp(q)
            finales.append(fila)
            if fila["seleccionado"]:
                modelos[str(h)] = {"metodo":metodo,"pipeline":modelo,"detalle":detalle,"cierre_origen":float(m.cierre.iloc[-1])}
        for j,mes in enumerate(m.index):
            valido = j >= 3 and j+h < len(m)
            muestras.append({"horizonte":h,"origen":str(mes),"objetivo":str(mes+h),
                "en_ajuste_final":valido,"motivo_fuera":"" if valido else ("sin_rezagos_iniciales" if j<3 else "objetivo_aun_no_observado")})
    pd.DataFrame(finales).to_csv(salida / "pronosticos_ultimo_origen.csv",index=False)
    pd.DataFrame(muestras).to_csv(salida / "muestra_ajuste_final.csv",index=False)
    joblib.dump({"objetivo":"promedio mensual de cierres publicados","origen":str(m.index[-1]),
                 "rasgos":RASGOS,"modelos":modelos,"cuantiles":qtabla},salida / "modelos_pronostico.joblib")
    decision = {"fuente_sha256":huella,"filas_crudas":len(pd.read_csv(fuente)),
        "filas_fuera_mes_incompleto":len(fuera),"meses_completos":len(m),"ultimo_origen":str(m.index[-1]),
        "objetivo":"promedio mensual de cierres publicados; centavos USD/libra",
        "horizontes_meses":HORIZONTES,"seleccionados":elegidos,"rasgos":RASGOS,
        "criterio":"menor complejidad dentro de 2 % de menor MAE en seleccion",
        "seleccion_origenes":["2005-02","2013-09"],"calibracion_origenes":["2014-01","2018-09"],
        "evaluacion_origenes_desde":"2019-01","intervalos":"errores de calibracion por horizonte/metodo; cuantiles congelados",
        "continuidad_contratos_certificada":False,"pronostico_actual":False,
        "test_nuevo_sin_inspeccion_previa":False}
    assert hashlib.sha256(fuente.read_bytes()).hexdigest() == huella
    (salida / "decision.json").write_text(json.dumps(decision,ensure_ascii=False,indent=2),encoding="utf-8")
    return decision


if __name__ == "__main__":
    print(json.dumps(ejecutar(Path(__file__).resolve().parents[1]),ensure_ascii=True,indent=2))
