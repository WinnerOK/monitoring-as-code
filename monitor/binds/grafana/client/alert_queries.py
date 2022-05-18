from typing import Optional

from abc import ABC

from pydantic import Field

from .base import BaseModel

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


class PrometheusQuery(QueryModel):
    expr: str = Field(..., description="PromQL expression")

    maxDataPoints: int
    legendFormat: Optional[str] = Field(None, description="A custom legend template")

    interval: Optional[str] = Field(None, description="Min step in Go Duration format")
