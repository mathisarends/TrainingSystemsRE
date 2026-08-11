from datetime import datetime

MAX_HISTORY = 10


class RecordSnapshot:
    def __init__(
        self,
        *,
        sets: int,
        reps: int,
        weight: float,
        actual_rpe: float,
        est_max: float,
        achieved_at: datetime,
    ) -> None:
        self.sets = sets
        self.reps = reps
        self.weight = weight
        self.actual_rpe = actual_rpe
        self.est_max = est_max
        self.achieved_at = achieved_at


class PersonalRecord:
    def __init__(
        self,
        *,
        exercise_name: str,
        category: str,
        sets: int,
        reps: int,
        weight: float,
        actual_rpe: float,
        est_max: float,
        achieved_at: datetime,
        history: list[RecordSnapshot] | None = None,
    ) -> None:
        self.exercise_name = exercise_name
        self.category = category
        self.sets = sets
        self.reps = reps
        self.weight = weight
        self.actual_rpe = actual_rpe
        self.est_max = est_max
        self.achieved_at = achieved_at
        self.history = history if history is not None else []

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
