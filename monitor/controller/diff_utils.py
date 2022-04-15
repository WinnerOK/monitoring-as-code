from typing import Iterable, Optional, TypeVar

from difflib import unified_diff

from controller.obj import MonitoringObject
from loguru import logger

RESOURCE_DIFF = Iterable[str]
T = TypeVar("T", bound=MonitoringObject)


def print_diff(calculated_diff: RESOURCE_DIFF):
    # todo: add coloring for added, deleted or whatever
    logger.info(calculated_diff)


def calculate_diff(original: Optional[T], changed: Optional[T]) -> RESOURCE_DIFF:
    original_lines: list[str] = original.json().splitlines() if original else []
    changed_lines: list[str] = changed.json().splitlines() if changed else []

    diff = unified_diff(
        original_lines,
        changed_lines,
        fromfile="before",
        tofile="after",
        lineterm="\n",
    )

    if diff:
        return diff
