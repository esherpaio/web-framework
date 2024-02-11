## REQUIREMENTS
## ----------
## requirements : install requirements
requirements:
	pip install --upgrade pip
	pip uninstall web
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

## FORMATTING
## ----------
## format : run formatters
format: format_py format_html
format_py:
	ruff check . --fix
	ruff format .
format_html:
	djlint . --reformat

## LINTING
## ----------
## lint : run linters
lint: lint_py lint_html
lint_py:
	ruff check .
	ruff format . --check
	mypy --install-types --non-interactive .
lint_html:
	djlint . --check
