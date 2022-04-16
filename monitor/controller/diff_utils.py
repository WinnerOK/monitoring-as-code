from typing import Iterable, Optional, TypeVar

from difflib import unified_diff

from loguru import logger

from monitor.controller.obj import MonitoringObject

RESOURCE_DIFF = Iterable[str]
T = TypeVar("T", bound=MonitoringObject)


def print_diff(diff_header: str, calculated_diff: RESOURCE_DIFF):
    # todo: add coloring for added, deleted or whatever
    # todo: invalid logging
    logger.info(diff_header + "\n" + "\n".join(calculated_diff))


def calculate_diff(original: Optional[T], changed: Optional[T]) -> RESOURCE_DIFF:
    original_lines: list[str] = original.json().splitlines() if original else []
    changed_lines: list[str] = changed.json().splitlines() if changed else []

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
