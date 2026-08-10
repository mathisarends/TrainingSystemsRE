from dataclasses import dataclass
from uuid import UUID

CAPPED_AT_9_CATEGORIES = frozenset({"Squat", "Bench", "Deadlift"})


@dataclass(frozen=True, slots=True)
class EntryEdit:
    """Desired state for one entry position within a day-edit request.

    `id=None` creates a new entry; an existing id updates it; an id present in
    the day's current entries but absent from the submitted list is deleted.
    """

    category: str
    exercise_name: str
    sets: int
    reps: int
    target_rpe: float
    id: UUID | None = None
    weight: float | None = None
    actual_rpe: float | None = None
    est_max: float | None = None
    notes: str | None = None


def rpe_cap_for(category: str) -> float:
    return 9.0 if category in CAPPED_AT_9_CATEGORIES else 10.0


def deload_target_rpe_for(category: str) -> float:
    return 6.0 if category in CAPPED_AT_9_CATEGORIES else 7.0
