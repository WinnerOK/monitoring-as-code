from pydantic import BaseModel, validator


class ReferenceableClass(BaseModel):
    refId: str


class ComplicatedClass(BaseModel):
    refId: str = None
    subInstance: ReferenceableClass

    @validator("refId", always=True, pre=True)
    def populate_refId(cls, v, values):
        if subInstance := values.get("subInstance"):
            return subInstance.refId


simple: ComplicatedClass = ComplicatedClass(subInstance=ReferenceableClass(refId="A"))

print(simple.dict())
# {'subInstance': {'refId': 'A'}, 'refId': 'A'}
