# Demo

Inside the [infra](infra) folder you can find a [docker-compose file](infra/docker-compose.yml) 
that boots up grafana, prometheus, and [prometheus-data-generator](https://github.com/little-angry-clouds/prometheus-data-generator).

This setup allows to run demo scripts from the [applier](applier) folder. 
[grafana_minimalistic.py](applier/grafana_minimalistic.py) shows a minimal example use to create an alert. 
[grafana.py](applier/grafana.py) shows slightly more configurations.
Both files export objects to a [main.py](applier/main.py) where they passed to the main `Monitor` object.

The [requests](requests) folder contains http bundles of often used requests.