from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from mihm.core import phi_s

app = FastAPI(title="MIHM Audit API", version="1.0.0")


class ScoreRequest(BaseModel):
    distances: list[float]
    weights: list[float] | None = None


@app.get('/health')
def health():
    return {"status": "ok"}


@app.post('/mihm/phi-s')
def score(req: ScoreRequest):
    return {
        "phi_s": phi_s(req.distances, req.weights),
        "status": "DERIVED"
    }
