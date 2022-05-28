from typing import Any, Dict, List, Optional

from enum import Enum

from pydantic import Field, root_validator, validator

from .alert_queries import Expression, QueryModel
from .alert_queries.classic_conditions import EXPRESSION_DATASOURCE_UID
from .alert_queries.queries import QUERY_MODEL_UNION
from .base import BaseModel
from .types import Duration, RelativeTimeRange


class AlertQuery(BaseModel):
    # purpose unknown
    queryType: str = Field(
        "",
        description=(
            "QueryType is an optional identifier for the type of query.\n"
            "It can be used to distinguish different types of queries."
        ),
    )

    relativeTimeRange: RelativeTimeRange = Field(
        ..., description="Time interval for query"
    )

    model: QUERY_MODEL_UNION = Field(
        ...,
        description="JSON is the raw JSON query and includes the above properties as well as custom properties.",
    )

    datasourceUid: str = Field(
        "-100",
        description="Grafana data source unique identifier; "
        "it should be '-100' for a Server Side Expression operation.",
    )

    refId: str = Field(
        None,  # together with validator is a hack until https://github.com/samuelcolvin/pydantic/pull/2625 is released
        description="RefID is the unique identifier of the query, set by the frontend call.",
    )

    @validator("refId", always=True, pre=True)
    def populate_ref_id(cls, v, values):
        if v:
            return v
        if model := values.get("model"):
            return model.refId
        raise ValueError("Expected to populate refId from model, but model was empty")

    @root_validator
    def validate_datasource(cls, values: dict[str, Any]) -> dict[str, Any]:
        query_model: QueryModel = values["model"]
        datasource_uid: str = values["datasourceUid"]

        if (
            isinstance(query_model, Expression)
            and datasource_uid != EXPRESSION_DATASOURCE_UID
        ):
            raise ValueError(
                "Expression queries must have datasource uid %s, got %s"
                % (EXPRESSION_DATASOURCE_UID, datasource_uid)
            )

        return values


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
