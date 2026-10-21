"""Contrasta datos originales, máscaras y riesgo con ecuaciones NumPy."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


RAIZ = Path(__file__).resolve().parents[2]
OUT = RAIZ / "outputs/serie3_precios"


def reconstruir():
    crudo = pd.read_csv(RAIZ / "data/raw/serie3/Sugar_data.csv",parse_dates=["date"])
    r = np.full(len(crudo),np.nan)
    r[1:] = np.log(crudo.close.to_numpy()[1:]/crudo.close.to_numpy()[:-1])
    alto = crudo[["open","low","close"]].to_numpy().max(axis=1)
    bajo = crudo[["open","high","close"]].to_numpy().min(axis=1)
    bad = (crudo.high.to_numpy()+1e-5 < alto) | (crudo.low.to_numpy()-1e-5 > bajo)
    cero = crudo.volume.to_numpy()==0
    marca_calidad = bad | np.r_[False,bad[:-1]] | cero | np.r_[False,cero[:-1]]
    meses = crudo.date.dt.strftime("%Y-%m").to_numpy()
    grupos = [(mes,np.flatnonzero(meses==mes)) for mes in np.unique(meses)]
    calendario = np.zeros(len(crudo),dtype=bool)
    for mes,idx in grupos:
        mm = int(mes[-2:])
        if mm in [2,4,6,9] and mes != meses[-1]: calendario[idx[-1]]=True
        if mm in [3,5,7,10] and mes != meses[0]: calendario[idx[0]]=True
    admisible = np.isfinite(r) & ~calendario & ~marca_calidad
    return crudo,r,bad,cero,calendario,admisible


def test_fuente_conservacion_y_retornos_no_recalculados_sobre_filas_filtradas():
    crudo,r,bad,cero,calendario,admisible = reconstruir()
    p = pd.read_csv(OUT / "precios_y_marcas.csv",parse_dates=["date"])
    d = json.loads((OUT / "decision.json").read_text(encoding="utf-8"))
    pd.testing.assert_frame_equal(crudo,p[crudo.columns])
    assert len(p)==6097 and admisible.sum()==5748
    np.testing.assert_array_equal(p.proxy_enlace,calendario)
    np.testing.assert_array_equal(p.ohlc_incoherente,bad)
    np.testing.assert_array_equal(p.volumen_cero,cero)
    np.testing.assert_array_equal(p.admisible_sensibilidad,admisible)
    np.testing.assert_allclose(p.retorno_log,r,equal_nan=True,atol=1e-15)
    fuera = pd.read_csv(OUT / "retornos_fuera_sensibilidad.csv",parse_dates=["date"])
    pd.testing.assert_frame_equal(fuera[crudo.columns].reset_index(drop=True),crudo.loc[~admisible].reset_index(drop=True))
    assert fuera.motivo_fuera_sensibilidad.notna().all() and len(fuera)==349
    assert d["retornos_proxy_enlace"]==194 and np.sum(bad & calendario)==11
    assert not p.proxy_enlace.iloc[-1]  # Junio acaba el día 24, no en vencimiento.
    assert hashlib.sha256((RAIZ/'data/raw/serie3/Sugar_data.csv').read_bytes()).hexdigest()==d['fuente_sha256']
    assert not d['ajuste_de_enlaces'] and not d['serie_restringida_certificada']


def test_volatilidad_estados_y_extremos_reconstruidos_con_ventanas_originales():
    crudo,r,_,_,_,admisible = reconstruir()
    p = pd.read_csv(OUT / "precios_y_marcas.csv")
    resumen = pd.read_csv(OUT / "sensibilidad_retornos.csv").set_index('variante')
    for nombre,mask in [('observada',np.isfinite(r)),('restringida',admisible)]:
        x=r[mask]
        np.testing.assert_allclose(resumen.loc[nombre,'vol_anualizada_pct'],np.sqrt(np.sum((x-x.mean())**2)/(len(x)-1))*np.sqrt(252)*100)
        np.testing.assert_allclose(resumen.loc[nombre,'q01_simple_pct'],np.percentile(np.expm1(x)*100,1))
    restringidos=np.where(admisible,r,np.nan)
    v=np.full(len(r),np.nan)
    for i in range(63,len(r)):
        x=restringidos[i-62:i+1]; x=x[np.isfinite(x)]
        if len(x)>=50: v[i]=np.std(x,ddof=1)*np.sqrt(252)*100
    np.testing.assert_allclose(p.vol_63_restringida_pct,v,equal_nan=True,atol=1e-10)
    limites=np.nanpercentile(v,[25,75])
    estado=np.select([~np.isfinite(v),v<=limites[0],v<=limites[1]],['sin_cobertura','baja','intermedia'],default='alta')
    np.testing.assert_array_equal(p.estado_63,estado)
    np.testing.assert_array_equal(p.extremo_p99_observado,np.abs(r)>=np.nanpercentile(np.abs(r),99))
    np.testing.assert_array_equal(p.extremo_p99_restringido,np.abs(restringidos)>=np.nanpercentile(np.abs(restringidos),99))
    episodios=pd.read_csv(OUT/'episodios_estados.csv')
    cambios=np.r_[0,np.flatnonzero(estado[1:]!=estado[:-1])+1,len(estado)]
    np.testing.assert_array_equal(episodios.sesiones,np.diff(cambios))
    np.testing.assert_array_equal(episodios.estado,estado[cambios[:-1]])
    contraste=pd.read_csv(OUT/'contraste_externo.csv')
    assert contraste.diferencia_cent_lb.abs().max()<.005
