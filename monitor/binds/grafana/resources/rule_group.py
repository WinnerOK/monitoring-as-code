from typing import List

from binds.grafana.client.refined_models import PostableExtendedRuleNode
from binds.grafana.client.types import Duration
from controller.resource import Resource

# todo хочется как-то разделить связи между объектами и тот самый "локальный стейт"
"""
То есть просить юзера создавать
rule = GrafanaRule(
    title = "blah",
    ...
    data = [q1, q2], # data is responsible for queries used
    condition = q2 
)

проверять self.condition in self.data, а в state выдавать

condition = q2.refId


Может быть тогда "локальный стейт" -- это функция, возвращающая из текущего объекта dict ???
"""

# todo: old resource -- remove asap
class RuleGroup(Resource):
    folder_title: str
    recipient: str = "grafana"

    name: str
    interval: Duration
    rules: List[PostableExtendedRuleNode]
