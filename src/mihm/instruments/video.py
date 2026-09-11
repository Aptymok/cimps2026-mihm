from __future__ import annotations
from dataclasses import dataclass

@dataclass
class AudioVideoIdentity:
    object_id: str
    resolved_source: str
    alignment_seconds: float|None
    overlap_seconds: float|None
    onset_correlation: float|None
    rms_correlation: float|None
    waveform_correlation: float|None
    status: str

# URL resolution, byte hashing and media decoding occur before scoring in scripts/measure_video.py.
