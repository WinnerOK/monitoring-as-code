from typing import Any

from enum import Enum

from pydantic import BaseModel, Field


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


class Evaluator(BaseModel):
    op: Evaluators
    param: float


class Condition(BaseModel):
    operator: Operators = Operators.AND
    reducer: Reducers
    query: str = Field(..., description="query ref id")
    evaluator: Evaluator

    type_: str = Field("query", alias="type")


def condition_serializer(cond: Condition) -> dict[str, Any]:
    return {
        "operator": {"type": cond.operator},
        "reducer": {"params": [], "type": cond.reducer},
        "query": {"params": [cond.query]},
        "evaluator": {
            "type": cond.evaluator.op,
            "params": [cond.evaluator.param],
        },
        "type": "query",
    }


class ClassicConditions(BaseModel):
    conditions: list[Condition]

    class Config:
        json_encoders = {
            Condition: condition_serializer,
        }


class OuterModel(BaseModel):
    inner: ClassicConditions

    class Config:
        json_encoders = {
            Condition: condition_serializer,
        }


gt_condition = Condition(
    operator=Operators.AND,
    reducer=Reducers.LAST,
    query="A",
    evaluator=Evaluator(op=Evaluators.GT, param=0.1),
)

foo = ClassicConditions(conditions=[gt_condition])

outer = OuterModel(inner=foo)

print(foo.json(models_as_dict=False))
print(outer.json(models_as_dict=False))
