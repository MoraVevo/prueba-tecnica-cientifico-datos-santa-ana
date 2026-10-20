"""Audita la campeona reproduciendo celdas reales, sin sobrescribir sus resultados."""

import ast
import hashlib
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from scripts.modelado_serie2 import OBJETIVO, calcular_metricas, crear_modelos, seleccionar_variables


def celda_sin_escrituras(texto):
    """Retira solo exportaciones; conserva las expresiones de selección, fit y predict."""
    class SinExportaciones(ast.NodeTransformer):
        def visit_Expr(self, nodo):
            llamada = nodo.value
            if isinstance(llamada, ast.Call) and isinstance(llamada.func, ast.Attribute):
                funcion = llamada.func
                if funcion.attr in {"to_csv", "write_text"}:
                    return None
                if funcion.attr == "dump" and isinstance(funcion.value, ast.Name) and funcion.value.id == "joblib":
                    return None
            return self.generic_visit(nodo)
    arbol = SinExportaciones().visit(ast.parse(texto))
    return compile(ast.fix_missing_locations(arbol), "notebook07_auditado", "exec")


def parametros(modelo):
    """Estado aprendido cuyo valor no debe depender de observaciones posteriores."""
    return [modelo[0].statistics_, modelo[1].mean_, modelo[1].scale_,
            modelo[-1].coef_, np.asarray(modelo[-1].intercept_)]


