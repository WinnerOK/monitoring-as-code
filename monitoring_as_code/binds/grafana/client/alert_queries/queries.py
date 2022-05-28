from typing import Any, Literal, Optional

from abc import ABC

from binds.grafana.client.base import BaseModel
from pydantic import Field

from ..types import Duration
from .classic_conditions import EXPRESSION_MODEL_DATASOURCE

"""
This code is not ready for usage.
Modelling Expressions requires not yet implemented features in Pydantic:
* recursive json serialization to support custom serializers in nested models.
  Since `model` is too flexible, I want to provide a strict model, 
  then transform it to general query using `json_encoders`. Currently encoders of nested models are ignored
  Waiting for: 
    * issue: https://github.com/samuelcolvin/pydantic/issues/2277
    * PR: https://github.com/samuelcolvin/pydantic/pull/3941

* computed fields
  refId in `AlertQuery` and in `QueryModel` must be the same, 
  so it makes sense to use computed field on outer model.
  A workaround to having computed fields is using `always` `pre` validator.
  Waiting for: 
    * issue: https://github.com/samuelcolvin/pydantic/issues/935
    * PR: https://github.com/samuelcolvin/pydantic/pull/2625

"""


class QueryModel(BaseModel, ABC):
    refId: str


class Expression(QueryModel, ABC):
    type: str


class ClassicExpression(QueryModel):
    type: Literal["classic_conditions"] = "classic_conditions"

    datasource: str = EXPRESSION_MODEL_DATASOURCE

    # Due to issues described above, here we accept just dict
    # conditions: list[ClassicCondition]
    conditions: list[dict[str, Any]]


class PrometheusQuery(QueryModel):
    type: Literal["prometheus_query"] = "prometheus_query"

    expr: str = Field(..., description="PromQL expression")
    maxDataPoints: int = 43500
    legendFormat: Optional[str] = Field(None, description="A custom legend template")
    interval: Optional[Duration] = Field(
        None,
        description="Min step in Go Duration format",
    )


QUERY_MODEL_UNION = ClassicExpression | PrometheusQuery
