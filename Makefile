SHELL:=/usr/bin/env bash

.PHONY: format
format:
	black .
	isort .
	pycln .

.PHONY: lint
lint:
	mypy .
	flake8 .
	doc8 -q docs

.PHONY: style
style: format lint

.PHONY: unit
unit:
ifeq ($(ci),1)
	pytest --no-testmon
else
	pytest --no-cov
endif

.PHONY: package
package:
	poetry check
	pip check
	safety check --full-report

.PHONY: translate
translate:
	pybabel extract -o ./locales/base.pot ./twtb
	pybabel update -d ./locales -i ./locales/base.pot
	pybabel compile -d ./locales

.PHONY: test
test: style package unit
