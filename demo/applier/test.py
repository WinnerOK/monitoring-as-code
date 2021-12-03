from datetime import timedelta

import durationpy
from pydantic import BaseModel, validator


class Foo(BaseModel):
    __root__: str

    @classmethod
    def from_timedelta(cls, v: timedelta) -> "Foo":
        return cls(__root__=str(durationpy.to_str(v)))

    @validator('__root__')
    def ensure_time_delta(cls, v: str) -> str:
        try:
            durationpy.from_str(v)
        except Exception as e:
            raise ValueError(*e.args) from e
        else:
            return v

class Bar(BaseModel):
    x: Foo


f = Foo.from_timedelta(timedelta(seconds=15))
b = Bar(x=f)

print(f.json())
print(b.json())
