from pydantic import BaseModel as pyBase


class BaseModel(pyBase):
    class Config:
        allow_population_by_field_name = True
