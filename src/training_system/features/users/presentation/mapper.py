from training_system.features.users.domain import User
from training_system.features.users.presentation.schemas import UserResponse


def to_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        picture_url=user.picture_url,
        created_at=user.created_at,
    )
