from pathlib import Path
import hashlib, datetime

def sha256_file(path: str|Path):
    p=Path(path)
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def ledger_record(path, asset_id, role, epistemic_status="OBSERVED", source_uri=None):
    p=Path(path)
    return {
        "asset_id":asset_id,"path":str(p),"bytes":p.stat().st_size,
        "sha256":sha256_file(p),"role":role,"epistemic_status":epistemic_status,
        "source_uri":source_uri,"recorded_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
