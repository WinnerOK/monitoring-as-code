from typing import Collection

from functools import reduce

import pytest
from _pytest.mark import ParameterSet


def are_list_or_tuple(*objects: object) -> bool:
    return all(isinstance(o, list | tuple) for o in objects)


def combine_params(
    acc: ParameterSet,
    param: ParameterSet,
    /,
) -> ParameterSet:
    new_values = acc.values + param.values

    match acc.marks, param.marks:
        case c1, c2 if are_list_or_tuple(c1, c2):
            new_marks = tuple(c1) + tuple(c2)
        case c, o if are_list_or_tuple(c):
            new_marks = c + (o,)
        case o, c if are_list_or_tuple(c):
            new_marks = (o,) + c
        case o1, o2:
            new_marks = (o1, o2)

    match acc.id, param.id:
        case None, None:
            new_id = None
        case None, s:
            new_id = s
        case s, None:
            new_id = s
        case s1, s2:
            new_id = f"{s1}|{s2}"

    return pytest.param(*new_values, marks=new_marks, id=new_id)


def join_param_lists(
    *params: Collection[ParameterSet | object], single_value=False
) -> list[ParameterSet]:
    assert all(isinstance(p, Collection) for p in params)

    param_lengths = [len(p) for p in params]
    assert all(
        length == param_lengths[0] for length in param_lengths
    ), f"Parametrization length is unequal: {param_lengths}"

    zipped = zip(*params)
    resulting_params = []

    for param_tuple in zipped:
        param_tuple_unified = [
            p if isinstance(p, ParameterSet) else pytest.param(p) for p in param_tuple
        ]

        first, *rest = param_tuple_unified
        resulting_param: ParameterSet = reduce(combine_params, rest, first)

        if single_value:
            resulting_params.append(
                pytest.param(
                    resulting_param.values,
                    marks=resulting_param.marks,
                    id=resulting_param.id,
                ),
            )
        else:
            resulting_params.append(resulting_param)

    return resulting_params
