from __future__ import annotations
import argparse, json, math, subprocess, tempfile, hashlib
from pathlib import Path
import cv2
import numpy as np
import pandas as pd
import librosa


def entropy_u8(gray: np.ndarray) -> float:
    hist = cv2.calcHist([gray],[0],None,[256],[0,256]).ravel()
    p = hist / max(hist.sum(), 1.0)
    p = p[p>0]
    return float(-(p*np.log2(p)).sum()/8.0)


def best_lag_corr(x, y, sample_hz=2.0, max_lag_s=2.0, n_perm=500, seed=42):
    x=np.asarray(x,float); y=np.asarray(y,float)
    max_lag=int(round(max_lag_s*sample_hz))
    best=None
    for lag in range(-max_lag,max_lag+1):
        if lag<0: a,b=x[-lag:],y[:len(y)+lag]
        elif lag>0: a,b=x[:-lag],y[lag:]
        else: a,b=x,y
        mask=np.isfinite(a)&np.isfinite(b)
        a=a[mask]; b=b[mask]
        if len(a)<8 or np.std(a)==0 or np.std(b)==0: continue
        r=float(np.corrcoef(a,b)[0,1])
        if best is None or abs(r)>abs(best[0]): best=(r,lag/sample_hz,len(a))
    if best is None: return {"r":None,"lag_s":None,"n":0,"p_perm":None}
    r0,lag_s,n=best
    rng=np.random.default_rng(seed)
    null=[]
    for _ in range(n_perm):
        sh=int(rng.integers(1,max(2,len(y)-1)))
        yp=np.roll(y,sh)
        if lag_s<0: a,b=x[int(round(-lag_s*sample_hz)):],yp[:len(yp)-int(round(-lag_s*sample_hz))]
        elif lag_s>0: L=int(round(lag_s*sample_hz)); a,b=x[:-L],yp[L:]
        else: a,b=x,yp
        mask=np.isfinite(a)&np.isfinite(b); a=a[mask]; b=b[mask]
        if len(a)>=8 and np.std(a)>0 and np.std(b)>0: null.append(abs(float(np.corrcoef(a,b)[0,1])))
    p=(1+sum(v>=abs(r0) for v in null))/(1+len(null)) if null else None
    return {"r":r0,"lag_s":lag_s,"n":n,"p_perm":p}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--video',required=True)
    ap.add_argument('--object',required=True)
    ap.add_argument('--outdir',required=True)
    ap.add_argument('--sample-hz',type=float,default=2.0)
    args=ap.parse_args()
    video=Path(args.video); out=Path(args.outdir); out.mkdir(parents=True,exist_ok=True)

    cap=cv2.VideoCapture(str(video))
    fps=float(cap.get(cv2.CAP_PROP_FPS)); nframes=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); duration=nframes/fps if fps>0 else None
    step=max(1,int(round(fps/args.sample_hz)))
    rows=[]; prev_gray=None; prev_flow_gray=None
    idx=0
    while True:
        ok,frame=cap.read()
        if not ok: break
        if idx%step: idx+=1; continue
        t=idx/fps
        small=cv2.resize(frame,(360,int(frame.shape[0]*360/frame.shape[1])),interpolation=cv2.INTER_AREA)
        gray=cv2.cvtColor(small,cv2.COLOR_BGR2GRAY)
        lum=float(gray.mean()/255.0); contrast=float(gray.std()/255.0); ent=entropy_u8(gray)
        edges=cv2.Canny(gray,100,200); edge=float((edges>0).mean())
        if prev_gray is None:
            pix=np.nan; flow=np.nan
        else:
            pix=float(np.mean(np.abs(gray.astype(np.float32)-prev_gray.astype(np.float32)))/255.0)
            fl=cv2.calcOpticalFlowFarneback(prev_flow_gray,gray,None,0.5,3,15,3,5,1.2,0)
            mag=np.sqrt(fl[...,0]**2+fl[...,1]**2)
            flow=float(np.mean(mag)/math.hypot(gray.shape[0],gray.shape[1]))
        rows.append({"t":t,"luminance":lum,"contrast":contrast,"entropy":ent,"edge_density":edge,"pixel_change":pix,"optical_flow":flow})
        prev_gray=gray; prev_flow_gray=gray; idx+=1
    cap.release()
    vdf=pd.DataFrame(rows)

    with tempfile.TemporaryDirectory() as td:
        wav=Path(td)/'embedded.wav'
        subprocess.run(['ffmpeg','-y','-i',str(video),'-vn','-ac','1','-ar','22050',str(wav)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        y,sr=librosa.load(str(wav),sr=22050,mono=True)
    hop=max(1,int(round(sr/args.sample_hz)))
    rms=librosa.feature.rms(y=y,frame_length=2048,hop_length=hop,center=True)[0]
    onset=librosa.onset.onset_strength(y=y,sr=sr,hop_length=hop)
    S=np.abs(librosa.stft(y,n_fft=2048,hop_length=hop,win_length=2048,window='hann'))
    Sn=S/(S.sum(axis=0,keepdims=True)+1e-12)
    flux=np.r_[0.0,np.sqrt(((np.diff(Sn,axis=1))**2).sum(axis=0))]
    at=librosa.frames_to_time(np.arange(len(rms)),sr=sr,hop_length=hop)
    for name,arr in [('audio_rms',rms),('audio_onset',onset),('audio_flux',flux)]:
        vdf[name]=np.interp(vdf.t.to_numpy(),at,arr,left=np.nan,right=np.nan)
    vdf.to_csv(out/f'{args.object}_public_timeseries.csv',index=False)

    relations={}
    for visual in ['pixel_change','optical_flow']:
        for audio in ['audio_rms','audio_onset','audio_flux']:
            relations[f'{visual}__{audio}']=best_lag_corr(vdf[visual].to_numpy(),vdf[audio].to_numpy(),args.sample_hz)
    summary={
      'object':args.object,
      'video_sha256':hashlib.sha256(video.read_bytes()).hexdigest(),
      'fps':fps,'duration_s':duration,'sample_hz':args.sample_hz,'n_samples':int(len(vdf)),
      'visual_summary':{c:{'mean':float(np.nanmean(vdf[c])),'p95':float(np.nanpercentile(vdf[c],95))} for c in ['luminance','contrast','entropy','edge_density','pixel_change','optical_flow']},
      'relations':relations,
      'interpretation_rule':'Associations are temporal covariation only; no causal claim and no cover-video equivalence is inferred.'
    }
    (out/f'{args.object}_public_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
