## REQUIREMENTS
## ----------
## requirements : install requirements
.PHONY: requirements
requirements:
	pip install --upgrade pip
	pip uninstall web
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

## FORMATTING
## ----------
## format : run formatters
.PHONY: format
format: format_py format_html
format_py:
	ruff check . --fix
	black .
format_html:
	djlint . --reformat

## LINTING
## ----------
## lint : run linters
.PHONY: lint
lint: lint_py lint_html
lint_py:
	ruff check .
	black . --check --quiet --diff --color
	mypy --install-types --non-interactive .
lint_html:
	djlint . --check
