from uuid import UUID

from sqlalchemy import delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from training_system.features.plans.domain.entities import Day, Entry, Plan, Week
from training_system.features.plans.domain.repository import PlanRepository
from training_system.infrastructure.database.orm import (
    PlanDayModel,
    PlanEntryModel,
    PlanModel,
    PlanWeekModel,
)


class SqlPlanRepository(PlanRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, *, plan_id: UUID, user_id: UUID) -> Plan | None:
        statement = select(PlanModel).where(
            PlanModel.id == plan_id, PlanModel.user_id == user_id
        )
        model = await self._session.scalar(statement)
        return await self._load_full(model) if model is not None else None

    async def list_for_user(self, *, user_id: UUID) -> list[Plan]:
        statement = (
            select(PlanModel)
            .where(PlanModel.user_id == user_id)
            .order_by(col(PlanModel.updated_at).desc())
        )
        models = (await self._session.scalars(statement)).all()
        return [await self._load_full(model) for model in models]

    async def find_most_recently_updated(self, *, user_id: UUID) -> Plan | None:
        statement = (
            select(PlanModel)
            .where(PlanModel.user_id == user_id)
            .order_by(col(PlanModel.updated_at).desc())
            .limit(1)
        )
        model = await self._session.scalar(statement)
        return await self._load_full(model) if model is not None else None

    async def _load_full(self, model: PlanModel) -> Plan:
        weeks_statement = (
            select(PlanWeekModel)
            .where(PlanWeekModel.plan_id == model.id)
            .order_by(col(PlanWeekModel.week_index))
        )
        week_models = (await self._session.scalars(weeks_statement)).all()

        weeks: list[Week] = []
        for week_model in week_models:
            days_statement = (
                select(PlanDayModel)
                .where(PlanDayModel.week_id == week_model.id)
                .order_by(col(PlanDayModel.day_index))
            )
            day_models = (await self._session.scalars(days_statement)).all()

            days: list[Day] = []
            for day_model in day_models:
                entries_statement = (
                    select(PlanEntryModel)
                    .where(PlanEntryModel.day_id == day_model.id)
                    .order_by(col(PlanEntryModel.position))
                )
                entry_models = (await self._session.scalars(entries_statement)).all()
                entries = [
                    Entry(
                        id=entry_model.id,
                        category=entry_model.category,
                        exercise_name=entry_model.exercise_name,
                        sets=entry_model.sets,
                        reps=entry_model.reps,
                        target_rpe=entry_model.target_rpe,
                        weight=entry_model.weight,
                        actual_rpe=entry_model.actual_rpe,
                        est_max=entry_model.est_max,
                        notes=entry_model.notes,
                    )
                    for entry_model in entry_models
                ]
                days.append(
                    Day(
                        id=day_model.id,
                        day_index=day_model.day_index,
                        entries=entries,
                        start_time=day_model.start_time,
                        end_time=day_model.end_time,
                        duration_minutes=day_model.duration_minutes,
                        is_recording=day_model.is_recording,
                    )
                )
            weeks.append(
                Week(id=week_model.id, week_index=week_model.week_index, days=days)
            )

        return Plan(
            id=model.id,
            created_time=model.created_at,
            user_id=model.user_id,
            title=model.title,
            weekdays=list(model.weekdays),
            block_length=model.block_length,
            start_date=model.start_date,
            cover_image=model.cover_image,
            weeks=weeks,
            last_used_week_index=model.last_used_week_index,
            last_used_day_index=model.last_used_day_index,
            updated_time=model.updated_at,
        )

    async def save(self, *, plan: Plan) -> Plan:
        existing = await self._session.get(PlanModel, plan.id)
        if existing is None:
            existing = PlanModel(
                id=plan.id, created_at=plan.created_at, user_id=plan.user_id
            )
            self._session.add(existing)
        existing.title = plan.title
        existing.weekdays = list(plan.weekdays)
        existing.block_length = plan.block_length
        existing.start_date = plan.start_date
        existing.cover_image = plan.cover_image
        existing.last_used_week_index = plan.last_used_week_index
        existing.last_used_day_index = plan.last_used_day_index
        existing.updated_at = plan.updated_at
        await self._session.flush()

        await self._replace_structure(plan)
        return plan

    async def _replace_structure(self, plan: Plan) -> None:
        await self._delete_structure(plan_id=plan.id)

        for week in plan.weeks:
            self._session.add(
                PlanWeekModel(id=week.id, plan_id=plan.id, week_index=week.week_index)
            )
        await self._session.flush()

        for week in plan.weeks:
            for day in week.days:
                self._session.add(
                    PlanDayModel(
                        id=day.id,
                        week_id=week.id,
                        day_index=day.day_index,
                        start_time=day.start_time,
                        end_time=day.end_time,
                        duration_minutes=day.duration_minutes,
                        is_recording=day.is_recording,
                    )
                )
        await self._session.flush()

        for week in plan.weeks:
            for day in week.days:
                for position, entry in enumerate(day.entries):
                    self._session.add(
                        PlanEntryModel(
                            id=entry.id,
                            day_id=day.id,
                            position=position,
                            category=entry.category,
                            exercise_name=entry.exercise_name,
                            sets=entry.sets,
                            reps=entry.reps,
                            weight=entry.weight,
                            target_rpe=entry.target_rpe,
                            actual_rpe=entry.actual_rpe,
                            est_max=entry.est_max,
                            notes=entry.notes,
                        )
                    )
        await self._session.flush()

    async def _delete_structure(self, *, plan_id: UUID) -> None:
        week_ids = (
            await self._session.scalars(
                select(PlanWeekModel.id).where(PlanWeekModel.plan_id == plan_id)
            )
        ).all()
        if not week_ids:
            return
        day_ids = (
            await self._session.scalars(
                select(PlanDayModel.id).where(col(PlanDayModel.week_id).in_(week_ids))
            )
        ).all()
        if day_ids:
            await self._session.execute(
                delete(PlanEntryModel).where(col(PlanEntryModel.day_id).in_(day_ids))
            )
        await self._session.execute(
            delete(PlanDayModel).where(col(PlanDayModel.week_id).in_(week_ids))
        )
        await self._session.execute(
            delete(PlanWeekModel).where(col(PlanWeekModel.plan_id) == plan_id)
        )

    async def delete(self, *, plan_id: UUID, user_id: UUID) -> bool:
        model = await self._session.scalar(
            select(PlanModel).where(
                PlanModel.id == plan_id, PlanModel.user_id == user_id
            )
        )
        if model is None:
            return False
        await self._delete_structure(plan_id=plan_id)
        await self._session.delete(model)
        await self._session.flush()
        return True

    async def average_recorded_duration_minutes(
        self, *, plan_id: UUID
    ) -> float | None:
        statement = (
            select(func.avg(PlanDayModel.duration_minutes))
            .select_from(PlanDayModel)
            .join(PlanWeekModel, col(PlanWeekModel.id) == PlanDayModel.week_id)
            .where(
                col(PlanWeekModel.plan_id) == plan_id,
                col(PlanDayModel.duration_minutes).is_not(None),
                col(PlanDayModel.duration_minutes) != 0,
            )
        )
        result = await self._session.scalar(statement)
        return float(result) if result is not None else None
