from typing import Iterable

from loguru import logger

RESOURCE_DIFF = Iterable[str]


def print_diff(calculated_diff: RESOURCE_DIFF):
    # todo: add coloring for added, deleted
    logger.info(calculated_diff)