def main():
    salida = RAIZ / "outputs/auditoria_leakage"
    salida.mkdir(exist_ok=True)
    rutas = [*sorted((RAIZ / "outputs").glob("serie2_*")),
             RAIZ / "notebooks/07_sensor_virtual_serie2.ipynb", RAIZ / "scripts/modelado_serie2.py",
             RAIZ / "data/raw/serie2/data.csv"]
    huellas = {str(p.relative_to(RAIZ)): hashlib.sha256(p.read_bytes()).hexdigest() for p in rutas if p.is_file()}
    notebook = json.loads((RAIZ / "notebooks/07_sensor_virtual_serie2.ipynb").read_text(encoding="utf-8"))
    codigo = {i: celda_sin_escrituras("".join(notebook["cells"][i]["source"])) for i in [3, 5, 6, 8]}
    datos = pd.read_csv(RAIZ / "data/raw/serie2/data.csv", parse_dates=["date"])
    comunes = dict(pd=pd, np=np, json=json, joblib=joblib, OBJETIVO=OBJETIVO,
                   threadpool_limits=threadpool_limits, seleccionar_variables=seleccionar_variables,
                   calcular_metricas=calcular_metricas, display=lambda *a, **k: None, print=lambda *a, **k: None)
    contexto = dict(comunes, datos=datos, inicio=datos.date.iloc[0])
    exec(codigo[3], contexto)
    X, y, fechas = contexto["X"], contexto["y"], contexto["fechas"]
    assert len(X.columns) == 29 and OBJETIVO not in X and "date" not in X
    assert not any("__" in c for c in X)
    originales = pd.read_csv(RAIZ / "outputs/serie2_predicciones_validacion.csv", parse_dates=["date"])
    originales = originales.loc[originales.modelo.eq("Ridge") & originales.variante.eq("Reducida 15")]
    pruebas, duplicados, diagnosticos = [], [], []
    generador = np.random.default_rng(20261020)

    def ejecutar_pliegue(nombre, entrenar, validar, entradas, etiquetas):
        # Se reproduce la celda real para Ridge; los otros algoritmos no son la campeona.
        entorno = dict(comunes, X=entradas, y=etiquetas, fechas=fechas,
                       base=contexto["base"], pliegues=[(nombre, entrenar, validar)],
                       crear_modelos=lambda: {"Ridge": crear_modelos()["Ridge"]})
        exec(codigo[5], entorno)
        return entorno["reducidas"], entorno["modelo"]

    def verificar_invariancia(nombre, referencia, otra, columnas, otras_columnas, validar, caso):
        assert columnas == otras_columnas
        for a, b in zip(parametros(referencia), parametros(otra)):
            np.testing.assert_allclose(a, b, rtol=0, atol=1e-12)
        p = referencia.predict(X.loc[validar, columnas])
        q = otra.predict(X.loc[validar, otras_columnas])
        np.testing.assert_allclose(p, q, rtol=0, atol=1e-12)
        pruebas.append(dict(particion=nombre, prueba=caso, seleccion_identica=True,
                            parametros_identicos=True, diferencia_max_prediccion=float(np.max(np.abs(p-q)))))

    for nombre, entrenar, validar in contexto["pliegues"]:
        with threadpool_limits(limits=2):
            columnas, modelo = ejecutar_pliegue(nombre, entrenar, validar, X, y)
            almacenadas = originales.loc[originales.particion.eq(nombre)]
            np.testing.assert_allclose(modelo.predict(X.loc[validar, columnas]), almacenadas.estimado,
                                       rtol=0, atol=1e-10)
            etiquetas = y.copy()
            etiquetas.loc[~entrenar] = generador.permutation(y.loc[~entrenar].to_numpy())
            otras_columnas, otro = ejecutar_pliegue(nombre, entrenar, validar, X, etiquetas)
            verificar_invariancia(nombre, modelo, otro, columnas, otras_columnas, validar, "Etiquetas futuras permutadas")
            entradas = X.copy()
            entradas.loc[~entrenar] = entradas.loc[~entrenar] * 1000 + 1e6
            otras_columnas, otro = ejecutar_pliegue(nombre, entrenar, validar, entradas, y)
            verificar_invariancia(nombre, modelo, otro, columnas, otras_columnas, validar, "Predictores futuros alterados")

            for etiqueta, seleccion in [("29 entradas", X.columns.tolist()), ("15 entradas", columnas)]:
                n = len(X.loc[validar, seleccion].merge(X.loc[entrenar, seleccion].drop_duplicates(),
                                                      how="inner", on=seleccion))
                duplicados.append(dict(particion=nombre, conjunto=etiqueta, coincidencias_exactas=n))
                assert n == 0

            par = ["PTCA_8322A.AV_0#", "PTCA_8324.AV_0#"]
            limite = fechas.loc[validar].min()
            largo = fechas.lt(limite-pd.Timedelta(hours=1))
            columnas_largo, _ = seleccionar_variables(X.loc[largo], y.loc[largo])
            variantes = [("Campeona 15", entrenar, columnas),
                         ("Solo dos presiones PTCA", entrenar, par),
                         ("Campeona sin las dos PTCA", entrenar, [c for c in columnas if c not in par]),
                         ("Separacion de una hora", largo, columnas_largo)]
            for variante, entrenamiento, seleccion in variantes:
                m = crear_modelos()["Ridge"].fit(X.loc[entrenamiento, seleccion], y.loc[entrenamiento])
                p = m.predict(X.loc[validar, seleccion])
                error = np.abs(p-y.loc[validar].to_numpy())
                diagnosticos.append(dict(particion=nombre, variante=variante,
                                         n_entrenamiento=int(entrenamiento.sum()), n_entradas=len(seleccion),
                                         suma_error_abs=float(error.sum()), suma_abs_observado=float(y.loc[validar].abs().sum()),
                                         **calcular_metricas(y.loc[validar], p)))
        print(nombre, "verificada", flush=True)

    # Reproducir la regla real de elección, desde las métricas completas originales.
    validacion = pd.read_csv(RAIZ / "outputs/serie2_validacion.csv")
    resumen = validacion.groupby(["variante", "modelo"], as_index=False).agg(
        MAE_medio=("MAE", "mean"), MAE_peor_dia=("MAE", "max"), entradas_medias=("n_entradas", "mean"))
    eleccion = dict(comunes, resumen=resumen)
    exec(codigo[6], eleccion)
    decision = json.loads((RAIZ / "outputs/serie2_decision_antes_test.json").read_text(encoding="utf-8"))
    assert eleccion["decision"] == decision

    def ejecutar_final(entradas, etiquetas):
        entorno = dict(comunes, X=entradas, y=etiquetas, fechas=fechas,
                       base=contexto["base"], desarrollo=contexto["desarrollo"], test=contexto["test"],
                       inicio=contexto["inicio"], decision=decision, crear_modelos=crear_modelos)
        exec(codigo[8], entorno)
        return entorno["columnas_finales"], entorno["campeon"]

    with threadpool_limits(limits=2):
        desarrollo, test = contexto["desarrollo"], contexto["test"]
        columnas, modelo = ejecutar_final(X, y)
        for etiqueta, seleccion in [("29 entradas", X.columns.tolist()), ("15 entradas", columnas)]:
            n = len(X.loc[test, seleccion].merge(X.loc[desarrollo, seleccion].drop_duplicates(),
                                               how="inner", on=seleccion))
            duplicados.append(dict(particion="Comprobación reutilizada", conjunto=etiqueta, coincidencias_exactas=n))
            assert n == 0
        artefacto = joblib.load(RAIZ / "outputs/serie2_sensor_virtual.joblib")
        assert artefacto["columnas"] == columnas
        for a,b in zip(parametros(modelo), parametros(artefacto["modelo"])):
            np.testing.assert_allclose(a,b,rtol=0,atol=1e-12)
        etiquetas = y.copy()
        etiquetas.loc[~desarrollo] = generador.permutation(y.loc[~desarrollo].to_numpy())
        otras_columnas, otro = ejecutar_final(X, etiquetas)
        verificar_invariancia("Comprobación reutilizada", modelo, otro, columnas, otras_columnas,
                             test, "Etiquetas posteriores a desarrollo permutadas")
        entradas = X.copy()
        entradas.loc[~desarrollo] = entradas.loc[~desarrollo] * 1000 + 1e6
        otras_columnas, otro = ejecutar_final(entradas, y)
        verificar_invariancia("Comprobación reutilizada", modelo, otro, columnas, otras_columnas,
                             test, "Predictores posteriores a desarrollo alterados")
    # Comprobar las estadísticas del artefacto directamente con las filas permitidas.
    medianas = X.loc[desarrollo, columnas].median()
    limpio = X.loc[desarrollo, columnas].fillna(medianas)
    np.testing.assert_allclose(modelo[0].statistics_, medianas, rtol=0, atol=1e-12)
    np.testing.assert_allclose(modelo[1].mean_, limpio.mean(), rtol=0, atol=1e-10)
    np.testing.assert_allclose(modelo[1].scale_, limpio.std(ddof=0), rtol=0, atol=1e-10)
    assert int(modelo[1].n_samples_seen_) == int(desarrollo.sum()) == 34530
    assert all(hashlib.sha256((RAIZ/p).read_bytes()).hexdigest() == h for p,h in huellas.items())
    pd.DataFrame(pruebas).to_csv(salida / "pruebas_adversariales.csv", index=False)
    pd.DataFrame(duplicados).to_csv(salida / "duplicados_entre_particiones.csv", index=False)
    diagnosticos = pd.DataFrame(diagnosticos)
    diagnosticos.to_csv(salida / "diagnosticos.csv", index=False)
    resumen_diagnostico = diagnosticos.groupby("variante", as_index=False).agg(
        MAE_medio=("MAE", "mean"), peor_MAE=("MAE", "max"),
        suma_error_abs=("suma_error_abs", "sum"), suma_abs_observado=("suma_abs_observado", "sum"))
    resumen_diagnostico["WAPE_agregado_pct"] = 100*resumen_diagnostico.suma_error_abs/resumen_diagnostico.suma_abs_observado
    resumen_diagnostico.to_csv(salida / "resumen_diagnosticos.csv", index=False)
    informe = dict(pruebas_adversariales=len(pruebas), todas_aprobadas=True,
                   eleccion_reproducida=True, estadisticas_solo_desarrollo=True, n_desarrollo=34530,
                   filas_mismas_29_y_15_sin_cruce=True, artefacto_reproducido=True,
                   protecciones_sin_cambios=True, huellas=huellas,
                   independencia_instrumental="No demostrada con el CSV",
                   test_independiente=False, validaciones_reutilizadas=True)
    (salida / "verificacion.json").write_text(json.dumps(informe, ensure_ascii=False, indent=2), encoding="utf-8")
    print(resumen_diagnostico.to_string(index=False))
    print("Ocho pruebas adversariales aprobadas; campeona sin cambios.")


if __name__ == "__main__":
    main()
