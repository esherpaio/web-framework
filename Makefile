## REQUIREMENTS
## ----------
## requirements : install requirements
.PHONY: requirements
requirements:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

## LINTING
## ----------
## lint : run linters
.PHONY: lint
lint:
	ruff check .
	black . --check --quiet --diff --color
	mypy --install-types --non-interactive .
	djlint . --check

## FORMATTING
## ----------
## format : run formatters
.PHONY: format
format:
	ruff check . --fix
	black .
	djlint . --reformat

## TESTING
## ----------
## test : run testers
.PHONY: test
test:
	pytest .

## TRANSLATIONS
## ----------
## translations : fix translations
.PHONY: translations
translations:
	python3 -c 'from script.sort_translations import sort_translations; sort_translations();'

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