import argparse, json, subprocess, hashlib, datetime
from pathlib import Path
ap=argparse.ArgumentParser(); ap.add_argument('--object',required=True); ap.add_argument('--url',required=True); ap.add_argument('--out',required=True); a=ap.parse_args()
out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
meta=json.loads(subprocess.check_output(['yt-dlp','--dump-single-json','--no-playlist',a.url],text=True))
path_tmpl=str(out/f"{a.object}.%(ext)s")
subprocess.run(['yt-dlp','--no-playlist','-f','bv*+ba/b','--merge-output-format','mp4','-o',path_tmpl,a.url],check=True)
files=sorted(out.glob(f"{a.object}.*")); media=next(p for p in files if p.suffix.lower() in {'.mp4','.mkv','.webm','.mov'})
h=hashlib.sha256(media.read_bytes()).hexdigest()
record={"object":a.object,"requested_url":a.url,"resolved_id":meta.get('id'),"title":meta.get('title'),"uploader":meta.get('uploader'),"duration":meta.get('duration'),"file":str(media),"sha256":h,"timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat()}
(out/f"{a.object}_source.json").write_text(json.dumps(record,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(record,indent=2,ensure_ascii=False))
