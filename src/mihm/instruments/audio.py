from __future__ import annotations
import numpy as np
from scipy.signal import find_peaks

EPS=1e-12

def frame_signal(y, frame_length=1024, hop_length=512):
    y=np.asarray(y,dtype=float)
    if len(y)<frame_length:
        y=np.pad(y,(0,frame_length-len(y)))
    starts=range(0, len(y)-frame_length+1, hop_length)
    return np.stack([y[s:s+frame_length] for s in starts])

def extract_features(y, sr=22050, frame_length=1024, hop_length=512):
    frames=frame_signal(y,frame_length,hop_length)
    win=np.hanning(frame_length)
    X=np.abs(np.fft.rfft(frames*win,axis=1)) + EPS
    q=X/X.sum(axis=1,keepdims=True)
    p=(X**2); p=p/p.sum(axis=1,keepdims=True)
    fs=float(np.mean(np.linalg.norm(np.diff(q,axis=0),axis=1)/np.sqrt(2))) if len(q)>1 else 0.0
    di=float(np.mean(np.exp(np.mean(np.log(X),axis=1))/np.mean(X,axis=1)))
    K=X.shape[1]
    ent=-np.sum(p*np.log(p+EPS),axis=1)/np.log(K)
    cs=float(1-np.mean(ent))
    rms=np.sqrt(np.mean(frames**2,axis=1)+EPS)
    er=float(np.percentile(rms,10)/(np.percentile(rms,90)+EPS))
    cv=float(np.std(rms)/(np.mean(rms)+EPS)); vi=float(cv/(1+cv))
    pos=np.maximum(np.diff(X,axis=0),0).sum(axis=1) if len(X)>1 else np.array([0.0])
    thr=float(np.median(pos)+0.5*np.std(pos))
    min_dist=max(1,int(round(0.08*sr/hop_length)))
    peaks,_=find_peaks(pos,height=thr,distance=min_dist)
    if len(peaks)>=3:
        times=(peaks+1)*hop_length/sr
        intervals=np.diff(times)
        cv_o=float(np.std(intervals)/(np.mean(intervals)+EPS)); d_onset=float(cv_o/(1+cv_o))
    else:
        d_onset=0.0
    return {"Fs":np.clip(fs,0,1).item(),"Di":np.clip(di,0,1).item(),"Cs":np.clip(cs,0,1).item(),"D_onset":np.clip(d_onset,0,1).item(),"Er":np.clip(er,0,1).item(),"Vi":np.clip(vi,0,1).item()}
