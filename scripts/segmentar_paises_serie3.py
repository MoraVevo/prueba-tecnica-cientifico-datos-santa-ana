"""Perfiles productivos y referencia de productividad territorial, Serie III.1."""

import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler


VENTANAS = ((1961, 1970), (1971, 1980), (1981, 1990),
            (1991, 2000), (2001, 2010), (2011, 2023))
RASGOS = ["log_area_reciente", "log_rendimiento_reciente", "tendencia_area_pct",
          "tendencia_rendimiento_pct", "variabilidad_area_log", "variabilidad_rendimiento_log"]
ESTRUCTURA = ["log_area_reciente", "tendencia_area_pct", "variabilidad_area_log"]


def representar(largo, cobertura=.6, reciente=(2019, 2023)):
    """Sin imputación: cobertura común por bloques y cuatro de cinco años recientes.

    Los ceros son válidos en el crudo; las características logarítmicas requieren
    operación positiva y se conserva qué tripletas quedan fuera por esa razón.
    """
    datos = largo[largo.ano <= reciente[1]].copy()
    tabla = datos.pivot(index=["area", "ano"], columns="elemento", values="valor").reset_index()
    tabla["tripleta_positiva"] = tabla[["Area harvested", "Yield", "Production"]].gt(0).all(axis=1)
    tabla["motivo_fuera_rasgos"] = np.where(tabla.tripleta_positiva, "", "tripleta_ausente_o_no_positiva")
    filas, criterios, bloques = [], [], []
    for area, g in tabla.groupby("area", sort=True):
        razones = []
        for inicio, fin in VENTANAS:
            fin = min(fin, reciente[1])
            if fin < inicio:
                continue
            ventana = g[g.ano.between(inicio, fin) & g.tripleta_positiva]
            minimo = int(np.ceil(cobertura * (fin - inicio + 1)))
            bloques.append({"area": area, "inicio": inicio, "fin": fin,
                            "n_positivas": len(ventana), "minimo": minimo,
                            "area_mediana_ha": ventana["Area harvested"].median(),
                            "rendimiento_mediano_kg_ha": ventana.Yield.median(),
                            "produccion_mediana_t": ventana.Production.median(),
                            "ano_central": ventana.ano.median()})
            if len(ventana) < minimo:
                razones.append(f"cobertura_insuficiente_{inicio}_{fin}")
        r = g[g.ano.between(*reciente) & g.tripleta_positiva]
        if len(r) < 4:
            razones.append("menos_de_4_anos_recientes_positivos")
        criterios.append({"area": area, "elegible": not razones,
                          "motivo": ";".join(razones), "n_recientes": len(r),
                          "n_positivas": int(g.tripleta_positiva.sum())})
        if razones:
            continue
        b = [f for f in bloques if f["area"] == area]
        b = pd.DataFrame(b)
        rasgos = {"area": area, "area_reciente_ha": r["Area harvested"].median(),
                  "rendimiento_reciente_kg_ha": r.Yield.median(),
                  "produccion_reciente_t": r.Production.median()}
        for elemento, nombre, campo in [("Area harvested", "area", "area_mediana_ha"),
                                         ("Yield", "rendimiento", "rendimiento_mediano_kg_ha")]:
            rasgos[f"log_{nombre}_reciente"] = np.log(rasgos[f"{nombre}_reciente_ha" if nombre == "area" else "rendimiento_reciente_kg_ha"])
            pendiente = np.polyfit(b.ano_central, np.log(b[campo]), 1)[0]
            rasgos[f"tendencia_{nombre}_pct"] = 100 * np.expm1(pendiente)
            positivas = g[g.tripleta_positiva].sort_values("ano")
            cambio = np.log(positivas[elemento]).diff()[positivas.ano.diff().eq(1)].dropna()
            rasgos[f"variabilidad_{nombre}_log"] = 100 * 1.4826 * (cambio - cambio.median()).abs().median()
        rasgos["tendencia_produccion_pct"] = 100 * np.expm1(np.polyfit(b.ano_central, np.log(b.produccion_mediana_t), 1)[0])
        filas.append(rasgos)
    return pd.DataFrame(filas).set_index("area"), pd.DataFrame(criterios), pd.DataFrame(bloques), tabla


