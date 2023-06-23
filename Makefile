## REQUIREMENTS
## ----------
## requirements : install requirements
.PHONY: requirements
requirements:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

## LINTING
## ----------
## lint : run linters
.PHONY: lint
lint:
	isort . --check-only
	black . --check --quiet --diff --color
	djlint . --check

## FORMATTING
## ----------
## format : run formatters
.PHONY: format
format:
	isort .
	black .
	djlint . --reformat

## TRANSLATIONS
## ----------
## translations : fix translations
.PHONY: translations
translations:
	python3 -c 'from web.i18n.utils import sort_translations; sort_translations();'

## MIGRATIONS
## ----------
## migrations : create migrations
.PHONY: migrations
migrations:
	alembic revision --autogenerate -m ""

## MIGRATE
## ----------
## migrate : run migrations
.PHONY: migrate
migrate:
	alembic upgrade head