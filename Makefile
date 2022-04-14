#* Variables
SHELL := /usr/bin/env bash
PYTHON := python

#* Poetry
.PHONY: poetry-download
poetry-download:
	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | $(PYTHON) -

.PHONY: poetry-remove
poetry-remove:
	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | $(PYTHON) - --uninstall

#* Installation
.PHONY: install
install:
	poetry lock -n
	poetry install -n


.PHONY: mypy
mypy:
	poetry run mypy --install-types --non-interactive --config-file pyproject.toml ./