def agrupar(rasgos, columnas=RASGOS, k=None, semilla=42):
    """Estandarización y K-means; elección K sin observar identidad de Guatemala."""
    escala = StandardScaler().fit(rasgos[columnas])
    z = escala.transform(rasgos[columnas])
    diagnostico = []
    modelos = {}
    for n in ([k] if k else [2, 3, 4]):
        modelo = KMeans(n_clusters=n, n_init=30, random_state=semilla).fit(z)
        tamanos = np.bincount(modelo.labels_)
        diagnostico.append({"k": n, "silueta": silhouette_score(z, modelo.labels_),
                            "menor_grupo": int(tamanos.min()), "inercia": modelo.inertia_})
        modelos[n] = modelo
    d = pd.DataFrame(diagnostico)
    if k is None:
        admisibles = d[d.menor_grupo >= 5]
        assert len(admisibles), "Ningún K produce grupos de tamaño suficiente: revisar el diseño."
        mejor = admisibles.silueta.max()
        k = int(admisibles[admisibles.silueta >= mejor - .02].k.min())
    modelo = modelos[k]
    # IDs ordenados por rendimiento reciente, para facilitar lectura, sin definir eficiencia.
    orden = pd.Series(modelo.labels_, index=rasgos.index).groupby(modelo.labels_).apply(
        lambda etiquetas: rasgos.loc[etiquetas.index, "rendimiento_reciente_kg_ha"].median()).sort_values().index
    mapa = {int(original): i + 1 for i, original in enumerate(orden)}
    etiquetas = pd.Series([mapa[int(g)] for g in modelo.labels_], index=rasgos.index, name="grupo")
    return etiquetas, d, escala, modelo


def buscar_pares(rasgos, cantidad=5, factor=4):
    """Vecinos por estructura de tierra, sin rendimiento ni producción como entradas."""
    escala = StandardScaler().fit(rasgos[ESTRUCTURA])
    z = pd.DataFrame(escala.transform(rasgos[ESTRUCTURA]), index=rasgos.index, columns=ESTRUCTURA)
    distancia = np.sqrt(((z - z.loc["Guatemala"]) ** 2).mean(axis=1))
    cociente = rasgos.area_reciente_ha / rasgos.loc["Guatemala", "area_reciente_ha"]
    candidatos = pd.DataFrame({"distancia": distancia, "ratio_area_a_GT": cociente})
    candidatos["admisible"] = candidatos.index.to_series().ne("Guatemala") & cociente.between(1/factor, factor)
    candidatos["elegido"] = False
    nombres = candidatos[candidatos.admisible].nsmallest(cantidad, "distancia").index
    assert len(nombres) == cantidad
    candidatos.loc[nombres, "elegido"] = True
    return candidatos.sort_values("distancia")


def referencia_productividad(largo, pares, solo_oficial=False, reciente=(2019, 2023)):
    """Referencia anual de los mismos pares, sin incorporar Guatemala al denominador."""
    datos = largo[largo.elemento.eq("Yield") & largo.ano.between(*reciente)].copy()
    filas = []
    for ano in range(reciente[0], reciente[1] + 1):
        g = datos[(datos.ano == ano) & datos.area.isin(pares)]
        if solo_oficial:
            g = g[g.flag == "A"]
        valores = g.loc[g.valor > 0, "valor"]
        gt = datos[(datos.ano == ano) & datos.area.eq("Guatemala")]
        gt_val = gt.valor.iloc[0]
        gt_flag = gt.flag.iloc[0]
        # Al menos tres referencias positivas y, en sensibilidad A, GT también oficial.
        suficiente = len(valores) >= 3 and (not solo_oficial or gt_flag == "A")
        mediana, p75 = (valores.median(), valores.quantile(.75)) if suficiente else (np.nan, np.nan)
        filas.append({"ano": ano, "n_pares": len(valores), "gt_kg_ha": gt_val,
                      "gt_flag": gt_flag, "mediana_pares_kg_ha": mediana, "p75_pares_kg_ha": p75,
                      "ratio_GT_mediana": gt_val / mediana, "ratio_GT_p75": gt_val / p75,
                      "solo_oficial": solo_oficial})
    return pd.DataFrame(filas)


