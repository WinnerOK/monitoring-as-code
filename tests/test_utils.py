import pytest

from tests.utils import join_param_lists

MARK_TESTS = [
    (
        [
            [pytest.param(1, marks=[pytest.mark.xfail])],
            [pytest.param("a", marks=(pytest.mark.skip,))],
        ],
        [
            pytest.param(1, "a", marks=(pytest.mark.xfail, pytest.mark.skip)),
        ],
    ),
    (
        [
            [pytest.param(2, marks=pytest.mark.xfail)],
            [pytest.param("b", marks=pytest.mark.skip)],
        ],
        [
            pytest.param(2, "b", marks=(pytest.mark.xfail, pytest.mark.skip)),
        ],
    ),
    (
        [
            [pytest.param(3, marks=pytest.mark.xfail)],
            [pytest.param("c")],
        ],
        [
            pytest.param(3, "c", marks=pytest.mark.xfail),
        ],
    ),
    (
        [
            [pytest.param(4)],
            [pytest.param("d", marks=pytest.mark.skip)],
        ],
        [
            pytest.param(4, "d", marks=pytest.mark.skip),
        ],
    ),
    (
        [
            [pytest.param(5)],
            [pytest.param("e")],
        ],
        [
            pytest.param(5, "e"),
        ],
    ),
]

ID_TESTS = [
    (
        [
            [pytest.param(1, id="1")],
            [pytest.param("a", id="a")],
        ],
        [
            pytest.param(1, "a", id="1|a"),
        ],
    ),
    (
        [
            [pytest.param(2, id="2")],
            [
                pytest.param(
                    "b",
                )
            ],
        ],
        [
            pytest.param(2, "b", id="2"),
        ],
    ),
    (
        [
            [
                pytest.param(
                    3,
                )
            ],
            [pytest.param("c", id="c")],
        ],
        [
            pytest.param(3, "c", id="c"),
        ],
    ),
    (
        [
            [
                pytest.param(4),
            ],
            [
                pytest.param("d"),
            ],
        ],
        [
            pytest.param(4, "d"),
        ],
    ),
]


@pytest.mark.parametrize(
    ["parameters", "expected_param"],
    [
        (
            [
                [pytest.param(1), pytest.param(2)],
                [pytest.param("a"), pytest.param("b")],
            ],
            [pytest.param(1, "a"), pytest.param(2, "b")],
        ),
        (
            [[1, 2], ["a", "b"], ["a1", "b1"]],
            [pytest.param(1, "a", "a1"), pytest.param(2, "b", "b1")],
        ),
        *ID_TESTS,
        *MARK_TESTS,
    ],
)
def test_join_params(parameters, expected_param):
    assert join_param_lists(*parameters) == expected_param


@pytest.mark.parametrize(
    ["parameters", "expected_param"],
    [
        (
            [
                [pytest.param(1), pytest.param(2)],
                [pytest.param("a"), pytest.param("b")],
            ],
            [pytest.param((1, "a")), pytest.param((2, "b"))],
        ),
        (
            [[1, 2], ["a", "b"], ["a1", "b1"]],
            [pytest.param((1, "a", "a1")), pytest.param((2, "b", "b1"))],
        ),
    ],
)
def test_join_to_single_param(parameters, expected_param):
    assert join_param_lists(*parameters, single_value=True) == expected_param
