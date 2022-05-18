import typing
from typing import Iterable, Optional, TypeVar, Union

from difflib import unified_diff

from loguru import logger

from .obj import MonitoringObject

if typing.TYPE_CHECKING:
    from pydantic.typing import AbstractSetIntStr, MappingIntStrAny  # noqa


RESOURCE_DIFF = Iterable[str]
T = TypeVar("T", bound=MonitoringObject)


def print_diff(diff_header: str, calculated_diff: RESOURCE_DIFF) -> None:
    # todo: add coloring for added, deleted or whatever
    # todo: invalid logging
    logger.info(diff_header + "\n" + "\n".join(calculated_diff))


def calculate_diff(
    original: Optional[T],
    changed: Optional[T],
    exclude: Union["AbstractSetIntStr", "MappingIntStrAny"] = None,
) -> RESOURCE_DIFF:
    exclude = exclude or dict()

    original_lines: list[str] = (
        original.json(exclude=exclude).splitlines() if original else []
    )
    changed_lines: list[str] = (
        changed.json(exclude=exclude).splitlines() if changed else []
    )

    diff = list(
        unified_diff(
            original_lines,
            changed_lines,
            fromfile="before",
            tofile="after",
            lineterm="",
        )
    )

    return diff
