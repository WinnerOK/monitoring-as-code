from typing import Any, Dict, List, Optional

import re
from abc import ABC
from datetime import timedelta
from enum import Enum

import durationpy
from pydantic import BaseModel as pyBase
from pydantic import ConstrainedStr, Field, root_validator, validator


class BaseModel(pyBase):
    class Config:
        allow_population_by_field_name = True


class Duration(ConstrainedStr):
    to_lower = True
    regex = re.compile(r"([\d.]+)([a-zµμ]+)")

    @classmethod
    def from_timedelta(cls, delta: timedelta) -> "Duration":
        return cls(durationpy.to_str(delta))


class RelativeTimeRange(BaseModel):
    from_: int = Field(..., alias="from", description="From X seconds ago")
    to: int = Field(0, description="Until X seconds ago")

    class Config:
        allow_population_by_field_name = True


class QueryModel(BaseModel, ABC):
    refId: str


class Expression(QueryModel, ABC):
    type: str


class PrometheusQuery(QueryModel):
    expr: str = Field(..., description="PromQL expression")

    maxDataPoints: int
    legendFormat: Optional[str] = Field(None, description="A custom legend template")

    interval: Optional[str] = Field(None, description="Min step in Go Duration format")


class AlertQuery(BaseModel):
    refId: str = Field(
        ...,
        description="RefID is the unique identifier of the query, set by the frontend call.",
    )

    # purpose unknown
    queryType: str = Field(
        "",
        description="QueryType is an optional identifier for the type of query.\nIt can be used to distinguish different types of queries.",
    )

    # todo: refer to a datasource type or "-100" if expression is target query
    datasourceUid: str = Field(
        "-100",
        description="Grafana data source unique identifier; it should be '-100' for a Server Side Expression operation.",
    )

    relativeTimeRange: RelativeTimeRange = Field(
        ..., description="Time interval for query"
    )

    # model: QueryModel = Field(
    model: dict[str, Any] = Field(
        ...,
        description="JSON is the raw JSON query and includes the above properties as well as custom properties.",
    )


class ExecErrState(str, Enum):
    Alerting = "Alerting"


class NoDataState(str, Enum):
    Alerting = "Alerting"
    NoData = "NoData"
    OK = "OK"


class PostableGrafanaRule(BaseModel):
    """
    Rules for a particular alert
    """

    # remote_id; If present in request -- will patch existing rule
    uid: Optional[str] = None

    condition: str  # must be one of refId of data
    title: str = Field(..., min_length=1, max_length=190)  # alert title;
    no_data_state: NoDataState = NoDataState.NoData
    exec_err_state: ExecErrState = ExecErrState.Alerting
    data: List[AlertQuery]  # non-empty list of alert data

    @validator("data")
    def non_empty_data_validator(cls, v: list[AlertQuery]) -> list[AlertQuery]:
        if len(v) == 0:
            raise ValueError("data must be a non-empty list of AlertQuery")
        return v

    @root_validator
    def condition_present_validator(cls, values: dict[str, Any]) -> dict[str, Any]:
        cond: str = values.get("condition")
        data: list[AlertQuery] = values.get("data")

        refs = {q.refId for q in data}
        if len(refs) != len(data):
            raise ValueError(f"AlertQueries contain duplicate refIds")
        if cond not in refs:
            raise ValueError(f"condition must be one of {refs}")

        return values


class PostableExtendedRuleNode(BaseModel):
    """
    Describes one alert with metadata
    """

    # ApiRuleNode
    # can be empty in grafana, but does not make sense to be optional for us
    # alert: str = Field(..., description="Alert name")
    annotations: Optional[Dict[str, str]] = Field(None, description="Alert annotations")

    for_: Optional[Duration] = Field(None, alias="for", description="Evaluation window")
    labels: Optional[Dict[str, str]] = Field(None, description="Alert labels")

    # can be empty in grafana, but does not make sense to be optional for us
    grafana_alert: PostableGrafanaRule

    # Purpose unknown
    record: Optional[str] = None  # ???
    expr: str = ""  # ???


class PostableRuleGroupConfig(BaseModel):
    interval: Duration  # evaluate every xxx, multiple of 10seconds
    name: str  # not really shown
    rules: Optional[List[PostableExtendedRuleNode]] = None

    class Config:
        json_encoders = {Duration: lambda d: str(d)}
