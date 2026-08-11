from training_systems.presentation.schema import Schema


class PushKeys(Schema):
    p256dh: str
    auth: str


class RegisterPushSubscriptionRequest(Schema):
    endpoint: str
    keys: PushKeys


class PushSubscriptionResponse(Schema):
    endpoint: str
