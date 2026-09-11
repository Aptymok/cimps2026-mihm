import argparse, hashlib, urllib.request
from pathlib import Path
URLS={"Fluo-N2DL-HeLa":"https://data.celltrackingchallenge.net/training-datasets/Fluo-N2DL-HeLa.zip"}
ap=argparse.ArgumentParser(); ap.add_argument('--dataset',required=True,choices=URLS); ap.add_argument('--out',required=True); a=ap.parse_args()
out=Path(a.out); out.mkdir(parents=True,exist_ok=True); dst=out/f"{a.dataset}.zip"
print(f"Downloading official CTC source: {URLS[a.dataset]}")
urllib.request.urlretrieve(URLS[a.dataset],dst)
h=hashlib.sha256(dst.read_bytes()).hexdigest(); print(dst, h)
