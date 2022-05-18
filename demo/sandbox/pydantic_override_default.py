from pydantic import BaseModel


class A(BaseModel):
    foo: str


class B(BaseModel):
    foo = "kek"


b = B()
print(b)
