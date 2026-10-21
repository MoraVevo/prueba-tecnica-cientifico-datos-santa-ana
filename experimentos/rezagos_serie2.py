"""Estudio temporal del inciso 3, independiente del artefacto campeón."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.modelado_serie2 import OBJETIVO, calcular_metricas, crear_modelos


REZAGOS = (0, 10, 30, 60, 120, 300, 600)
PRESIONES = ("PTCA_8322A.AV_0#", "PTCA_8324.AV_0#")


def construir_rezagos(entradas, segundos):
    """X(t-k) en rejilla comprobada de diez segundos; nunca rellena el inicio."""
    assert segundos > 0 and segundos % 10 == 0
    assert entradas.index.to_series().diff().dropna().eq(pd.Timedelta(seconds=10)).all()
    return entradas.shift(segundos // 10).rename(columns=lambda c: f"{c}__pasado_{segundos}s")


def explorar_correlaciones(entradas, objetivo, mascara):
    """Compara niveles y cambios con pares válidos, sin imputar para correlacionar.

    Positivo k siempre significa señal ANTERIOR al caudal. Los cambios son
    diferencias hacia atrás de 10/60 s, sin ventanas centradas ni objetivo pasado.
    La máscara común garantiza historia de 600+60 s para todas las comparaciones.
    """
    filas = []
    for cambio in (0, 10, 60):
        x = entradas if cambio == 0 else entradas.diff(cambio // 10)
        y = objetivo if cambio == 0 else objetivo.diff(cambio // 10)
        for rezago in REZAGOS:
            a = x.shift(rezago // 10).loc[mascara]
            b = y.loc[mascara]
            correlaciones = a.corrwith(b)
            for sensor, r in correlaciones.items():
                filas.append({"sensor": sensor, "cambio_s": cambio,
                              "rezago_s": rezago, "correlacion": r,
                              "n_pares": int((a[sensor].notna() & b.notna()).sum())})
    return pd.DataFrame(filas)


def seleccionar_rezagos(correlaciones):
    """Un rezago positivo por sensor, máximo |r| de cambios de 10 s en pasado.

    Es una regla de generación de candidatos, no prueba de significancia o
    causalidad. Se conserva el cero como referencia; empates prefieren menor k.
    """
    positivas = correlaciones.query("cambio_s == 10 and rezago_s > 0").copy()
    positivas["magnitud"] = positivas.correlacion.abs()
    elegidas = positivas.sort_values(
        ["sensor", "magnitud", "rezago_s"], ascending=[True, False, True],
    ).drop_duplicates("sensor").drop(columns="magnitud")
    cero = correlaciones.query("cambio_s == 10 and rezago_s == 0").set_index("sensor")
    elegidas["correlacion_cero"] = elegidas.sensor.map(cero.correlacion)
    return elegidas


def ejecutar(raiz):
    """Exporta trazabilidad, correlaciones y cuatro comparaciones prefijadas."""
    raiz = Path(raiz)
    salida = raiz / "outputs/rezagos"
    salida.mkdir(parents=True, exist_ok=True)
    protegidos = [raiz / "data/raw/serie2/data.csv",
                  raiz / "scripts/modelado_serie2.py",
                  raiz / "notebooks/07_sensor_virtual_serie2.ipynb",
                  *(raiz / "outputs").glob("serie2_*")]
    huellas = {str(p.relative_to(raiz)): hashlib.sha256(p.read_bytes()).hexdigest()
               for p in protegidos if p.is_file()}
    crudo = pd.read_csv(raiz / "data/raw/serie2/data.csv", parse_dates=["date"])
    assert len(crudo) == 86400
    assert crudo.date.diff().dropna().eq(pd.Timedelta(seconds=5)).all()
    origen = crudo.date.iloc[0]
    # Primero se toma la misma fase de diez segundos que la campeona.
    datos = crudo.iloc[::2].set_index("date")
    x, y = datos.drop(columns=OBJETIVO), datos[OBJETIVO]
    # El quinto día ni siquiera forma parte de la matriz experimental.
    desarrollo = x.index < origen + pd.Timedelta(days=4)
    x, y = x.loc[desarrollo], y.loc[desarrollo]
    minimo = origen + pd.Timedelta(seconds=660)
    historia = x.index >= minimo
    seleccion_original = pd.read_csv(raiz / "outputs/serie2_selecciones_por_pliegue.csv")
    limites = pd.read_csv(raiz / "outputs/serie2_particiones.csv")
    limites = limites[limites.particion.str.startswith("Validación")]
    traza = crudo.copy()
    traza.insert(0, "fila_original", np.arange(len(crudo)))
    traza["uso"] = "elegible"
    traza["motivo"] = ""
    reglas = [
        (traza.date >= origen + pd.Timedelta(days=4), "quinto_dia_fuera_del_estudio"),
        ((traza.fila_original % 2 == 1) & (traza.date < origen + pd.Timedelta(days=4)),
         "segunda_fase_de_muestreo_10s"),
        ((traza.fila_original % 2 == 0) & (traza.date < minimo),
         "sin_historia_comun_de_660s"),
    ]
    for mascara, motivo in reglas:
        traza.loc[mascara, ["uso", "motivo"]] = ["fuera_del_estudio", motivo]
    traza.to_csv(salida / "trazabilidad_filas.csv", index=False)
    traza[traza.uso == "fuera_del_estudio"].to_csv(salida / "filas_excluidas.csv", index=False)
    correlaciones, selecciones, metricas, predicciones, papeles, reproducciones = [], [], [], [], [], []
    primeras = None
    for _, corte in limites.iterrows():
        nombre = corte.particion
        fin_train = pd.Timestamp(corte.fin_entrenamiento)
        inicio_eval, fin_eval = pd.Timestamp(corte.inicio_evaluacion), pd.Timestamp(corte.fin_evaluacion)
        train_original = x.index <= fin_train
        train = train_original & historia
        evaluacion = (x.index >= inicio_eval) & (x.index <= fin_eval)
        columnas15 = seleccion_original.loc[seleccion_original.particion == nombre, "entrada"].tolist()
        assert len(columnas15) == 15 and OBJETIVO not in x.columns
        # Referencia exacta previa y control con la misma historia que las variantes.
        referencia = crear_modelos()["Ridge"].fit(x.loc[train_original, columnas15], y.loc[train_original])
        p_ref = referencia.predict(x.loc[evaluacion, columnas15])
        reproducciones.append({"particion": nombre, **calcular_metricas(y.loc[evaluacion], p_ref)})
        corr = explorar_correlaciones(x, y, train)
        corr["particion"] = nombre
        correlaciones.append(corr)
        elegidas = seleccionar_rezagos(corr)
        elegidas["particion"] = nombre
        selecciones.append(elegidas)
        if primeras is None:
            primeras = elegidas.copy()
        pasados = pd.concat([construir_rezagos(x[[f.sensor]], int(f.rezago_s))
                             for f in elegidas.itertuples()], axis=1)
        variantes = [(f"{n} actuales" + (" + rezagos" if memoria else ""), columnas,
                      columnas if memoria else [])
                     for n, columnas in ((15, columnas15), (29, x.columns.tolist()))
                     for memoria in (False, True)]
        # Diagnóstico añadido tras la comparación inicial: separar la historia de
        # las dos presiones dominantes de la de los otros trece sensores.
        # Es exploratorio sobre las mismas validaciones; no confirmación nueva.
        assert set(PRESIONES).issubset(columnas15)
        variantes.extend([
            ("15 actuales + historia dos presiones", columnas15, list(PRESIONES)),
            ("15 actuales + historia otras trece", columnas15, [c for c in columnas15 if c not in PRESIONES]),
        ])
        coeficientes = []
        for variante, columnas, historicas in variantes:
            matriz = x[columnas]
            extra = [f"{f.sensor}__pasado_{int(f.rezago_s)}s"
                     for f in elegidas.itertuples() if f.sensor in historicas]
            matriz = pd.concat([matriz, pasados[extra]], axis=1)
            modelo = crear_modelos()["Ridge"].fit(matriz.loc[train], y.loc[train])
            p = modelo.predict(matriz.loc[evaluacion])
            metricas.append({"particion": nombre, "variante": variante,
                             "entradas": matriz.shape[1], "n_train": int(train.sum()),
                             "n_eval": int(evaluacion.sum()), **calcular_metricas(y.loc[evaluacion], p)})
            predicciones.append(pd.DataFrame({"date": x.index[evaluacion], "particion": nombre,
                "variante": variante, "observado": y.loc[evaluacion].values, "estimado": p}))
            coeficientes.extend({"particion": nombre, "variante": variante, "entrada": c,
                                 "coeficiente_estandarizado": float(v)}
                                for c, v in zip(matriz.columns, modelo[-1].coef_))
        pd.DataFrame(coeficientes).to_csv(salida / f"coeficientes_{len(reproducciones)}.csv", index=False)
        papel = pd.DataFrame({"date": x.index, "particion": nombre, "papel": "otro_periodo"})
        papel.loc[train, "papel"] = "entrenamiento"
        papel.loc[evaluacion, "papel"] = "validacion"
        papel.loc[train_original & ~historia, "papel"] = "sin_historia_comun"
        papel.loc[(x.index > fin_train) & (x.index < inicio_eval), "papel"] = "separacion_5min"
        papeles.append(papel)
    pd.concat(correlaciones, ignore_index=True).to_csv(salida / "correlaciones_entrenamiento.csv", index=False)
    pd.concat(selecciones, ignore_index=True).to_csv(salida / "rezagos_por_entrenamiento.csv", index=False)
    pd.concat(papeles, ignore_index=True).to_csv(salida / "papeles_por_pliegue.csv", index=False)
    pd.DataFrame(reproducciones).to_csv(salida / "reproduccion_base_original.csv", index=False)
    m = pd.DataFrame(metricas)
    p = pd.concat(predicciones, ignore_index=True)
    m.to_csv(salida / "metricas.csv", index=False)
    p.to_csv(salida / "predicciones.csv", index=False)
    resumen = []
    for variante, filas in p.groupby("variante"):
        diarios = m[m.variante == variante]
        resumen.append({"variante": variante, "entradas": int(diarios.entradas.iloc[0]),
                        "MAE_medio": diarios.MAE.mean(), "peor_MAE_diario": diarios.MAE.max(),
                        "WAPE_agregado": calcular_metricas(filas.observado, filas.estimado)["WAPE_pct"]})
    resumen = pd.DataFrame(resumen)
    base = resumen.set_index("variante").loc["15 actuales", "MAE_medio"]
    resumen["cambio_MAE_pct_vs15"] = 100 * (resumen.MAE_medio / base - 1)
    resumen.to_csv(salida / "resumen.csv", index=False)
    # Corroboración descriptiva: el rezago del primer entrenamiento queda fijo
    # al medir cambios de cada día posterior. No elige otro rezago en evaluación.
    validaciones = []
    for _, corte in limites.iterrows():
        mascara = (x.index >= pd.Timestamp(corte.inicio_evaluacion)) & (x.index <= pd.Timestamp(corte.fin_evaluacion))
        for f in primeras.itertuples():
            a = x[f.sensor].diff().shift(int(f.rezago_s) // 10).loc[mascara]
            b = y.diff().loc[mascara]
            validaciones.append({"particion": corte.particion, "sensor": f.sensor,
                "rezago_s_fijo_dia1": int(f.rezago_s), "correlacion_cambios": a.corr(b),
                "correlacion_cero": x[f.sensor].diff().loc[mascara].corr(b)})
    pd.DataFrame(validaciones).to_csv(salida / "corroboracion_rezagos_dia1.csv", index=False)
    # Horas ancladas al inicio de cada evaluación; resumen pareado, sin asumir iid.
    p["error_abs"] = (p.estimado - p.observado).abs()
    p["hora"] = p.groupby(["particion", "variante"]).cumcount() // 360
    horas = p.groupby(["particion", "hora", "variante"]).error_abs.mean().unstack("variante")
    for n in (15, 29):
        horas[f"mejora_{n}"] = horas[f"{n} actuales"] - horas[f"{n} actuales + rezagos"]
    horas["mejora_dos_presiones"] = horas["15 actuales"] - horas["15 actuales + historia dos presiones"]
    horas.to_csv(salida / "errores_por_hora.csv")
    assert all(hashlib.sha256((raiz / p).read_bytes()).hexdigest() == h for p, h in huellas.items())
    verificacion = {"huellas_protegidas": huellas, "filas_crudo": len(crudo),
        "filas_elegibles": int((traza.uso == "elegible").sum()),
        "filas_fuera": traza.motivo.value_counts().to_dict(), "rezagos_s": REZAGOS,
        "regla_seleccion": "maximo absoluto de correlacion de cambios10s; solo entrenamiento",
        "dia5_evaluado": False, "objetivo_pasado_como_entrada": False,
        "alpha": 100, "promocion_campeona": False}
    (salida / "verificacion.json").write_text(json.dumps(verificacion, ensure_ascii=False, indent=2), encoding="utf-8")
    return resumen
