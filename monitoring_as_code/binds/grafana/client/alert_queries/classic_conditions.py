from typing import Any

from abc import ABC
from enum import Enum

from binds.grafana.client.base import BaseModel
from pydantic import Field, root_validator

__all__ = [
    "EXPRESSION_DATASOURCE_UID",
    "EXPRESSION_MODEL_DATASOURCE",
    "Reducers",
    "Operators",
    "Evaluators",
    "Evaluator",
    "GT",
    "LT",
    "InRange",
    "OutRange",
    "ClassicCondition",
    "dictify_condition",
]

EXPRESSION_DATASOURCE_UID = "-100"
EXPRESSION_MODEL_DATASOURCE = "__expr__"


class Reducers(str, Enum):
    AVERAGE = "avg"
    MIN = "min"
    MAX = "max"
    SUM = "sum"
    COUNT = "count"
    LAST = "last"
    MEDIAN = "median"
    DIFF = "diff"
    DIFF_ABS = "diff_abs"
    PERCENT_DIFF = "percent_diff"
    PERCENT_DIFF_ABS = "percent_diff_abs"
    COUNT_NON_NULL = "count_non_null"


class Operators(str, Enum):
    AND = "and"
    OR = "or"


class Evaluators(str, Enum):
    GT = "gt"
    LT = "lt"
    OUTSIDE_RANGE = "outside_range"  # takes 2 params
    WITHIN_RANGE = "within_range"  # takes 2 params
    NO_VALUE = "no_value"  # takes 0 params


class Evaluator(BaseModel, ABC):
    evaluator: Evaluators


class ComparisonEvaluator(Evaluator, ABC):
    param: float


class GT(ComparisonEvaluator):
    evaluator = Evaluators.GT


class LT(ComparisonEvaluator):
    evaluator = Evaluators.LT


class RangeEvaluator(Evaluator, ABC):
    start: float
    end: float

    @root_validator(allow_reuse=True)
    def validate_range(cls, values: dict[str, Any]) -> dict[str, Any]:
        start: float = values["start"]
        end: float = values["end"]

        if not (start < end):
            # todo: make custom exception
            raise ValueError(
                "InvalidRange: start must be less than end, got: %s < %s" % (start, end)
            )

        return values


class OutRange(RangeEvaluator):
    evaluator = Evaluators.OUTSIDE_RANGE


class InRange(RangeEvaluator):
    evaluator = Evaluators.WITHIN_RANGE


def generic_serializer(op: str | None, params: list[Any] = None) -> dict[str, Any]:
    serialized = dict()

    if op:
        serialized["type"] = op
    if params:
        serialized["params"] = list(params)

    return serialized


class ClassicConditionTypes(str, Enum):
    QUERY = "query"


class ClassicCondition(BaseModel):
    operator: Operators = Operators.AND
    reducer: Reducers
    query: str = Field(..., description="Query ref id")
    evaluator: Evaluator
    type_: ClassicConditionTypes = Field(ClassicConditionTypes.QUERY, alias="type")


def evaluator_serializer(evaluator: Evaluator) -> dict[str, Any]:
    if isinstance(evaluator, ComparisonEvaluator):
        return generic_serializer(evaluator.evaluator.value, [evaluator.param])

    elif isinstance(evaluator, RangeEvaluator):
        return generic_serializer(
            evaluator.evaluator.value, [evaluator.start, evaluator.end]
        )
    else:
        raise TypeError("No serializer present for %s" % type(evaluator))


def dictify_condition(cond: ClassicCondition) -> dict[str, Any]:
    return {
        "operator": generic_serializer(op=cond.operator.value),
        "reducer": generic_serializer(op=cond.reducer.value),
        "query": generic_serializer(op=None, params=[cond.query]),
        "evaluator": evaluator_serializer(cond.evaluator),
        "type": cond.type_.value,
    }
