import math
import re
from datetime import timedelta

import durationpy
from pydantic import BaseModel, ConstrainedStr, Field


class Base(BaseModel):
    def json(
        self,
        *,
        by_alias: bool = True,
        **kwargs,
    ) -> str:
        return super(Base, self).json(by_alias=by_alias, **kwargs)


class Duration(Base):
    """
    Positive timedelta, at least 1 second
    """

    __root__: timedelta

    def seconds(self) -> int:
        return math.floor(self.__root__.total_seconds())

    def __str__(self):
        return durationpy.to_str(self.__root__)


class GoDuration(ConstrainedStr):
    to_lower = True
    regex = re.compile(r"([\d.]+)([a-zµμ]+)")

    @classmethod
    def from_timedelta(cls, delta: timedelta) -> "GoDuration":
        return cls(durationpy.to_str(delta))


class RelativeTimeRange(Base):
    from_: int = Field(..., alias="from", description="From X seconds ago")
    to: int = Field(0, description="Until X seconds ago")

    class Config:
        allow_population_by_field_name = True


class Model(Base):
    go_duration: GoDuration
    seconds_range: RelativeTimeRange


time_range = RelativeTimeRange(from_=10, to=0)
go_duration = GoDuration.from_timedelta(timedelta(seconds=5))
m = Model(go_duration=go_duration, seconds_range=time_range)

print(
    m.json(
        indent=2,
    )
)
# print(go_duration.json())
print(time_range.json())
