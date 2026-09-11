from __future__ import annotations
import numpy as np
import cv2
from skimage.color import rgb2lab
from skimage.measure import shannon_entropy

def extract_image_features(rgb):
    rgb=np.asarray(rgb)
    if rgb.dtype!=np.uint8:
        rgb=np.clip(rgb,0,255).astype(np.uint8)
    gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)
    H=float(shannon_entropy(gray)/8.0)
    C=float(np.std(gray)/127.5)
    E=float(np.mean(cv2.Canny(gray,100,200)>0))
    flipped=np.fliplr(gray).astype(float)
    a=gray.astype(float).ravel(); b=flipped.ravel()
    corr=float(np.corrcoef(a,b)[0,1]) if np.std(a)>0 and np.std(b)>0 else 0.0
    S=float((corr+1)/2)
    lab=rgb2lab(rgb/255.0)
    chroma=np.sqrt(lab[:,:,1]**2+lab[:,:,2]**2)
    Ch=float(np.mean(chroma)/181.02)
    return {"H":np.clip(H,0,1).item(),"C":np.clip(C,0,1).item(),"E":np.clip(E,0,1).item(),"S":np.clip(S,0,1).item(),"Ch":np.clip(Ch,0,1).item()}
