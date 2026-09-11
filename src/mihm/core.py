from __future__ import annotations
import numpy as np

EPS=1e-12

def robust_reference(x, floor=0.01):
    x=np.asarray(x,dtype=float)
    med=float(np.median(x))
    mad=float(np.median(np.abs(x-med)))
    a=1.4826*mad
    q25,q75=np.percentile(x,[25,75])
    iqr=float(q75-q25)
    scale=a if a>=floor else max(a, iqr/1.349, floor)
    return {"center":med,"scale":float(scale),"mad_scaled":float(a),"iqr":iqr}

def normalized_distance(value, center, scale, k=3.0, epsilon=EPS):
    return float(min(abs(float(value)-float(center))/(k*float(scale)+epsilon),1.0))

def phi_s(distances, weights=None):
    d=np.asarray(distances,dtype=float)
    if weights is None:
        w=np.ones_like(d)/len(d)
    else:
        w=np.asarray(weights,dtype=float); w=w/w.sum()
    return float(np.clip(1.0-np.sum(w*d),0.0,1.0))
