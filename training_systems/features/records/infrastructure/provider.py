from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from training_systems.features.records.application import PersonalRecordService
from training_systems.features.records.domain import PersonalRecordRepository
from training_systems.features.records.infrastructure.repository import (
    SqlPersonalRecordRepository,
)


class RecordsProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def personal_record_repository(
        self, session: AsyncSession
    ) -> PersonalRecordRepository:
        return SqlPersonalRecordRepository(session)

    @provide(scope=Scope.REQUEST)
    def personal_record_service(
        self, repository: PersonalRecordRepository
    ) -> PersonalRecordService:
        return PersonalRecordService(repository)
