from __future__ import annotations
import json, math, hashlib, platform, sys
from pathlib import Path
import numpy as np
import pandas as pd
import librosa, scipy, sklearn
from scipy.signal import find_peaks
from scipy.stats import spearmanr, wilcoxon
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score

SEED=724450
WINDOW_S=4.0
TARGET_SR=22050
EPS=1e-12
FEATURES=['Fs','Di','Cs','Dcog','Er','Vi']
ROOT=Path('/mnt/data/cimps_r1_work')
OUT=ROOT/'r1_extended_results'; OUT.mkdir(parents=True,exist_ok=True)
INPUTS={
 'REM618': ('primary', Path('/mnt/data/cimps_r1_inputs/rem618_master_final_exact.wav')),
 'easter_egg': ('primary', Path('/mnt/data/cimps_r1_inputs/easter_egg_exact.mpeg')),
 'AELUDE': ('secondary', Path('/mnt/data/cimps_r1_inputs/secondary/aelude.wav')),
 'BLVCK': ('secondary', Path('/mnt/data/cimps_r1_inputs/secondary/blvck.wav')),
 'ED': ('secondary', Path('/mnt/data/cimps_r1_inputs/secondary/ed.wav')),
 'YNLPC': ('secondary', Path('/mnt/data/cimps_r1_inputs/secondary/ynlpc.wav')),
 'ODIO_DECIRTELO': ('secondary', Path('/mnt/data/cimps_r1_inputs/secondary/odio_decirtelo.wav')),
}

