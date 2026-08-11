from dataclasses import dataclass, field
from datetime import datetime

MAX_HISTORY = 10


@dataclass(frozen=True, slots=True)
class RecordSnapshot:
    sets: int
    reps: int
    weight: float
    actual_rpe: float
    est_max: float
    achieved_at: datetime


@dataclass(slots=True)
class PersonalRecord:
    exercise_name: str
    category: str
    sets: int
    reps: int
    weight: float
    actual_rpe: float
    est_max: float
    achieved_at: datetime
    history: list[RecordSnapshot] = field(default_factory=list)

    def replace_with(self, snapshot: RecordSnapshot, *, category: str) -> None:
        previous = RecordSnapshot(
            sets=self.sets,
            reps=self.reps,
            weight=self.weight,
            actual_rpe=self.actual_rpe,
            est_max=self.est_max,
            achieved_at=self.achieved_at,
        )
        self.history = [previous, *self.history][:MAX_HISTORY]
        self.category = category
        self.sets = snapshot.sets
        self.reps = snapshot.reps
        self.weight = snapshot.weight
        self.actual_rpe = snapshot.actual_rpe
        self.est_max = snapshot.est_max
        self.achieved_at = snapshot.achieved_at

    def revert_to_previous(self) -> bool:
        if not self.history:
            return False
        previous, *rest = self.history
        self.sets = previous.sets
        self.reps = previous.reps
        self.weight = previous.weight
        self.actual_rpe = previous.actual_rpe
        self.est_max = previous.est_max
        self.achieved_at = previous.achieved_at
        self.history = rest
        return True
