"""Serie III.3: comparación exploratoria acotada de rasgos y familias.

Conserva el experimento inicial. No convierte la evaluación ya inspeccionada
en un test nuevo ni corrige la continuidad contractual del archivo.
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from threadpoolctl import threadpool_limits

from scripts.analizar_precios_serie3 import preparar, MESES_PREVIOS, MESES_ENTREGA
from scripts.pronosticar_azucar_serie3 import (
    RASGOS, mensualizar, fase_origen, metricas, cuantil_banda, puntuar_intervalo,
)


HISTORIA = RASGOS + [
    "cambio_media_6m", "cambio_media_12m", "retorno_media_rezagado_1",
    "retorno_media_rezagado_2", "cambio_cierre_1m", "cambio_cierre_3m",
    "cambio_cierre_6m", "cambio_cierre_12m", "cierre_sobre_tendencia_3m",
    "cierre_sobre_tendencia_12m", "vol_media_3m", "vol_media_12m",
    "mes_seno", "mes_coseno",
]
OHLC = HISTORIA + ["rango_diario_log", "cuerpo_diario_log", "vol_diaria",
                   "riesgo_bajista_diario", "retorno_5sesiones"]
COMPLETOS = OHLC + ["volumen_relativo_3m", "volumen_relativo_12m"]
AUTORREGRESIVOS = ["log_cierre_sobre_media", "cambio_media_1m"] + [
    f"retorno_media_rezagado_{i}" for i in range(1, 12)]
CONJUNTOS = {"original": RASGOS, "autorregresivos": AUTORREGRESIVOS,
             "historia": HISTORIA, "ohlc": OHLC, "completos": COMPLETOS}

# Propuesta exploratoria fijada después de revisar la comparación histórica.
# No reemplaza al ganador de selección ni acredita un test independiente.
PROPUESTOS = {"1": "extra_trees_10", "3": "ridge_historia_100"}

# Malla pequeña, fijada antes de ejecutar: dos opciones por familia ampliada.
CANDIDATOS = [
    {"metodo": "ingenuo_cierre", "familia": "referencia", "rasgos": "original"},
    {"metodo": "ingenuo_media", "familia": "referencia", "rasgos": "original"},
    {"metodo": "deriva", "familia": "deriva", "rasgos": "original"},
    {"metodo": "suavizado", "familia": "suavizado", "rasgos": "original"},
    {"metodo": "ridge_original", "familia": "ridge_original", "rasgos": "original", "alpha": 100},
] + [
    {"metodo": f"ridge_{rasgos}_{alpha}", "familia": f"ridge_{rasgos}",
     "rasgos": rasgos, "alpha": alpha}
    for rasgos in ["autorregresivos", "historia", "ohlc", "completos"] for alpha in [100, 10]
] + [
    {"metodo": f"svr_{c}", "familia": "svr", "rasgos": "completos", "C": c}
    for c in [0.1, 1.0]
] + [
    {"metodo": f"extra_trees_{hoja}", "familia": "extra_trees", "rasgos": "completos", "hoja": hoja}
    for hoja in [5, 10]
] + [
    {"metodo": f"boosting_{hoja}", "familia": "boosting", "rasgos": "completos", "hoja": hoja}
    for hoja in [5, 10]
]


def construir_rasgos(crudo):
    """Solo historia conocida; cada fila cruda conserva uso y motivo por señal."""
    m, fuera = mensualizar(crudo)
    p = preparar(crudo)
    p["mes"] = p.date.dt.to_period("M")
    p["uso_mes_completo"] = p.mes <= m.index[-1]
    p["uso_ohlc"] = p.uso_mes_completo & ~p.ohlc_incoherente
    p["uso_volumen"] = p.uso_mes_completo & ~p.volumen_cero
    # Al cierre del mes se conoce su última sesión observada: no se exige
    # observar el mes siguiente para marcar la frontera del mes completo.
    ultima = p.date.eq(p.groupby("mes").date.transform("max"))
    primera = p.date.eq(p.groupby("mes").date.transform("min"))
    proxy = (p.date.dt.month.isin(MESES_PREVIOS) & ultima) | (p.date.dt.month.isin(MESES_ENTREGA) & primera)
    p["proxy_rasgos"] = proxy & p.uso_mes_completo
    motivo = pd.Series("", index=p.index)
    for mascara, texto in [(p.retorno_log.isna(), "sin_cierre_anterior"),
        (p.proxy_rasgos, "ventana_proxy_enlace"),
        (p.extremo_con_ohlc_incoherente, "OHLC_actual_o_anterior_incoherente"),
        (p.extremo_con_volumen_cero, "volumen_actual_o_anterior_cero")]:
        motivo.loc[mascara] += texto+";"
    p["uso_retorno_volatilidad"] = p.uso_mes_completo & motivo.eq("")
    p["motivo_ohlc"] = np.select(
        [~p.uso_mes_completo, p.ohlc_incoherente],
        ["mes_incompleto", "OHLC_incoherente"], default="")
    p["motivo_volumen"] = np.select(
        [~p.uso_mes_completo, p.volumen_cero],
        ["mes_incompleto", "volumen_cero_sin_reporte_confirmado"], default="")
    p["motivo_retorno"] = motivo.str.rstrip(";")
    p.loc[~p.uso_mes_completo, "motivo_retorno"] = "mes_incompleto"
    p["rango_rasgo"] = np.log(p.high / p.low).where(p.uso_ohlc)
    p["cuerpo_rasgo"] = np.log(p.close / p.open).where(p.uso_ohlc)
    p["volumen_rasgo"] = p.volume.where(p.uso_volumen)
    # Se calcula el retorno sobre la secuencia original, antes de enmascarar.
    p["retorno_rasgo"] = p.retorno_log.where(p.uso_retorno_volatilidad)
    p["bajista_rasgo"] = np.minimum(p.retorno_rasgo, 0)**2
    p["retorno_5sesiones"] = np.log(p.close / p.close.shift(5))
    q = p[p.uso_mes_completo].groupby("mes").agg(
        rango_diario_log=("rango_rasgo", "mean"), cuerpo_diario_log=("cuerpo_rasgo", "mean"),
        vol_diaria=("retorno_rasgo", "std"), riesgo_bajista_diario=("bajista_rasgo", "mean"),
        retorno_5sesiones=("retorno_5sesiones", "last"), volumen_medio=("volumen_rasgo", "mean"),
        dias_ohlc_utilizados=("uso_ohlc", "sum"), dias_volumen_utilizados=("uso_volumen", "sum"),
        retornos_vol_utilizados=("uso_retorno_volatilidad", "sum"))
    q["riesgo_bajista_diario"] = np.sqrt(q.riesgo_bajista_diario)
    m = m.join(q)
    for k in [6, 12]:
        m[f"cambio_media_{k}m"] = np.log(m.precio / m.precio.shift(k))
    for k in range(1, 12):
        m[f"retorno_media_rezagado_{k}"] = m.cambio_media_1m.shift(k)
    for k in [1, 3, 6, 12]:
        m[f"cambio_cierre_{k}m"] = np.log(m.cierre / m.cierre.shift(k))
    for k in [3, 12]:
        m[f"cierre_sobre_tendencia_{k}m"] = np.log(m.cierre / m.precio.rolling(k).mean())
        m[f"vol_media_{k}m"] = m.cambio_media_1m.rolling(k).std(ddof=1)
        m[f"volumen_relativo_{k}m"] = np.log(m.volumen_medio / m.volumen_medio.rolling(k).mean())
    m["mes_seno"] = np.sin(2*np.pi*m.index.month/12)
    m["mes_coseno"] = np.cos(2*np.pi*m.index.month/12)
    # Todos los conjuntos comparten los primeros doce meses sin historia completa.
    assert np.isfinite(m.iloc[12:][list(dict.fromkeys(COMPLETOS + AUTORREGRESIVOS))]).all().all()
    return m, p, fuera


def estimador(config):
    familia = config["familia"]
    if familia.startswith("ridge"):
        return make_pipeline(StandardScaler(), Ridge(alpha=config["alpha"]))
    if familia == "svr":
        return make_pipeline(StandardScaler(), SVR(C=config["C"], epsilon=0.02, kernel="rbf"))
    if familia == "extra_trees":
        return ExtraTreesRegressor(n_estimators=100, min_samples_leaf=config["hoja"],
                                   max_features=0.8, random_state=2026, n_jobs=1)
    if familia == "boosting":
        return HistGradientBoostingRegressor(max_iter=80, max_leaf_nodes=5,
            min_samples_leaf=config["hoja"], learning_rate=0.05,
            l2_regularization=1, early_stopping=False, random_state=2026)
    raise ValueError(f"Familia sin estimador: {familia}")


def predecir(m, origen, h, config):
    """Ajuste directo: j+h<=origen. Ningún escalado utiliza el futuro."""
    metodo = config["metodo"]
    historia = np.log(m.precio.iloc[:origen+1].to_numpy())
    detalle = {"n_ajuste": origen+1, "ultimo_objetivo_ajuste": str(m.index[origen])}
    if metodo.startswith("ingenuo"):
        pred = m.cierre.iloc[origen] if metodo == "ingenuo_cierre" else m.precio.iloc[origen]
        return float(pred), detalle, None
    if metodo == "deriva":
        return float(np.exp(historia[-1]+h*(historia[-1]-historia[0])/origen)), detalle, None
    if metodo == "suavizado":
        def filtrar(alpha):
            nivel = historia[0]
            sse = 0.0
            for y in historia[1:]:
                sse += (y-nivel)**2
                nivel = alpha*y+(1-alpha)*nivel
            return sse, nivel
        ajuste = minimize_scalar(lambda a: filtrar(a)[0], bounds=(0.001, 0.999), method="bounded")
        assert ajuste.success
        detalle["alpha"] = float(ajuste.x)
        return float(np.exp(filtrar(ajuste.x)[1])), detalle, None
    columnas = CONJUNTOS[config["rasgos"]]
    j = np.arange(12, origen-h+1)
    modelo = estimador(config)
    y = np.log(m.precio.iloc[j+h].to_numpy()/m.cierre.iloc[j].to_numpy())
    modelo.fit(m.iloc[j][columnas], y)
    pred = m.cierre.iloc[origen]*np.exp(modelo.predict(m.iloc[[origen]][columnas])[0])
    detalle.update(n_ajuste=len(j), primer_origen_ajuste=str(m.index[j[0]]),
        ultimo_origen_ajuste=str(m.index[j[-1]]), n_rasgos=len(columnas))
    return float(pred), detalle, modelo


def elegir(predicciones, candidatos=CANDIDATOS):
    """Elige con selección únicamente; prioridad explícita para diferencias <=2 %."""
    elegidos, familias = {}, []
    for h in [1, 3]:
        s = predicciones[predicciones.fase.eq("seleccion") & predicciones.horizonte.eq(h)]
        errores = s.assign(error=(s.prediccion-s.observado).abs()).groupby("metodo").error.mean()
        elegidos[str(h)] = next(c["metodo"] for c in candidatos if errores[c["metodo"]] <= 1.02*errores.min())
        for familia in dict.fromkeys(c["familia"] for c in candidatos):
            opciones = [c for c in candidatos if c["familia"] == familia]
            mejor = min(opciones, key=lambda c: errores[c["metodo"]])
            familias.append({"horizonte": h, "familia": familia, "metodo": mejor["metodo"],
                             "MAE_seleccion": errores[mejor["metodo"]]})
    return elegidos, pd.DataFrame(familias)


def guardar_propuesta(out):
    """Entrega dos modelos entrenados; conserva la elección temporal original."""
    out = Path(out)
    previo = json.loads((out/"decision.json").read_text(encoding="utf-8"))
    artefactos = joblib.load(out/"modelos.joblib")
    finales = pd.read_csv(out/"pronosticos_ultimo_origen.csv")
    bandas = pd.read_csv(out/"metricas_intervalos.csv")
    mascara = [n == PROPUESTOS[str(h)] for h, n in zip(finales.horizonte, finales.metodo)]
    pronosticos = finales.loc[mascara].copy().sort_values("horizonte")
    pronosticos = pronosticos.rename(columns={"seleccionado": "ganador_seleccion_previa"})
    pronosticos["propuesto"] = True
    assert len(pronosticos) == 2
    mascara = [n == PROPUESTOS[str(h)] for h, n in zip(bandas.horizonte, bandas.metodo)]
    intervalos = bandas.loc[mascara].copy()
    intervalos = intervalos.rename(columns={"seleccionado": "ganador_seleccion_previa"})
    intervalos["propuesto"] = True
    modelos = {h: artefactos["candidatos"][h][n] for h, n in PROPUESTOS.items()}
    assert all(m["pipeline"] is not None for m in modelos.values())
    decision = {
        "propuestos": PROPUESTOS, "ganadores_seleccion_previa": previo["seleccionados"],
        "criterio": "propuesta exploratoria por mejora posterior y horizonte; evaluación ya inspeccionada",
        "evaluacion_reutilizada": True,
        "test_ciego": {"reservado_en_datos_actuales": False, "ejecutado": False,
                       "estado": "pendiente; requiere datos no utilizados"},
        "uso": "prototipo para planificación y escenarios; sin validación comercial",
        "origen_historico": artefactos["origen"], "fuente_sha256": previo["fuente_sha256"],
        "continuidad_certificada": False,
    }
    pronosticos.to_csv(out/"pronosticos_propuestos.csv", index=False)
    intervalos.to_csv(out/"intervalos_propuestos.csv", index=False)
    joblib.dump({"modelos": modelos, "bandas": intervalos.to_dict("records"),
                 "decision": decision}, out/"modelos_propuestos.joblib")
    (out/"decision_propuesta.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8")
    return decision


def ejecutar(raiz):
    raiz = Path(raiz)
    out = raiz/"outputs/serie3_pronostico_ampliado"
    out.mkdir(parents=True, exist_ok=True)
    fuente = raiz/"data/raw/serie3/Sugar_data.csv"
    huella = hashlib.sha256(fuente.read_bytes()).hexdigest()
    diseno = {"registrado_utc": datetime.now(timezone.utc).isoformat(),
        "objetivo": "promedio mensual de cierres publicados a +1/+3 meses; centavos USD/libra",
        "candidatos": CANDIDATOS, "conjuntos": CONJUNTOS, "inicio_rasgos": 12,
        "seleccion": "2005-02 a 2013-09; menor complejidad en orden de malla a <=2% del menor MAE",
        "calibracion": "2014-01 a 2018-09, cuantiles congelados por horizonte",
        "evaluacion": "2019-01 en adelante; ya inspeccionada, comparación exploratoria",
        "ajuste": "historia creciente, j+h<=origen; mismo inicio j=12 para modelos directos",
        "restriccion": "malla fija; no ampliarla tras ver evaluación; sin datos externos ni test nuevo",
        "fuente_sha256": huella}
    # No sobrescribir el registro previo al reproducir exactamente el experimento.
    ruta_diseno = out/"diseno_previo.json"
    if ruta_diseno.exists():
        previo = json.loads(ruta_diseno.read_text(encoding="utf-8"))
        assert all(previo[k] == v for k, v in diseno.items() if k != "registrado_utc")
    else:
        ruta_diseno.write_text(json.dumps(diseno, ensure_ascii=False, indent=2), encoding="utf-8")
    m, diario, fuera = construir_rasgos(pd.read_csv(fuente))
    m.to_csv(out/"mensual_y_rasgos.csv")
    iniciales = m.iloc[:12].copy()
    iniciales["motivo"] = "historia_insuficiente_para_rasgos_de_12_meses;conservado_como_antecedente"
    iniciales.to_csv(out/"meses_sin_rasgos_completos.csv")
    diario.to_csv(out/"dias_y_uso_rasgos.csv", index=False)
    fuera.to_csv(out/"filas_mes_incompleto.csv", index=False)
    papeles, filas, ajustes = [], [], []
    for h in [1, 3]:
        for i, mes in enumerate(m.index):
            fase = fase_origen(mes, i, h, len(m))
            papeles.append({"origen": str(mes), "objetivo": str(mes+h), "horizonte": h,
                "fase": fase, "rasgos_completos": i >= 12,
                "motivo_sin_emision": "" if fase in ["seleccion", "calibracion", "evaluacion"] else fase})
            if fase != "seleccion":
                continue
            for c in CANDIDATOS:
                pred, detalle, _ = predecir(m, i, h, c)
                filas.append({"fase": fase, "origen": str(mes), "objetivo": str(mes+h),
                    "horizonte": h, "metodo": c["metodo"], "observado": float(m.precio.iloc[i+h]),
                    "prediccion": pred, "sin_marcas_calidad": bool(m.n_marcas_calidad.iloc[[i,i+h]].eq(0).all())})
                ajustes.append({"fase": fase, "origen": str(mes), "horizonte": h, "metodo": c["metodo"], **detalle})
        print(f"Selección a {h} meses calculada ({len(CANDIDATOS)} candidatos).", flush=True)
    seleccion = pd.DataFrame(filas)
    elegidos, representantes = elegir(seleccion)
    representantes.to_csv(out/"representantes_familias.csv", index=False)
    # Se congela antes de calcular calibración y evaluación ampliadas.
    (out/"seleccion_congelada.json").write_text(json.dumps(elegidos, indent=2), encoding="utf-8")
    for h in [1, 3]:
        nombres = set(representantes[representantes.horizonte.eq(h)].metodo) | {elegidos[str(h)], "ingenuo_cierre", "ingenuo_media"}
        configs = [c for c in CANDIDATOS if c["metodo"] in nombres]
        for i, mes in enumerate(m.index):
            fase = fase_origen(mes, i, h, len(m))
            if fase not in ["calibracion", "evaluacion"]:
                continue
            for c in configs:
                pred, detalle, _ = predecir(m, i, h, c)
                filas.append({"fase": fase, "origen": str(mes), "objetivo": str(mes+h),
                    "horizonte": h, "metodo": c["metodo"], "observado": float(m.precio.iloc[i+h]),
                    "prediccion": pred, "sin_marcas_calidad": bool(m.n_marcas_calidad.iloc[[i,i+h]].eq(0).all())})
                ajustes.append({"fase": fase, "origen": str(mes), "horizonte": h, "metodo": c["metodo"], **detalle})
        print(f"Calibración/evaluación a {h} meses calculadas.", flush=True)
    p = pd.DataFrame(filas)
    p["seleccionado"] = [metodo == elegidos[str(h)] for h, metodo in zip(p.horizonte, p.metodo)]
    p.to_csv(out/"predicciones_historicas.csv", index=False)
    pd.DataFrame(papeles).to_csv(out/"origenes_y_papeles.csv", index=False)
    (out/"ajustes.jsonl").write_text("\n".join(json.dumps(a, ensure_ascii=False) for a in ajustes)+"\n", encoding="utf-8")
    pd.DataFrame([{ "fase": f, "horizonte": h, "metodo": metodo, **metricas(g)}
        for (f, h, metodo), g in p.groupby(["fase", "horizonte", "metodo"])]).to_csv(out/"metricas.csv", index=False)
    test = p[p.fase.eq("evaluacion")].copy()
    test["ano_objetivo"] = test.objetivo.str[:4].astype(int)
    pd.DataFrame([{"horizonte": h, "metodo": metodo, "ano_objetivo": a, **metricas(g)}
        for (h, metodo, a), g in test.groupby(["horizonte", "metodo", "ano_objetivo"])]).to_csv(out/"metricas_por_ano.csv", index=False)
    revision = test[~test.sin_marcas_calidad].copy()
    revision["motivo"] = "mes_origen_u_objetivo_con_OHLC_incoherente_o_volumen_cero"
    revision.to_csv(out/"casos_fuera_sensibilidad.csv", index=False)
    pd.DataFrame([{"horizonte": h, "metodo": metodo, **metricas(g)}
        for (h, metodo), g in test[test.sin_marcas_calidad].groupby(["horizonte", "metodo"])]).to_csv(out/"sensibilidad_calidad.csv", index=False)
    bandas, medidas, finales, modelos, modelos_candidatos = [], [], [], {}, {}
    for (h, nombre), cal in p[p.fase.eq("calibracion")].groupby(["horizonte", "metodo"]):
        c = next(c for c in CANDIDATOS if c["metodo"] == nombre)
        pred, detalle, modelo = predecir(m, len(m)-1, h, c)
        a = {"config": c, "pipeline": modelo, "detalle": detalle,
             "columnas": CONJUNTOS[c["rasgos"]], "cierre_origen": float(m.cierre.iloc[-1])}
        modelos_candidatos.setdefault(str(h), {})[nombre] = a
        seleccionado = nombre == elegidos[str(h)]
        if seleccionado:
            modelos[str(h)] = a
        f = {"origen": str(m.index[-1]), "objetivo": str(m.index[-1]+h),
             "horizonte": h, "metodo": nombre, "seleccionado": seleccionado, "prediccion": pred}
        for cobertura in [0.8, 0.95]:
            q, orden = cuantil_banda(np.abs(np.log(cal.observado/cal.prediccion)), cobertura)
            b = test[test.horizonte.eq(h) & test.metodo.eq(nombre)].copy()
            b["cobertura_nominal"] = cobertura
            b["q_log"] = q
            b["inferior"] = b.prediccion*np.exp(-q)
            b["superior"] = b.prediccion*np.exp(q)
            b["cubierto"] = b.observado.between(b.inferior, b.superior)
            b["winkler"] = puntuar_intervalo(b.observado, b.inferior, b.superior, cobertura)
            bandas.append(b)
            medidas.append({"horizonte": h, "metodo": nombre, "seleccionado": seleccionado, "cobertura_nominal": cobertura,
                "q_log": q, "orden": orden, "n_calibracion": len(cal), "n": len(b),
                "aciertos": int(b.cubierto.sum()), "cobertura_real_pct": 100*b.cubierto.mean(),
                "amplitud_media": (b.superior-b.inferior).mean(), "Winkler_medio": b.winkler.mean()})
            f[f"inferior_{int(cobertura*100)}"] = pred*np.exp(-q)
            f[f"superior_{int(cobertura*100)}"] = pred*np.exp(q)
        finales.append(f)
    pd.concat(bandas).to_csv(out/"intervalos_evaluacion.csv", index=False)
    pd.DataFrame(medidas).to_csv(out/"metricas_intervalos.csv", index=False)
    pd.DataFrame(finales).to_csv(out/"pronosticos_ultimo_origen.csv", index=False)
    joblib.dump({"modelos": modelos, "candidatos": modelos_candidatos,
                 "origen": str(m.index[-1]), "bandas": medidas}, out/"modelos.joblib")
    decision = {"seleccionados": elegidos, "n_configuraciones": len(CANDIDATOS),
        "n_rasgos": {k: len(v) for k, v in CONJUNTOS.items()}, "fuente_sha256": huella,
        "filas_crudas": len(diario), "filas_mes_incompleto": len(fuera),
        "meses": len(m), "meses_iniciales_sin_rasgos": 12,
        "test_nuevo": False, "continuidad_certificada": False,
        "tipo": "ampliación exploratoria con datos del enunciado; selección congelada por MAE",
        "sin_datos_externos": True}
    (out/"decision.json").write_text(json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8")
    guardar_propuesta(out)
    assert hashlib.sha256(fuente.read_bytes()).hexdigest() == huella
    return decision


if __name__ == "__main__":
    with threadpool_limits(limits=1):
        print(json.dumps(ejecutar(Path(__file__).resolve().parents[1]), ensure_ascii=True, indent=2))
