import typing
from operator import attrgetter

from that_depends.providers.base import AbstractProvider


T_co = typing.TypeVar("T_co", covariant=True)
P = typing.ParamSpec("P")


def _get_value_from_object_by_dotted_path(obj: typing.Any, path: str) -> typing.Any:  # noqa: ANN401
    attribute_getter = attrgetter(path)
    return attribute_getter(obj)


class AttrGetter(
    AbstractProvider[T_co],
):
    __slots__ = "_provider", "_attrs"

    def __init__(self, provider: AbstractProvider[T_co], attr_name: str) -> None:
        super().__init__()
        self._provider = provider
        self._attrs = [attr_name]

    def __getattr__(self, attr: str) -> "AttrGetter[T_co]":
        if attr.startswith("_"):
            msg = f"'{type(self)}' object has no attribute '{attr}'"
            raise AttributeError(msg)
        self._attrs.append(attr)
        return self

    async def async_resolve(self) -> typing.Any:  # noqa: ANN401
        resolved_provider_object = await self._provider.async_resolve()
        attribute_path = ".".join(self._attrs)
        return _get_value_from_object_by_dotted_path(resolved_provider_object, attribute_path)

    def sync_resolve(self) -> typing.Any:  # noqa: ANN401
        resolved_provider_object = self._provider.sync_resolve()
        attribute_path = ".".join(self._attrs)
        return _get_value_from_object_by_dotted_path(resolved_provider_object, attribute_path)
