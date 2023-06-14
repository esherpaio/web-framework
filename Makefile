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