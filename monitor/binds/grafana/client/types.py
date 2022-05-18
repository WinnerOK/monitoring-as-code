import re
from datetime import timedelta

import durationpy
from binds.grafana.client.base import BaseModel
from pydantic import ConstrainedStr, Field


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
