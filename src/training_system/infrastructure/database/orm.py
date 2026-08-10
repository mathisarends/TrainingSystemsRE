"""Central table registration point (see database.md#table-placement-and-registration)."""

from datetime import UTC, date, datetime
from uuid import UUID

from sqlalchemy import JSON, Column, DateTime, UniqueConstraint
from sqlmodel import Field

from training_system.infrastructure.database.models import DatabaseModel


class UserModel(DatabaseModel, table=True):
    __tablename__ = "users"

    name: str = Field(max_length=200)
    email: str = Field(max_length=320, unique=True, index=True)
    picture_url: str | None = None


class AuthIdentityModel(DatabaseModel, table=True):
    __tablename__ = "auth_identities"
    __table_args__ = (UniqueConstraint("provider", "subject"),)

    user_id: UUID = Field(index=True, foreign_key="users.id")
    provider: str = Field(max_length=50)
    subject: str = Field(max_length=255)


class SessionModel(DatabaseModel, table=True):
    __tablename__ = "sessions"

    token: str = Field(max_length=128, unique=True, index=True)
    user_id: UUID = Field(index=True, foreign_key="users.id")
    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))


class ExerciseCategoryModel(DatabaseModel, table=True):
    __tablename__ = "exercise_categories"
    __table_args__ = (UniqueConstraint("user_id", "category"),)

    user_id: UUID = Field(index=True, foreign_key="users.id")
    category: str = Field(max_length=50)
    rest_seconds: int
    default_sets: int
    default_reps: int
    default_target_rpe: float


class CatalogExerciseModel(DatabaseModel, table=True):
    __tablename__ = "catalog_exercises"

    user_id: UUID = Field(index=True, foreign_key="users.id")
    category: str = Field(max_length=50)
    name: str = Field(max_length=200)
    position: int
    max_factor: float | None = None


class PlanModel(DatabaseModel, table=True):
    __tablename__ = "plans"

    user_id: UUID = Field(index=True, foreign_key="users.id")
    title: str = Field(max_length=200)
    weekdays: list[str] = Field(sa_column=Column(JSON, nullable=False))
    block_length: int
    start_date: date
    cover_image: str | None = None
    last_used_week_index: int = 0
    last_used_day_index: int = 0
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class PlanWeekModel(DatabaseModel, table=True):
    __tablename__ = "plan_weeks"
    __table_args__ = (UniqueConstraint("plan_id", "week_index"),)

    plan_id: UUID = Field(index=True, foreign_key="plans.id")
    week_index: int


class PlanDayModel(DatabaseModel, table=True):
    __tablename__ = "plan_days"
    __table_args__ = (UniqueConstraint("week_id", "day_index"),)

    week_id: UUID = Field(index=True, foreign_key="plan_weeks.id")
    day_index: int
    start_time: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    end_time: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    duration_minutes: int | None = None
    is_recording: bool = False


class PlanEntryModel(DatabaseModel, table=True):
    __tablename__ = "plan_entries"

    day_id: UUID = Field(index=True, foreign_key="plan_days.id")
    position: int
    category: str = Field(max_length=50)
    exercise_name: str = Field(max_length=200)
    sets: int
    reps: int
    weight: float | None = None
    target_rpe: float
    actual_rpe: float | None = None
    est_max: float | None = None
    notes: str | None = None


class BodyWeightEntryModel(DatabaseModel, table=True):
    __tablename__ = "body_weight_entries"
    __table_args__ = (UniqueConstraint("user_id", "date"),)

    user_id: UUID = Field(index=True, foreign_key="users.id")
    date: date
    weight: float


class BodyWeightGoalModel(DatabaseModel, table=True):
    __tablename__ = "body_weight_goals"

    user_id: UUID = Field(unique=True, index=True, foreign_key="users.id")
    direction: str = Field(max_length=20)
    rate: float


class PersonalRecordModel(DatabaseModel, table=True):
    __tablename__ = "personal_records"
    __table_args__ = (UniqueConstraint("user_id", "exercise_name"),)

    user_id: UUID = Field(index=True, foreign_key="users.id")
    exercise_name: str = Field(max_length=200)
    category: str = Field(max_length=50)
    sets: int
    reps: int
    weight: float
    actual_rpe: float
    est_max: float
    achieved_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    history: list[dict[str, object]] = Field(
        default_factory=list, sa_column=Column(JSON, nullable=False)
    )


class PushSubscriptionModel(DatabaseModel, table=True):
    __tablename__ = "push_subscriptions"

    user_id: UUID = Field(unique=True, index=True, foreign_key="users.id")
    endpoint: str = Field(max_length=1000)
    p256dh: str = Field(max_length=500)
    auth: str = Field(max_length=500)


class UnseenCompletionModel(DatabaseModel, table=True):
    __tablename__ = "unseen_completions"

    user_id: UUID = Field(index=True, foreign_key="users.id")
    completed_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))


def register_models() -> None:
    """Import side effect: registers every table class on SQLModel.metadata."""
