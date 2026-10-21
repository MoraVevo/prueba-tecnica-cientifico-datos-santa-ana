"""Reconstruye pronósticos y bandas desde el crudo sin helpers productivos."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


RAIZ=Path(__file__).resolve().parents[2]
OUT=RAIZ/"outputs/serie3_pronostico"


def reconstruir_mensual():
    crudo=pd.read_csv(RAIZ/"data/raw/serie3/Sugar_data.csv",parse_dates=["date"])
    p=crudo[crudo.date<pd.Timestamp("2024-06-01")].copy()
    meses=p.date.dt.strftime("%Y-%m").to_numpy()
    nombres=np.unique(meses)
    y=np.array([np.mean(p.loc[meses==mes,"close"].values) for mes in nombres])
    cierre=np.array([p.loc[meses==mes,"close"].values[-1] for mes in nombres])
    x=np.full((len(y),3),np.nan)
    x[:,0]=np.log(cierre/y)
    x[1:,1]=np.log(y[1:]/y[:-1])
    x[3:,2]=np.log(y[3:]/y[:-3])
    return crudo,nombres,y,cierre,x


def test_agregacion_y_todas_las_predicciones_con_etiquetas_maduras_por_ecuacion():
    crudo,nombres,y,cierre,x=reconstruir_mensual()
    m=pd.read_csv(OUT/"mensual.csv")
    np.testing.assert_allclose(m.precio,y)
    np.testing.assert_allclose(m.cierre,cierre)
    assert len(m)==291 and m.n_dias.sum()==6082
    fuera=pd.read_csv(OUT/"filas_fuera_mensual.csv",parse_dates=["date"])
    pd.testing.assert_frame_equal(fuera[crudo.columns].reset_index(drop=True),crudo[crudo.date>=pd.Timestamp("2024-06-01")].reset_index(drop=True))
    assert len(fuera)==15 and fuera.motivo.notna().all()
    pred=pd.read_csv(OUT/"predicciones_historicas.csv")
    for fila in pred.itertuples():
        t=np.flatnonzero(nombres==fila.origen)[0]; h=fila.horizonte
        assert nombres[t+h]==fila.objetivo
        np.testing.assert_allclose(fila.observado,y[t+h])
        if fila.metodo.startswith("ingenuo"):
            esperado=cierre[t] if fila.metodo=="ingenuo_cierre" else y[t]
        else:
            j=np.arange(3,t-h+1)
            assert (j+h).max()==t
            a=x[j]; centro=a.mean(axis=0); escala=a.std(axis=0)
            z=(a-centro)/escala
            target=np.log(y[j+h]/cierre[j]); intercepto=target.mean()
            coef=np.linalg.solve(z.T@z+int(fila.metodo.split('_')[1])*np.eye(3),z.T@(target-intercepto))
            esperado=cierre[t]*np.exp(intercepto+((x[t]-centro)/escala)@coef)
        np.testing.assert_allclose(fila.prediccion,esperado,atol=1e-10,rtol=1e-10)
    parametros=[json.loads(s) for s in (OUT/'parametros_ajustes.jsonl').read_text(encoding='utf-8').splitlines()]
    assert all(a['ultimo_objetivo_ajuste']<=a['origen'] for a in parametros)
    decision=json.loads((OUT/'decision.json').read_text(encoding='utf-8'))
    assert hashlib.sha256((RAIZ/'data/raw/serie3/Sugar_data.csv').read_bytes()).hexdigest()==decision['fuente_sha256']


def test_particiones_seleccion_cuantiles_cobertura_y_pronostico_final_independientes():
    p=pd.read_csv(OUT/'predicciones_historicas.csv')
    d=json.loads((OUT/'decision.json').read_text(encoding='utf-8'))
    assert p[p.fase.eq('seleccion')].objetivo.max() < p[p.fase.eq('calibracion')].origen.min()
    assert p[p.fase.eq('calibracion')].objetivo.max() < p[p.fase.eq('evaluacion')].origen.min()
    q=pd.read_csv(OUT/'cuantiles_calibracion.csv')
    bandas=pd.read_csv(OUT/'intervalos_evaluacion.csv')
    resumen_bandas=pd.read_csv(OUT/'metricas_intervalos.csv')
    tabla=pd.read_csv(OUT/'metricas_puntuales.csv')
    finales=pd.read_csv(OUT/'pronosticos_ultimo_origen.csv')
    for h in [1,3]:
        seleccion=p[p.fase.eq('seleccion') & p.horizonte.eq(h)]
        errores={metodo:np.mean(np.abs(g.prediccion-g.observado)) for metodo,g in seleccion.groupby('metodo')}
        orden=['ingenuo_cierre','ingenuo_media','ridge_100','ridge_10','ridge_1']
        elegido=next(n for n in orden if errores[n]<=1.02*min(errores.values()))
        assert d['seleccionados'][str(h)]==elegido=='ingenuo_cierre'
        for metodo in orden:
            test=p[p.fase.eq('evaluacion') & p.horizonte.eq(h) & p.metodo.eq(metodo)]
            assert len(test)==(64 if h==1 else 62)
            a=tabla[tabla.fase.eq('evaluacion') & tabla.horizonte.eq(h) & tabla.metodo.eq(metodo)].iloc[0]
            np.testing.assert_allclose(a.MAE,np.mean(np.abs(test.prediccion-test.observado)))
            np.testing.assert_allclose(a.WAPE_pct,100*np.sum(np.abs(test.prediccion-test.observado))/np.sum(test.observado))
            cal=p[p.fase.eq('calibracion') & p.horizonte.eq(h) & p.metodo.eq(metodo)]
            for cobertura in [.8,.95]:
                k=int(np.ceil((len(cal)+1)*cobertura))
                umbral=np.sort(np.abs(np.log(cal.observado/cal.prediccion)))[k-1]
                registro=q[q.horizonte.eq(h) & q.metodo.eq(metodo) & q.cobertura_nominal.eq(cobertura)].iloc[0]
                assert registro.orden==k and registro.n_calibracion==57
                np.testing.assert_allclose(registro.q_log,umbral)
                b=bandas[bandas.horizonte.eq(h) & bandas.metodo.eq(metodo) & bandas.cobertura_nominal.eq(cobertura)]
                inferior=b.prediccion*np.exp(-umbral); superior=b.prediccion*np.exp(umbral)
                np.testing.assert_allclose(b.inferior,inferior)
                np.testing.assert_allclose(b.superior,superior)
                np.testing.assert_array_equal(b.cubierto,(b.observado>=inferior)&(b.observado<=superior))
                score=(superior-inferior)+2/(1-cobertura)*(np.maximum(inferior-b.observado,0)+np.maximum(b.observado-superior,0))
                np.testing.assert_allclose(b.winkler,score)
                resumen=resumen_bandas[resumen_bandas.horizonte.eq(h) & resumen_bandas.metodo.eq(metodo) & resumen_bandas.cobertura_nominal.eq(cobertura)].iloc[0]
                assert resumen.aciertos==int(((b.observado>=inferior)&(b.observado<=superior)).sum())
                np.testing.assert_allclose(resumen.amplitud_media,np.mean(superior-inferior))
                np.testing.assert_allclose(resumen.Winkler_medio,np.mean(score))
                f=finales[finales.horizonte.eq(h) & finales.metodo.eq(metodo)].iloc[0]
                np.testing.assert_allclose(f[f'inferior_{int(cobertura*100)}'],f.prediccion*np.exp(-umbral))
    assert finales[finales.seleccionado].objetivo.tolist()==['2024-06','2024-08']
    _,_,_,cierre,_=reconstruir_mensual()
    np.testing.assert_allclose(finales[finales.seleccionado].prediccion,cierre[-1])
    assert not d['pronostico_actual'] and not d['continuidad_contratos_certificada']
