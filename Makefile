SHELL:=/usr/bin/env bash

.PHONY: style
style:
	black .
	isort .
	pycln .
	mypy .
	flake8 .
	cruft check
	doc8 -q docs

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
