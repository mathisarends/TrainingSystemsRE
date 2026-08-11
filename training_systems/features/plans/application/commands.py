from dataclasses import dataclass
from datetime import date

from training_systems.features.plans.domain import EntryEdit


@dataclass(frozen=True, slots=True)
class PlanBasicsUpdate:
    title: str | None = None
    weekdays: list[str] | None = None
    block_length: int | None = None
    start_date: date | None = None
    cover_image: str | None = None


@dataclass(frozen=True, slots=True)
class DayEdit:
    week_index: int
    day_index: int
    entries: list[EntryEdit]


@dataclass(frozen=True, slots=True)
class PlanPatch:
    basics: PlanBasicsUpdate | None = None
    day_edit: DayEdit | None = None
