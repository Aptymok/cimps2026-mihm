from dataclasses import dataclass, field
from typing import Mapping, Sequence, Any

@dataclass(frozen=True)
class InstrumentContract:
    instrument_id: str
    domain: str
    object_definition: str
    question: str
    observables: Sequence[str]
    reference_rule: str
    perturbations: Mapping[str, Any]
    threshold_rule: str | None
    ground_truth_rule: str | None
    missingness_rule: str
    failure_conditions: Sequence[str] = field(default_factory=tuple)

    def validate(self):
        assert self.instrument_id and self.domain and self.observables
        assert self.missingness_rule
        return True
