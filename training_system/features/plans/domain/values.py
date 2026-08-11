from uuid import UUID

CAPPED_AT_9_CATEGORIES = frozenset({"Squat", "Bench", "Deadlift"})


class EntryEdit:
    """Desired state for one entry position within a day-edit request.

    `id=None` creates a new entry; an existing id updates it; an id present in
    the day's current entries but absent from the submitted list is deleted.
    """

    def __init__(
        self,
        *,
        category: str,
        exercise_name: str,
        sets: int,
        reps: int,
        target_rpe: float,
        id: UUID | None = None,
        weight: float | None = None,
        actual_rpe: float | None = None,
        est_max: float | None = None,
        notes: str | None = None,
    ) -> None:
        self.category = category
        self.exercise_name = exercise_name
        self.sets = sets
        self.reps = reps
        self.target_rpe = target_rpe
        self.id = id
        self.weight = weight
        self.actual_rpe = actual_rpe
        self.est_max = est_max
        self.notes = notes


def rpe_cap_for(category: str) -> float:
    return 9.0 if category in CAPPED_AT_9_CATEGORIES else 10.0


def deload_target_rpe_for(category: str) -> float:
    return 6.0 if category in CAPPED_AT_9_CATEGORIES else 7.0
