#* Variables
SHELL := /usr/bin/env bash
PYTHON := python

#* Directories with source code
CODE = monitoring_as_code tests
CODE_FMT = monitoring_as_code tests demo

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


.PHONY: format
format:
	poetry run pyupgrade --exit-zero-even-if-changed --py310-plus **/*.py
	poetry run autoflake --recursive --in-place --remove-all-unused-imports --ignore-init-module-imports $(CODE_FMT)
	poetry run isort --settings-path pyproject.toml $(CODE_FMT)
	poetry run black --config pyproject.toml $(CODE_FMT)