def ejecutar(raiz):
    raiz = Path(raiz)
    salida = raiz / "outputs/serie3_segmentacion"
    salida.mkdir(parents=True, exist_ok=True)
    entrada = raiz / "outputs/serie3_eda/revision/cana_paises.csv"
    huella = hashlib.sha256(entrada.read_bytes()).hexdigest()
    largo = pd.read_csv(entrada)
    f, elegibilidad, bloques, tripletas = representar(largo)
    etiquetas, diagnostico, escala, modelo = agrupar(f)
    grupos = f.join(etiquetas)
    grupos.to_csv(salida / "paises_y_rasgos.csv")
    elegibilidad.to_csv(salida / "elegibilidad.csv", index=False)
    bloques.to_csv(salida / "bloques.csv", index=False)
    tripletas.to_csv(salida / "tripletas_y_marcas.csv", index=False)
    excluidas = largo[~largo.area.isin(f.index)].copy()
    excluidas = excluidas.merge(elegibilidad[["area", "motivo"]], on="area", validate="many_to_one")
    excluidas.to_csv(salida / "filas_fuera_segmentacion.csv", index=False)
    tripletas[~tripletas.tripleta_positiva].to_csv(salida / "tripletas_fuera_rasgos.csv", index=False)
    diagnostico.to_csv(salida / "eleccion_k.csv", index=False)
    perfiles = grupos.groupby("grupo").median(numeric_only=True)
    perfiles["n_areas"] = grupos.groupby("grupo").size()
    perfiles.to_csv(salida / "perfiles.csv")
    candidatos = buscar_pares(f)
    pares = candidatos.index[candidatos.elegido].tolist()
    candidatos.join(grupos).to_csv(salida / "pares_y_candidatos.csv")
    referencia = pd.concat([referencia_productividad(largo, pares),
                            referencia_productividad(largo, pares, solo_oficial=True)])
    referencia.to_csv(salida / "referencia_productividad.csv", index=False)
    # Calidad se muestra, no se convierte en puntuación de exactitud.
    calidad = largo[largo.area.isin(f.index)].groupby(["area", "elemento"]).agg(
        observadas=("valor", "count"), oficiales=("flag", lambda a: a.eq("A").sum()),
        estimadas_imputadas_externas=("flag", lambda a: a.isin(["E", "I", "X"]).sum()),
    ).reset_index()
    calidad["proporcion_A"] = calidad.oficiales / calidad.observadas
    calidad.to_csv(salida / "calidad_paises.csv", index=False)
    calidad.merge(etiquetas.reset_index(), on="area").groupby(["grupo", "elemento"]).proporcion_A.median().to_csv(
        salida / "calidad_por_grupo.csv")
    largo[largo.area.isin(["Guatemala", *pares])].to_csv(salida / "guatemala_pares_celdas.csv", index=False)
    recientes = largo[largo.area.isin(["Guatemala", *pares]) & largo.ano.isin([2019,2023])].pivot(
        index=["area", "elemento"], columns="ano", values="valor")
    recientes["cambio_2019_2023_pct"] = 100 * (recientes[2023] / recientes[2019] - 1)
    recientes.to_csv(salida / "evolucion_reciente.csv")
    oficiales = largo.copy()
    retiradas_A = oficiales[oficiales.flag.ne("A")].copy()
    retiradas_A["motivo"] = "sin_flag_A_solo_para_sensibilidad"
    retiradas_A.to_csv(salida / "filas_fuera_sensibilidad_A.csv", index=False)
    oficiales.loc[oficiales.flag.ne("A"), "valor"] = np.nan
    _, elegibilidad_A, _, _ = representar(oficiales)
    elegibilidad_A.to_csv(salida / "elegibilidad_solo_A.csv", index=False)
    coherencia = pd.read_csv(raiz / "outputs/serie3_eda/revision/coherencia_area_rendimiento_produccion.csv")
    coherencia[coherencia.revisar & coherencia.en_ambito_paises].to_csv(salida / "revision_aritmetica.csv", index=False)
    sensibilidades, recurrencia, referencias_alt = [], [], []
    configuraciones = [("K2", .6, (2019,2023), RASGOS, 2, 4),
                       ("K3", .6, (2019,2023), RASGOS, 3, 4),
                       ("K4", .6, (2019,2023), RASGOS, 4, 4),
                       ("cobertura_50", .5, (2019,2023), RASGOS, modelo.n_clusters, 4),
                       ("cobertura_80", .8, (2019,2023), RASGOS, modelo.n_clusters, 4),
                       ("ventana_2014_2018", .6, (2014,2018), RASGOS, modelo.n_clusters, 4),
                       ("sin_variabilidad", .6, (2019,2023), RASGOS[:4], modelo.n_clusters, 4),
                       ("area_factor2", .6, (2019,2023), RASGOS, modelo.n_clusters, 2),
                       ("tres_pares", .6, (2019,2023), RASGOS, modelo.n_clusters, 4),
                       ("ocho_pares", .6, (2019,2023), RASGOS, modelo.n_clusters, 4)]
    for nombre, cobertura, reciente, columnas, k, factor in configuraciones:
        alt, _, _, _ = representar(largo, cobertura, reciente)
        labels, _, _, _ = agrupar(alt, columnas, k)
        comunes = f.index.intersection(alt.index)
        grupo_gt_base = set(etiquetas.index[etiquetas == etiquetas.loc["Guatemala"]])
        grupo_gt_alt = set(labels.index[labels == labels.loc["Guatemala"]])
        # Sensibilidad de pares excluye variabilidad también de su distancia.
        if nombre == "sin_variabilidad":
            alterada = alt.copy()
            alterada["variabilidad_area_log"] = 0.
        else:
            alterada = alt
        cantidad = {"tres_pares": 3, "ocho_pares": 8}.get(nombre, 5)
        pp = buscar_pares(alterada, cantidad=cantidad, factor=factor)
        nombres = pp.index[pp.elegido].tolist()
        sensibilidades.append({"escenario": nombre, "n_areas": len(alt),
            "ARI_comunes": adjusted_rand_score(etiquetas.loc[comunes], labels.loc[comunes]),
            "Jaccard_grupo_GT": len(grupo_gt_base & grupo_gt_alt) / len(grupo_gt_base | grupo_gt_alt),
            "Jaccard_pares": len(set(pares) & set(nombres)) / len(set(pares) | set(nombres)),
            "pares": ";".join(nombres)})
        recurrencia.extend({"escenario": nombre, "area": a, "elegido": a in nombres} for a in alt.index)
        if reciente == (2019,2023):
            ref = referencia_productividad(largo, nombres)
            ref["escenario"] = nombre
            referencias_alt.append(ref)
    for semilla in [43, 44, 45]:
        labels, _, _, _ = agrupar(f, k=modelo.n_clusters, semilla=semilla)
        sensibilidades.append({"escenario": f"semilla_{semilla}", "n_areas": len(f),
                               "ARI_comunes": adjusted_rand_score(etiquetas, labels)})
    ward = AgglomerativeClustering(n_clusters=modelo.n_clusters).fit_predict(escala.transform(f[RASGOS]))
    sensibilidades.append({"escenario": "Ward", "n_areas": len(f),
                           "ARI_comunes": adjusted_rand_score(etiquetas, ward)})
    pd.DataFrame(sensibilidades).to_csv(salida / "sensibilidad.csv", index=False)
    pd.DataFrame(recurrencia).to_csv(salida / "recurrencia_pares.csv", index=False)
    pd.concat(referencias_alt).to_csv(salida / "referencias_sensibilidad.csv", index=False)
    joblib.dump({"escalador": escala, "modelo": modelo, "rasgos": RASGOS,
                 "etiquetas": etiquetas.to_dict()}, salida / "modelo_perfiles.joblib")
    decision = {"periodo": [1961,2023], "reciente": [2019,2023], "cobertura_bloque": .6,
                "ventanas": VENTANAS, "rasgos": RASGOS, "rasgos_pares": ESTRUCTURA,
                "k": modelo.n_clusters, "criterio_k": "menor K a 0.02 de mejor silueta, grupos >=5",
                "numero_pares": 5, "factor_superficie": 4,
                "n_areas_entrada": largo.area.nunique(), "n_areas_elegibles": len(f),
                "filas_entrada": len(largo), "filas_fuera_segmentacion": len(excluidas),
                "grupo_GT": int(etiquetas.loc["Guatemala"]), "pares_GT": pares,
                "ratio_GT_mediana_reciente": referencia.loc[~referencia.solo_oficial, "ratio_GT_mediana"].median(),
                "ratio_GT_p75_reciente": referencia.loc[~referencia.solo_oficial, "ratio_GT_p75"].median(),
                "fuente_sha256": huella, "recursos_naturales_observados": False,
                "costos_observados": False, "imputacion": False}
    assert hashlib.sha256(entrada.read_bytes()).hexdigest() == huella
    (salida / "decision.json").write_text(json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8")
    return decision


if __name__ == "__main__":
    print(json.dumps(ejecutar(Path(__file__).resolve().parents[1]), ensure_ascii=True, indent=2))
