from datetime import UTC, date, datetime
from uuid import UUID, uuid4

from training_systems.domain import Aggregate
from training_systems.features.plans.domain.values import (
    EntryEdit,
    deload_target_rpe_for,
    rpe_cap_for,
)

DEFAULT_INACTIVITY_MINUTES = 35
MINIMUM_RECORDED_MINUTES = 30
DURATION_ROUNDING_MINUTES = 5


class Entry:
    def __init__(
        self,
        *,
        id: UUID,
        category: str,
        exercise_name: str,
        sets: int,
        reps: int,
        target_rpe: float,
        weight: float | None = None,
        actual_rpe: float | None = None,
        est_max: float | None = None,
        notes: str | None = None,
    ) -> None:
        self.id = id
        self.category = category
        self.exercise_name = exercise_name
        self.sets = sets
        self.reps = reps
        self.target_rpe = target_rpe
        self.weight = weight
        self.actual_rpe = actual_rpe
        self.est_max = est_max
        self.notes = notes


class Day:
    def __init__(
        self,
        *,
        id: UUID,
        day_index: int,
        entries: list[Entry] | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        duration_minutes: int | None = None,
        is_recording: bool = False,
    ) -> None:
        self.id = id
        self.day_index = day_index
        self.entries = entries if entries is not None else []
        self.start_time = start_time
        self.end_time = end_time
        self.duration_minutes = duration_minutes
        self.is_recording = is_recording


class Week:
    def __init__(
        self,
        *,
        id: UUID,
        week_index: int,
        days: list[Day] | None = None,
    ) -> None:
        self.id = id
        self.week_index = week_index
        self.days = days if days is not None else []


def _new_day(day_index: int) -> Day:
    return Day(id=uuid4(), day_index=day_index)


def _new_week(week_index: int, day_count: int) -> Week:
    return Week(
        id=uuid4(),
        week_index=week_index,
        days=[_new_day(index) for index in range(day_count)],
    )


