from typing import Any, Dict, List, Optional

import math
from datetime import timedelta
from enum import Enum

import durationpy
from pydantic import BaseModel as pyBase
from pydantic import Field, root_validator, validator


class BaseModel(pyBase):
    class Config:
        allow_population_by_field_name = True


# todo:  сделать пока что 2 типа: DurationInt, DurationStr, у которых будет classmethod from_timestamp
# потом может быть написать свою алгебру, внутри которой уже приводить к правильному типу
class Duration(BaseModel):
    """
    Positive timedelta, at least 1 second
    """

    __root__: timedelta

    # @classmethod
    # def from_timedelta(cls, v: timedelta) -> "Duration":
    #     return cls(__root__=str(durationpy.to_str(v)))
    #
    # @validator('__root__')
    # def ensure_duration(cls, v: str) -> str:
    #     try:
    #         durationpy.from_str(v)
    #     except Exception as e:
    #         raise ValueError(*e.args) from e
    #     else:
    #         return v

    def seconds(self) -> int:
        return math.floor(self.__root__.total_seconds())

    def __str__(self) -> str:
        return durationpy.to_str(self.__root__)


class RelativeTimeRange(BaseModel):
    """
        RelativeTimeRange is the per query start and end time
    for requests.
    """

    from_: Optional[Duration] = Field(None, alias="from")
    to: Optional[Duration] = None

    class Config:
        allow_population_by_field_name = True
        json_encoders = {Duration: lambda d: d.seconds}


class AlertQuery(BaseModel):
    # todo: refer to a datasource type or "-100" if expression is target query
    datasourceUid: Optional[str] = Field(
        None,
        description="Grafana data source unique identifier; it should be '-100' for a Server Side Expression operation.",
    )
    model: Optional[Dict[str, Any]] = Field(
        None,
        description="JSON is the raw JSON query and includes the above properties as well as custom properties.",
    )
    queryType: Optional[str] = Field(
        None,
        description="QueryType is an optional identifier for the type of query.\nIt can be used to distinguish different types of queries.",
    )
    refId: Optional[str] = Field(
        None,
        description="RefID is the unique identifier of the query, set by the frontend call.",
    )
    relativeTimeRange: Optional[RelativeTimeRange] = None


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

    condition: str  # must be one of refId of data
    title: str = Field(..., min_length=1, max_length=190)  # alert title;
    no_data_state: NoDataState = NoDataState.NoData
    exec_err_state: ExecErrState = ExecErrState.Alerting
    data: List[AlertQuery]  # non-empty list of alert data

    # remote_id; If present in request -- will patch existing rule
    uid: Optional[str] = None

    @validator("data")
    def non_empty_data_validator(cls, v: list[AlertQuery]) -> list[AlertQuery]:
        if len(v) == 0:
            raise ValueError("data must be a non-empty list")
        return v

    @root_validator
    def condition_present_validator(cls, values: dict[str, Any]) -> dict[str, Any]:
        cond: str = values.get("condition")
        data: list[AlertQuery] = values.get("data")

        refs = [q.refId for q in data]
        if cond not in refs:
            raise ValueError(f"condition must be one of {refs}")

        return values


class PostableExtendedRuleNode(BaseModel):
    """
    Describes one alert
    """

    alert: Optional[str] = None  # alert_name
    annotations: Optional[Dict[str, str]] = None  # alert annotations
    for_: Optional[Duration] = Field(None, alias="for")  # evaluation window
    grafana_alert: Optional[PostableGrafanaRule] = None
    labels: Optional[Dict[str, str]] = None  # alert labels

    # Purpose unknown
    record: Optional[str] = None  # ???
    expr: Optional[str] = None  # ???


class PostableRuleGroupConfig(BaseModel):
    interval: Optional[Duration] = None  # evaluate every xxx
    name: str  # not really shown
    rules: Optional[List[PostableExtendedRuleNode]] = None

    class Config:
        json_encoders = {Duration: lambda d: str(d)}