def sha256(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
 return h.hexdigest()

def frames(y, n_fft=1024, hop=512):
 if len(y)<n_fft: y=np.pad(y,(0,n_fft-len(y)))
 n=1+(len(y)-n_fft)//hop
 shape=(n,n_fft); strides=(y.strides[0]*hop,y.strides[0])
 x=np.lib.stride_tricks.as_strided(y,shape=shape,strides=strides).copy()
 x*=np.hanning(n_fft)
 return x

def extract_features(y:np.ndarray,sr:int)->dict:
 x=frames(y)
 spec=np.abs(np.fft.rfft(x,axis=1))+EPS
 power=spec**2
 q=spec/(spec.sum(axis=1,keepdims=True)+EPS)
 dif=np.diff(q,axis=0)
 flux=np.linalg.norm(dif,axis=1)/math.sqrt(2)
 Fs=float(np.clip(np.mean(flux) if flux.size else 0,0,1))
 gm=np.exp(np.mean(np.log(spec),axis=1)); am=np.mean(spec,axis=1)+EPS
 Di=float(np.mean(np.clip(gm/am,0,1)))
 p=power/(power.sum(axis=1,keepdims=True)+EPS)
 ent=-np.sum(p*np.log(p+EPS),axis=1)/math.log(p.shape[1])
 Cs=float(np.clip(1-np.mean(ent),0,1))
 onset=np.r_[0,np.maximum(0,np.sum(np.maximum(0,np.diff(spec,axis=0)),axis=1))]
 if onset.max()>0: onset=onset/(onset.max()+EPS)
 height=float(np.median(onset)+0.5*np.std(onset))
 peaks,_=find_peaks(onset,height=height,distance=max(1,int(0.08*sr/512)))
 if len(peaks)>=3:
  intervals=np.diff(peaks)*512/sr
  cv=float(np.std(intervals)/(np.mean(intervals)+EPS))
  Dcog=float(np.clip(cv/(1+cv),0,1))
 else: Dcog=0.0
 rms=np.sqrt(np.mean(x*x,axis=1)+EPS)
 p10=float(np.percentile(rms,10)); p90=float(np.percentile(rms,90))
 Er=float(np.clip(p10/(p90+EPS),0,1))
 cv_r=float(np.std(rms)/(np.mean(rms)+EPS)); Vi=float(np.clip(cv_r/(1+cv_r),0,1))
 return dict(Fs=Fs,Di=Di,Cs=Cs,Dcog=Dcog,Er=Er,Vi=Vi)

def perturb(y, family, level, seed):
 y=y.copy(); r=np.random.default_rng(seed)
 if family=='clean': return y
 if family=='noise':
  snr={1:30,2:20,3:10}[level]
  ps=np.mean(y*y)+EPS; pn=ps/(10**(snr/10))
  return np.clip(y+r.normal(0,math.sqrt(pn),len(y)),-1,1)
 if family=='clipping':
  ratio={1:0.90,2:0.60,3:0.30}[level]; peak=np.max(np.abs(y))+EPS; t=ratio*peak
  return np.clip(y,-t,t)
 if family=='dropout':
  frac={1:0.01,2:0.05,3:0.10}[level]; total=max(1,int(frac*len(y))); blocks=5; remain=total; z=y.copy()
  for b in range(blocks):
   n=remain//(blocks-b); start=int(r.integers(0,max(1,len(y)-n))); z[start:start+n]=0; remain-=n
  return z
 raise ValueError(family)

def robust_baseline(df):
 centers={}; scales={}
 for f in FEATURES:
  arr=df[f].to_numpy(float); med=float(np.median(arr)); mad=float(np.median(np.abs(arr-med)))*1.4826
  if mad<0.01:
   q75,q25=np.percentile(arr,[75,25]); mad=max(mad,float((q75-q25)/1.349),0.01)
  centers[f]=med; scales[f]=mad
 return centers,scales

def phi_from_values(values, center, scale, weights, k=3.0):
 c=np.array([center[f] for f in FEATURES]); s=np.array([scale[f] for f in FEATURES])
 d=np.minimum(np.abs(values-c)/(k*s+EPS),1.0)
 return np.clip(1.0-d@weights,0,1)

def holm(pvals):
 m=len(pvals); order=np.argsort(pvals); out=np.empty(m); running=0.0
 for rank,idx in enumerate(order):
  adj=(m-rank)*pvals[idx]; running=max(running,adj); out[idx]=min(1.0,running)
 return out

all_rows=[]; baseline_rows=[]; manifests=[]
for si,(sname,(cohort,path)) in enumerate(INPUTS.items()):
 y,sr=librosa.load(path,sr=TARGET_SR,mono=True); dur=len(y)/sr; nwin=int(dur//WINDOW_S)
 split=nwin//2
 for i in range(nwin):
  seg=y[int(i*WINDOW_S*sr):int((i+1)*WINDOW_S*sr)]
  if i<split:
   baseline_rows.append(dict(signal=sname,cohort=cohort,window=i,start_s=i*WINDOW_S,**extract_features(seg,sr)))
  else:
   variants=[('clean',0)]+[(fam,lvl) for fam in ['noise','clipping','dropout'] for lvl in [1,2,3]]
   for fam,lvl in variants:
    seed=SEED+si*100000+i*101+lvl*7+{'clean':0,'noise':1000,'clipping':2000,'dropout':3000}[fam]
    all_rows.append(dict(signal=sname,cohort=cohort,window=i,start_s=i*WINDOW_S,family=fam,severity=lvl,seed=seed,label=int(fam!='clean'),**extract_features(perturb(seg,fam,lvl,seed),sr)))
 manifests.append(dict(signal=sname,cohort=cohort,path=str(path),sha256=sha256(path),duration_s=dur,sr_loaded=sr,total_windows=nwin,baseline_windows=split,evaluation_windows=nwin-split))

base=pd.DataFrame(baseline_rows); obs=pd.DataFrame(all_rows)
centers_scales={}; obs['Phi_S']=np.nan
w0=np.ones(len(FEATURES))/len(FEATURES)
for sname in INPUTS:
 center,scale=robust_baseline(base[base.signal==sname]); centers_scales[sname]={'center':center,'scale':scale,'k':3.0}
 idx=obs.signal==sname; vals=obs.loc[idx,FEATURES].to_numpy(float)
 obs.loc[idx,'Phi_S']=phi_from_values(vals,center,scale,w0,3.0)
obs['mihm_anomaly']=1-obs.Phi_S
obs['iforest_anomaly']=np.nan; obs['ocsvm_anomaly']=np.nan
for sname in INPUTS:
 Xtr=base[base.signal==sname][FEATURES].to_numpy(float); mask=obs.signal==sname; Xte=obs.loc[mask,FEATURES].to_numpy(float)
 iso=IsolationForest(n_estimators=300,random_state=SEED,contamination='auto').fit(Xtr)
 obs.loc[mask,'iforest_anomaly']=-iso.decision_function(Xte)
 sc=StandardScaler().fit(Xtr); svm=OneClassSVM(kernel='rbf',gamma='scale',nu=0.05).fit(sc.transform(Xtr))
 obs.loc[mask,'ocsvm_anomaly']=-svm.decision_function(sc.transform(Xte))

scopes=[('ALL',obs),('PRIMARY',obs[obs.cohort=='primary']),('SECONDARY',obs[obs.cohort=='secondary'])]+[(s,obs[obs.signal==s]) for s in INPUTS]
metrics=[]
for scope,sub in scopes:
 for method,col in [('MIHM_R1','mihm_anomaly'),('IsolationForest','iforest_anomaly'),('OneClassSVM','ocsvm_anomaly')]:
  metrics.append(dict(scope=scope,method=method,metric='roc_auc',value=float(roc_auc_score(sub.label,sub[col])),n=len(sub)))
 for fam in ['noise','clipping','dropout']:
  sf=sub[(sub.family=='clean')|(sub.family==fam)]
  for method,col in [('MIHM_R1','mihm_anomaly'),('IsolationForest','iforest_anomaly'),('OneClassSVM','ocsvm_anomaly')]:
   rho,p=spearmanr(sf.severity,sf[col]); metrics.append(dict(scope=scope,method=method,metric=f'spearman_{fam}',value=float(rho),p=float(p),n=len(sf)))

stats=[]; pvals=[]
clean=obs[obs.family=='clean'][['signal','window','mihm_anomaly','Phi_S']].rename(columns={'mihm_anomaly':'clean_anom','Phi_S':'clean_phi'})
for fam in ['noise','clipping','dropout']:
 for lvl in [1,2,3]:
  sub=obs[(obs.family==fam)&(obs.severity==lvl)][['signal','window','mihm_anomaly','Phi_S']]; m=sub.merge(clean,on=['signal','window']); diff=m.mihm_anomaly-m.clean_anom
  stat,p=wilcoxon(diff,alternative='greater',zero_method='wilcox')
  stats.append(dict(family=fam,severity=lvl,n=len(m),median_phi=float(np.median(m.Phi_S)),median_clean_phi=float(np.median(m.clean_phi)),median_anomaly_delta=float(np.median(diff)),wilcoxon_W=float(stat),p=float(p))); pvals.append(p)
for r,a in zip(stats,holm(np.array(pvals,float))): r['p_holm']=float(a)

# vectorized sensitivity - perturb equal weights by +/-20%, k in 2.5/3.0/3.5
sens=[]; rr=np.random.default_rng(SEED+999)
pre={}
for sname in INPUTS:
 mask=(obs.signal==sname).to_numpy(); vals=obs.loc[mask,FEATURES].to_numpy(float); cs=centers_scales[sname]; c=np.array([cs['center'][f] for f in FEATURES]); s=np.array([cs['scale'][f] for f in FEATURES]); pre[sname]=(mask,vals,c,s)
for k in [2.5,3.0,3.5]:
 for rep in range(300):
  mult=rr.uniform(.8,1.2,len(FEATURES)); w=mult/mult.sum(); score=np.empty(len(obs),float)
  for sname,(mask,vals,c,s) in pre.items():
   d=np.minimum(np.abs(vals-c)/(k*s+EPS),1.0); score[mask]=d@w
  sens.append(dict(k=k,rep=rep,roc_auc=float(roc_auc_score(obs.label,score)),**{f'w_{FEATURES[i]}':float(w[i]) for i in range(len(FEATURES))}))
sdf=pd.DataFrame(sens)
summary=obs.groupby(['family','severity']).agg(n=('Phi_S','size'),phi_median=('Phi_S','median'),phi_mean=('Phi_S','mean'),phi_sd=('Phi_S','std'),anomaly_median=('mihm_anomaly','median')).reset_index()
summary_signal=obs.groupby(['signal','cohort','family','severity']).agg(n=('Phi_S','size'),phi_median=('Phi_S','median'),phi_mean=('Phi_S','mean'),phi_sd=('Phi_S','std')).reset_index()

base.to_csv(OUT/'baseline_clean_features.csv',index=False); obs.to_csv(OUT/'observations.csv',index=False); pd.DataFrame(metrics).to_csv(OUT/'metrics.csv',index=False); pd.DataFrame(stats).to_csv(OUT/'paired_stats.csv',index=False); summary.to_csv(OUT/'condition_summary.csv',index=False); summary_signal.to_csv(OUT/'condition_summary_by_signal.csv',index=False); sdf.to_csv(OUT/'sensitivity.csv',index=False)
with open(OUT/'baseline_contract.json','w') as f: json.dump(centers_scales,f,indent=2)
manifest={
 'study_id':'CIMPS2026-724450-R1-EXTENDED','seed':SEED,'window_s':WINDOW_S,'target_sr':TARGET_SR,
 'primary_confirmatory_signals':['REM618','easter_egg'],'secondary_within_corpus_signals':['AELUDE','BLVCK','ED','YNLPC','ODIO_DECIRTELO'],
 'features':{
  'Fs':'mean bounded spectral flux between adjacent L1-normalized magnitude spectra',
  'Di':'mean spectral flatness (geometric/arithmetic magnitude ratio); operational interference/noise-density proxy',
  'Cs':'1 - mean normalized spectral entropy; spectral concentration/coherence proxy',
  'Dcog':'legacy symbol retained for traceability; onset-interval dispersion proxy CV/(1+CV), not a direct measurement of human cognition',
  'Er':'RMS energy-floor retention p10/p90',
  'Vi':'RMS-envelope coefficient of variation CV/(1+CV)'
 },
 'phi':'Phi_S = 1 - weighted mean_j min(|x_j - median_baseline_j|/(k*robust_scale_j),1), equal weights, k=3; robust_scale=max(1.4826*MAD,IQR/1.349,0.01)',
 'train_test':'first half of non-overlapping 4-s windows per source defines source-specific clean baseline; second half is held out and reused only to generate paired controlled perturbations',
 'perturbations':{'noise_snr_db':[30,20,10],'clipping_peak_ratio':[0.9,0.6,0.3],'dropout_fraction':[0.01,0.05,0.10]},
 'baselines':{'IsolationForest':{'n_estimators':300,'random_state':SEED,'contamination':'auto'},'OneClassSVM':{'kernel':'rbf','gamma':'scale','nu':0.05,'preprocess':'StandardScaler fit only on clean baseline windows'}},
 'inputs':manifests,
 'software':{'python':sys.version.split()[0],'platform':platform.platform(),'numpy':np.__version__,'pandas':pd.__version__,'librosa':librosa.__version__,'scipy':scipy.__version__,'scikit_learn':sklearn.__version__},
 'validity_boundary':'This experiment evaluates a bounded acoustic operationalization and controlled perturbation sensitivity. The primary analysis preserves the two signals reported in the submitted manuscript; five additional KXTXR audio objects are a secondary within-corpus robustness check. It does not establish universal MIHM validity, human cognitive measurement, multimodal validity, or general sociotechnical performance.'
}
with open(OUT/'RUN_MANIFEST.json','w') as f: json.dump(manifest,f,indent=2)
with open(OUT/'sensitivity_summary.json','w') as f: json.dump({'auc_median':float(sdf.roc_auc.median()),'auc_min':float(sdf.roc_auc.min()),'auc_max':float(sdf.roc_auc.max()),'by_k':sdf.groupby('k').roc_auc.agg(['median','min','max']).reset_index().to_dict('records')},f,indent=2)
print(pd.DataFrame(metrics).query("metric=='roc_auc'")[['scope','method','value','n']].to_string(index=False)); print('\nSUMMARY\n',summary.to_string(index=False)); print('\nPAIRED\n',pd.DataFrame(stats).to_string(index=False)); print('\nSENS',sdf.roc_auc.min(),sdf.roc_auc.median(),sdf.roc_auc.max()); print('\nN',len(obs),'eval windows',obs[['signal','window']].drop_duplicates().shape[0])
