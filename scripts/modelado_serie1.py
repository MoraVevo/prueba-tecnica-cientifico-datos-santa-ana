"""Historia y modelos del notebook 04, compartidos con las pruebas."""

import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeRegressor


CATEGORICAS = ["CLONE", "LOC", "STAGE"]
NUMERICAS = ["YEAR", "CROP", "HIST_CLONE", "HIST_LOC", "HIST_CLONE_CROP"]
ENTRADAS = CATEGORICAS + NUMERICAS


def agregar_historia(tabla):
    """Añade medias del objetivo de años estrictamente anteriores."""
    resultado = tabla.copy()
    grupos = [(["CLONE"], "HIST_CLONE"), (["LOC"], "HIST_LOC"), (["CLONE", "CROP"], "HIST_CLONE_CROP")]
    for anio in sorted(tabla["YEAR"].unique()):
        pasado = tabla.loc[tabla["YEAR"].lt(anio)]
        actuales = tabla.loc[tabla["YEAR"].eq(anio)]
        for claves, nombre in grupos:
            historia = pasado.groupby(claves, as_index=False)["T_SPACRE"].mean().rename(columns={"T_SPACRE": nombre})
            valores = actuales[claves].merge(historia, on=claves, how="left", validate="many_to_one")[nombre]
            resultado.loc[actuales.index, nombre] = valores.to_numpy()
    return resultado


def referencia_reciente(entrenamiento, evaluacion):
    """Usa clon/ambiente del último año y respaldos calculados en entrenamiento."""
    claves = ["CLONE", "LOC", "STAGE", "CROP"]
    reciente = entrenamiento.loc[entrenamiento["YEAR"].eq(entrenamiento["YEAR"].max())]
    prediccion = evaluacion[claves].join(reciente.groupby(claves)["T_SPACRE"].mean().rename("PRED"), on=claves)["PRED"]
    historica = evaluacion[claves].join(entrenamiento.groupby(claves)["T_SPACRE"].mean().rename("PRED"), on=claves)["PRED"]
    por_corte = evaluacion[["STAGE", "CROP"]].join(entrenamiento.groupby(["STAGE", "CROP"])["T_SPACRE"].mean().rename("PRED"), on=["STAGE", "CROP"])["PRED"]
    return prediccion.fillna(historica).fillna(por_corte).fillna(entrenamiento["T_SPACRE"].mean())


def crear_modelos():
    """Crea los tres pipelines; sus transformaciones se ajustan al llamar fit."""
    preparacion = ColumnTransformer([
        ("categorias", OneHotEncoder(handle_unknown="ignore", min_frequency=5), CATEGORICAS),
        ("numeros", Pipeline([("imputar", SimpleImputer(strategy="median")), ("escalar", StandardScaler())]), NUMERICAS),
    ])
    algoritmos = {
        "Ridge interpretable": Ridge(alpha=10, solver="lsqr"),
        "Árbol de decisión": DecisionTreeRegressor(max_depth=6, min_samples_leaf=20, random_state=42),
        "Bosque aleatorio": RandomForestRegressor(n_estimators=120, max_depth=18, min_samples_leaf=5, max_features=0.8, n_jobs=-1, random_state=42),
    }
    return {
        nombre: Pipeline([("preparar", clone(preparacion)), ("regresor", algoritmo)])
        for nombre, algoritmo in algoritmos.items()
    }
