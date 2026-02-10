from __future__ import annotations

from typing import Any, Callable, Iterable
from pydantic import BaseModel, ConfigDict


class Query(BaseModel):
    """Composable predicate wrapper for querying dataset objects.

    Instances are callable and support `&`, `|`, and `~` for composition.
    Built on pydantic v2 so queries can be validated/serialized if needed.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    func: Callable[[Any], bool]

    def __call__(self, obj: Any) -> bool:
        return bool(self.func(obj))

    def matches(self, obj: Any) -> bool:
        return self(obj)

    def __and__(self, other: "Query | Callable[[Any], bool]") -> "Query":
        if isinstance(other, Query):
            return Query(func=lambda o: self(o) and other(o))
        if callable(other):
            return Query(func=lambda o: self(o) and bool(other(o)))
        raise TypeError("Right operand must be Query or callable")

    def __or__(self, other: "Query | Callable[[Any], bool]") -> "Query":
        if isinstance(other, Query):
            return Query(func=lambda o: self(o) or other(o))
        if callable(other):
            return Query(func=lambda o: self(o) or bool(other(o)))
        raise TypeError("Right operand must be Query or callable")

    def __invert__(self) -> "Query":
        return Query(func=lambda o: not self(o))


# Helper factories
def from_callable(fn: Callable[[Any], bool]) -> Query:
    return Query(func=fn)


def attr_eq(attr: str, value) -> Query:
    return Query(func=lambda o: getattr(o, attr, None) == value)


def attr_in(attr: str, values: Iterable) -> Query:
    vals = set(values)
    return Query(func=lambda o: getattr(o, attr, None) in vals)


def attr_contains(attr: str, substr: str) -> Query:
    return Query(func=lambda o: (getattr(o, attr, None) or "").find(substr) != -1)


def attr_gt(attr: str, thresh) -> Query:
    return Query(func=lambda o: (getattr(o, attr, None) is not None) and (getattr(o, attr) > thresh))


def has_attr(attr: str) -> Query:
    return Query(func=lambda o: hasattr(o, attr))
