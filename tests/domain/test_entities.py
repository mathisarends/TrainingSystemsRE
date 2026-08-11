from datetime import UTC, datetime
from uuid import UUID, uuid4

from training_systems.domain import Entity


def test_entity_generates_id_and_created_at_when_not_given() -> None:
    entity = Entity()

    assert isinstance(entity.id, UUID)
    assert entity.created_at.tzinfo is UTC


def test_entity_keeps_given_id_and_created_at() -> None:
    given_id = uuid4()
    given_created_at = datetime(2026, 1, 1, tzinfo=UTC)

    entity = Entity(id=given_id, created_time=given_created_at)

    assert entity.id == given_id
    assert entity.created_at == given_created_at