class Plan(Aggregate):
    def __init__(
        self,
        user_id: UUID,
        title: str,
        weekdays: list[str],
        block_length: int,
        start_date: date,
        cover_image: str | None = None,
        weeks: list[Week] | None = None,
        last_used_week_index: int = 0,
        last_used_day_index: int = 0,
        updated_time: datetime | None = None,
        id: UUID | None = None,
        created_time: datetime | None = None,
    ) -> None:
        super().__init__(id=id, created_time=created_time)
        self._user_id = user_id
        self._title = title
        self._weekdays = weekdays
        self._block_length = block_length
        self._start_date = start_date
        self._cover_image = cover_image
        self._weeks = weeks if weeks is not None else []
        self._last_used_week_index = last_used_week_index
        self._last_used_day_index = last_used_day_index
        self._updated_at = updated_time or self.created_at

    @property
    def user_id(self) -> UUID:
        return self._user_id

    @property
    def title(self) -> str:
        return self._title

    @property
    def weekdays(self) -> list[str]:
        return self._weekdays

    @property
    def block_length(self) -> int:
        return self._block_length

    @property
    def start_date(self) -> date:
        return self._start_date

    @property
    def cover_image(self) -> str | None:
        return self._cover_image

    @property
    def weeks(self) -> list[Week]:
        return self._weeks

    @property
    def last_used_week_index(self) -> int:
        return self._last_used_week_index

    @property
    def last_used_day_index(self) -> int:
        return self._last_used_day_index

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def _touch(self) -> None:
        self._updated_at = datetime.now(UTC)

    @classmethod
    def create(
        cls,
        *,
        user_id: UUID,
        title: str,
        weekdays: list[str],
        block_length: int,
        start_date: date,
        cover_image: str | None = None,
    ) -> "Plan":
        weeks = [
            _new_week(index, len(weekdays)) for index in range(block_length)
        ]
        return cls(
            user_id=user_id,
            title=title,
            weekdays=weekdays,
            block_length=block_length,
            start_date=start_date,
            cover_image=cover_image,
            weeks=weeks,
        )

    def update_basics(
        self,
        *,
        title: str | None = None,
        weekdays: list[str] | None = None,
        block_length: int | None = None,
        start_date: date | None = None,
        cover_image: str | None = None,
    ) -> None:
        if title is not None:
            self._title = title
        if start_date is not None:
            self._start_date = start_date
        if cover_image is not None:
            self._cover_image = cover_image

        new_weekdays = weekdays if weekdays is not None else self._weekdays
        new_block_length = (
            block_length if block_length is not None else self._block_length
        )
        if new_weekdays != self._weekdays or new_block_length != self._block_length:
            self._weekdays = new_weekdays
            self._resize(block_length=new_block_length, day_count=len(new_weekdays))
        self._touch()

    def _resize(self, *, block_length: int, day_count: int) -> None:
        if len(self._weeks) < block_length:
            self._weeks.extend(
                _new_week(index, day_count)
                for index in range(len(self._weeks), block_length)
            )
        elif len(self._weeks) > block_length:
            self._weeks = self._weeks[:block_length]

        for week in self._weeks:
            if len(week.days) < day_count:
                week.days.extend(
                    _new_day(index) for index in range(len(week.days), day_count)
                )
            elif len(week.days) > day_count:
                week.days = week.days[:day_count]

        self._block_length = block_length

    def day_at(self, *, week_index: int, day_index: int) -> Day:
        if week_index < 0 or week_index >= len(self._weeks):
            raise IndexError(f"week index {week_index} out of range")
        week = self._weeks[week_index]
        if day_index < 0 or day_index >= len(week.days):
            raise IndexError(f"day index {day_index} out of range")
        return week.days[day_index]

    def apply_day_edit(
        self, *, week_index: int, day_index: int, entries: list[EntryEdit]
    ) -> bool:
        """Applies the day's new entry list, propagates structure forward to
        the same weekday in future weeks, and reports whether an activity
        signal (a changed weight/actual_rpe) occurred."""
        day = self.day_at(week_index=week_index, day_index=day_index)
        existing_by_id = {entry.id: entry for entry in day.entries}

        activity = False
        new_entries: list[Entry] = []
        for edit in entries:
            existing = existing_by_id.get(edit.id) if edit.id is not None else None
            if existing is not None:
                if (
                    edit.weight != existing.weight
                    or edit.actual_rpe != existing.actual_rpe
                ):
                    activity = True
            elif edit.weight is not None or edit.actual_rpe is not None:
                activity = True
            new_entries.append(
                Entry(
                    id=existing.id if existing is not None else uuid4(),
                    category=edit.category,
                    exercise_name=edit.exercise_name,
                    sets=edit.sets,
                    reps=edit.reps,
                    target_rpe=edit.target_rpe,
                    weight=edit.weight,
                    actual_rpe=edit.actual_rpe,
                    est_max=edit.est_max,
                    notes=edit.notes,
                )
            )

        day.entries = new_entries
        self._propagate_structure(
            week_index=week_index, day_index=day_index, entries=new_entries
        )
        self._last_used_week_index = week_index
        self._last_used_day_index = day_index
        self._touch()
        return activity

    def _propagate_structure(
        self, *, week_index: int, day_index: int, entries: list[Entry]
    ) -> None:
        for future_week in self._weeks[week_index + 1 :]:
            if day_index >= len(future_week.days):
                continue
            future_day = future_week.days[day_index]
            propagated: list[Entry] = []
            for position, entry in enumerate(entries):
                current = (
                    future_day.entries[position]
                    if position < len(future_day.entries)
                    else None
                )
                propagated.append(
                    Entry(
                        id=current.id if current is not None else uuid4(),
                        category=entry.category,
                        exercise_name=entry.exercise_name,
                        sets=entry.sets,
                        reps=entry.reps,
                        target_rpe=entry.target_rpe,
                        notes=entry.notes,
                        weight=current.weight if current is not None else None,
                        actual_rpe=current.actual_rpe if current is not None else None,
                        est_max=current.est_max if current is not None else None,
                    )
                )
            future_day.entries = propagated

    def apply_progression(
        self, *, rpe_increment: float, deload_last_week: bool
    ) -> None:
        last_week_index = len(self._weeks) - 1
        for week_index in range(1, len(self._weeks)):
            week = self._weeks[week_index]
            previous_week = self._weeks[week_index - 1]
            is_deload = deload_last_week and week_index == last_week_index

            for day_index, day in enumerate(week.days):
                if day_index >= len(previous_week.days):
                    continue
                previous_day = previous_week.days[day_index]

                for position, entry in enumerate(day.entries):
                    if position >= len(previous_day.entries):
                        continue
                    previous_entry = previous_day.entries[position]
                    if previous_entry.exercise_name != entry.exercise_name:
                        continue

                    if is_deload:
                        entry.sets = max(0, previous_entry.sets - 1)
                        entry.target_rpe = deload_target_rpe_for(entry.category)
                    else:
                        cap = rpe_cap_for(entry.category)
                        entry.target_rpe = min(
                            cap, previous_entry.target_rpe + rpe_increment
                        )
        self._touch()

    def start_recording(self, *, week_index: int, day_index: int, at: datetime) -> None:
        day = self.day_at(week_index=week_index, day_index=day_index)
        day.start_time = at
        day.is_recording = True

    def close_recording(self, *, week_index: int, day_index: int, at: datetime) -> int:
        day = self.day_at(week_index=week_index, day_index=day_index)
        day.end_time = at
        elapsed_minutes = (
            (at - day.start_time).total_seconds() / 60 if day.start_time else 0.0
        )
        active_minutes = max(0.0, elapsed_minutes - DEFAULT_INACTIVITY_MINUTES)
        rounded = (
            round(active_minutes / DURATION_ROUNDING_MINUTES)
            * DURATION_ROUNDING_MINUTES
        )
        day.duration_minutes = int(rounded)
        day.is_recording = False
        return day.duration_minutes
