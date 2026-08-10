from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class PushMessage:
    title: str
    body: str
    url: str | None = None
    tag: str | None = None
    actions: list[dict[str, str]] = field(default_factory=list)
    vibrate: list[int] = field(default_factory=list)
    silent: bool = False
