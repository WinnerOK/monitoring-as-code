import math
from datetime import timedelta
from enum import Enum
from typing import Optional, List, Dict, Any

import durationpy
from pydantic import (
    BaseModel as pyBase,
    Field,
)


class BaseModel(pyBase):
    class Config:
        allow_population_by_field_name = True


# todo:  сделать пока что 2 типа: DurationInt, DurationStr, у которых будет classmethod from_timestamp
# потом может быть написать свою алгебру, внутри которой уже приводить к правильному типу
class Duration(BaseModel):
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
        json_encoders = {
            Duration: lambda d: d.seconds
        }


class AlertQuery(BaseModel):
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
    condition: Optional[str] = None
    data: Optional[List[AlertQuery]] = None
    exec_err_state: Optional[ExecErrState] = None
    no_data_state: Optional[NoDataState] = None
    title: Optional[str] = None
    uid: Optional[str] = None


class PostableExtendedRuleNode(BaseModel):
    alert: Optional[str] = None
    annotations: Optional[Dict[str, str]] = None
    expr: Optional[str] = None
    for_: Optional[Duration] = Field(None, alias="for")
    grafana_alert: Optional[PostableGrafanaRule] = None
    labels: Optional[Dict[str, str]] = None
    record: Optional[str] = None


class PostableRuleGroupConfig(BaseModel):
    interval: Optional[Duration] = None
    name: str
    rules: Optional[List[PostableExtendedRuleNode]] = None

    class Config:
        json_encoders = {
            Duration: lambda d: str(d)
        }
