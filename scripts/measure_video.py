import argparse, subprocess, tempfile, json, hashlib, sys
from pathlib import Path
import numpy as np
import soundfile as sf
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from mihm.instruments.audio import extract_features

ap=argparse.ArgumentParser(); ap.add_argument('--object',required=True); ap.add_argument('--video',required=True); ap.add_argument('--reference-audio'); ap.add_argument('--out',default='outputs/video_identity.json'); a=ap.parse_args()
video=Path(a.video)
with tempfile.TemporaryDirectory() as td:
    wav=Path(td)/'embedded.wav'
    subprocess.run(['ffmpeg','-y','-i',str(video),'-vn','-ac','1','-ar','22050',str(wav)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    y,sr=sf.read(wav)
    result={"object":a.object,"video_sha256":hashlib.sha256(video.read_bytes()).hexdigest(),"embedded_audio_features":extract_features(y,sr),"reference_status":"MISSING_NOT_OBSERVED" if not a.reference_audio else "OBSERVED"}
    if a.reference_audio:
        ref,_=sf.read(a.reference_audio)
        n=min(len(y),len(ref))
        if n>0:
            yy=y[:n].astype(float); rr=ref[:n].astype(float)
            result['waveform_corr_zero_offset']=float(np.corrcoef(yy,rr)[0,1]) if np.std(yy)>0 and np.std(rr)>0 else None
    Path(a.out).parent.mkdir(parents=True,exist_ok=True); Path(a.out).write_text(json.dumps(result,indent=2),encoding='utf-8'); print(json.dumps(result,indent=2))
