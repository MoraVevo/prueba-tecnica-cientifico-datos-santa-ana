"""Garantías temporales: datos disponibles, selección y calibración separadas."""

import numpy as np
import pandas as pd

from scripts.pronosticar_azucar_serie3 import (
    mensualizar, predecir, seleccionar, cuantil_banda, puntuar_intervalo, PRIORIDAD)


def fuente_sintetica():
    filas = []
    for i,mes in enumerate(pd.period_range("2014-01","2024-06",freq="M")):
        nivel = 20 + 2*np.sin(i/3) + i/50
        for fecha,precio in [(mes.start_time,nivel*.98),(mes.end_time.normalize(),nivel*1.02)]:
            if mes == pd.Period("2024-06","M") and fecha.day > 24:
                continue
            filas.append({"date":str(fecha.date()),"open":precio,"high":precio+.05,
                "low":precio-.05,"close":precio,"volume":100})
    return pd.DataFrame(filas)


def test_promedio_mensual_excluye_mes_parcial_conservando_filas_y_sin_imputacion():
    crudo=fuente_sintetica(); copia=crudo.copy(deep=True)
    m,fuera=mensualizar(crudo)
    pd.testing.assert_frame_equal(crudo,copia)
    assert str(m.index[-1])=="2024-05" and len(fuera)==1
    assert fuera.motivo.eq("mes_incompleto_en_fuente").all()
    assert m.n_dias.sum()+len(fuera)==len(crudo)
    np.testing.assert_allclose(m.precio.iloc[0],20.)
    assert m.cambio_media_3m.iloc[:3].isna().all()


def test_objetivos_de_ridge_maduros_y_prediccion_invariante_al_futuro():
    m,_=mensualizar(fuente_sintetica())
    origen=80
    modificada=m.copy()
    modificada.loc[modificada.index>m.index[origen],["precio","cierre"]] *= 1000
    modificada["log_cierre_sobre_media"]=np.log(modificada.cierre/modificada.precio)
    modificada["cambio_media_1m"]=np.log(modificada.precio/modificada.precio.shift())
    modificada["cambio_media_3m"]=np.log(modificada.precio/modificada.precio.shift(3))
    for h in [1,3]:
        for metodo in PRIORIDAD:
            a,detalle,_=predecir(m,origen,h,metodo)
            b,detalle_futuro,_=predecir(modificada,origen,h,metodo)
            assert a==b and detalle==detalle_futuro
            if detalle:
                assert detalle["ultimo_objetivo_ajuste"]==str(m.index[origen])
                assert detalle["ultimo_origen_ajuste"]==str(m.index[origen-h])
                assert detalle["n_ajuste"]==origen-h-2


def test_seleccion_ignora_calibracion_y_evaluacion_y_prefiere_parsimonia():
    filas=[]
    errores={"ingenuo_cierre":1.,"ingenuo_media":1.01,"ridge_100":.99,"ridge_10":.98,"ridge_1":1.02}
    for h in [1,3]:
        for fase in ["seleccion","calibracion","evaluacion"]:
            for metodo,error in errores.items():
                filas.append({"horizonte":h,"fase":fase,"metodo":metodo,"observado":10.,"prediccion":10+error})
    p=pd.DataFrame(filas)
    esperado=seleccionar(p)
    assert esperado=={"1":"ridge_100","3":"ridge_100"}
    # El cierre (1.00) está fuera de 2 % de 0.98: no se altera la tolerancia.
    p.loc[~p.fase.eq("seleccion"),"prediccion"]=1e8
    assert seleccionar(p)==esperado
    p.loc[p.fase.eq("seleccion") & p.metodo.eq("ingenuo_cierre"),"prediccion"]=10.999
    assert seleccionar(p)=={"1":"ingenuo_cierre","3":"ingenuo_cierre"}


def test_cuantiles_y_winkler_con_resultados_conocidos():
    errores=np.arange(1,58)/100
    assert cuantil_banda(errores,.8)==(.47,47)
    assert cuantil_banda(errores,.95)==(.56,56)
    np.testing.assert_allclose(puntuar_intervalo(np.array([8,11,14]),10,12,.8),[22,2,22])
