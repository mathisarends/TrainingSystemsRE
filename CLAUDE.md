# Conventions

## Domain objects

Entities and other domain/business objects use plain classes with an explicit
`__init__`, not `@dataclass`. This applies to mutable entities as well as
immutable value objects living under `domain/`.

## Router mapping functions

Small response/request mapping functions (`to_response`, `to_list_response`,
etc.) used by only one router live directly in that router module as private
(`_`-prefixed) functions, not in a separate `mapper.py`. Only extract a
shared module when the mapping is reused across multiple routers (e.g.
`users/presentation/mapper.py`, used by both the users and authentication
routers).

Within a router file, keep the route handlers (the public API) at the top,
in route-declaration order, and place each private helper directly below the
route handler that uses it first.

## Router operation IDs

Don't set `operation_id=` manually on `@router.*` decorators. The FastAPI
app is configured with `generate_unique_id_function` (see `main.py`) to
derive it from the route handler's function name automatically.

## `@asynccontextmanager` return type

Annotate `@asynccontextmanager`-decorated functions as returning
`AsyncGenerator[T]` (from `collections.abc`), not `AsyncIterator[T]` —
the latter is deprecated for this use.

```python
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    yield
    await app.state.dishka_container.close()
```

This doesn't apply to dishka's `@provide`-decorated generator methods
(e.g. in `infrastructure/*/provider.py`), which keep `AsyncIterator[T]`.
