from typing import Hashable

import json
from functools import partial

from pydantic import BaseModel


class Base(BaseModel):
    def local_id(self) -> str:
        return "some id"

    class Config:
        json_dumps = partial(json.dumps, sort_keys=True, ensure_ascii=False)


class Obj(Base, Hashable):
    v: int

    def __hash__(self) -> int:
        return self.v

    def __lt__(self, other: "Obj") -> bool:
        if not isinstance(other, Obj):
            return NotImplemented
        return self.v < other.v


class Nested(Base):
    st: set[int]


class Outer(Base):
    lst: list[int]
    name: str
    n: Nested


# st = {Obj(v=3), Obj(v=2), Obj(v=1)}
# l = sorted(list(st))
# print(l)


f1 = Outer(lst=[1, 2, 3], name="foo", n=Nested(st={1, 3, 2}))
f2 = Outer(name="foo", lst=[3, 2, 1], n=Nested(st={3, 2, 1}))

print(f1.json())
print(f2.json())
