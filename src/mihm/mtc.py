from dataclasses import dataclass, asdict
from typing import Sequence

@dataclass
class MTCRecord:
    object_id: str
    domain_a: str
    domain_b: str
    shared_identity_evidence: Sequence[str]
    declared_invariants: Sequence[str]
    functional_mapping: Sequence[str]
    temporal_alignment: str | None
    information_loss: Sequence[str]
    provenance: Sequence[str]
    status: str

    def to_dict(self):
        return asdict(self)
