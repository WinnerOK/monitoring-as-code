from pprint import pprint

from binds.grafana.client.alert_queries.classic_conditions import (
    GT,
    ClassicCondition,
    Reducers,
    dictify_condition,
)

c = ClassicCondition(
    reducer=Reducers.LAST,
    query="A",
    evaluator=GT(param=10),
)


pprint(
    dictify_condition(c),
)
