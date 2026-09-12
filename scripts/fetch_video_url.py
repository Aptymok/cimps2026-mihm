import argparse, json, subprocess, hashlib, datetime, sys
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument('--object',required=True)
ap.add_argument('--url',required=True)
ap.add_argument('--out',required=True)
a=ap.parse_args()
out=Path(a.out); out.mkdir(parents=True,exist_ok=True)

attempts=[
    ['--js-runtimes','node','--extractor-args','youtube:player_client=web_embedded,default'],
    ['--js-runtimes','node','--extractor-args','youtube:player_client=tv_embedded,web_embedded'],
    ['--js-runtimes','node','--extractor-args','youtube:player_client=android_vr,web_embedded'],
    ['--js-runtimes','node','--extractor-args','youtube:player_client=web_safari,web_embedded'],
]

def run_ytdlp(extra, metadata=False):
    base=['yt-dlp','--no-playlist']+extra
    if metadata:
        base+=['--dump-single-json',a.url]
    else:
        base+=['-f','bv*+ba/b','--merge-output-format','mp4','-o',str(out/f'{a.object}.%(ext)s'),a.url]
    return subprocess.run(base,text=True,capture_output=True)

meta=None; selected=None; errors=[]
for extra in attempts:
    p=run_ytdlp(extra,metadata=True)
    if p.returncode==0:
        try:
            meta=json.loads(p.stdout)
            selected=extra
            break
        except Exception as exc:
            errors.append({'args':extra,'error':f'json:{exc}','stderr':p.stderr[-1200:]})
    else:
        errors.append({'args':extra,'error':'metadata_failed','stderr':p.stderr[-1200:]})

if meta is None:
    (out/f'{a.object}_resolver_failure.json').write_text(json.dumps({
        'object':a.object,'requested_url':a.url,'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status':'UNRESOLVED_EXTERNAL_FETCH','attempts':errors
    },indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(errors,indent=2,ensure_ascii=False),file=sys.stderr)
    raise SystemExit(2)

p=run_ytdlp(selected,metadata=False)
if p.returncode!=0:
    errors.append({'args':selected,'error':'download_failed','stderr':p.stderr[-2000:]})
    (out/f'{a.object}_resolver_failure.json').write_text(json.dumps({
        'object':a.object,'requested_url':a.url,'resolved_id':meta.get('id'),'title':meta.get('title'),
        'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status':'UNRESOLVED_EXTERNAL_FETCH','attempts':errors
    },indent=2,ensure_ascii=False),encoding='utf-8')
    print(p.stderr,file=sys.stderr)
    raise SystemExit(3)

files=sorted(out.glob(f'{a.object}.*'))
media=next((p for p in files if p.suffix.lower() in {'.mp4','.mkv','.webm','.mov'}),None)
if media is None:
    raise SystemExit('No media file resolved')
h=hashlib.sha256(media.read_bytes()).hexdigest()
record={
    'object':a.object,'requested_url':a.url,'resolved_id':meta.get('id'),'title':meta.get('title'),
    'uploader':meta.get('uploader'),'duration':meta.get('duration'),'file':str(media),'sha256':h,
    'resolver_args':selected,'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'status':'OBSERVED_FROM_PUBLIC_URL'
}
(out/f'{a.object}_source.json').write_text(json.dumps(record,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(record,indent=2,ensure_ascii=False))
