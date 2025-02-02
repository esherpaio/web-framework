# REQUIREMENTS
.PHONY: requirements
requirements:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

# FORMATTING
.PHONY: format format_py format_html format_js format_css
format: format_py format_html format_js format_css
format_py:
	ruff check . --fix
	ruff format .
format_html:
	djlint . --reformat
format_js:
	find . -type f -name '*.js' -not -path '*/.*' -exec js-beautify -r {} \;
format_css:
	find . -type f -name '*.css' -not -path '*/.*' -exec css-beautify -r {} \;

# LINTING
.PHONY: lint lint_py lint_html
lint: lint_py lint_html
lint_py:
	ruff check .
	ruff format . --check
	mypy --install-types --non-interactive .
lint_html:
	djlint . --check

## TESTING
.PHONY: test
test:
	pytest .

## DATABASE
.PHONY: migrations migrate
migrations:
	alembic check || alembic revision --autogenerate -m ""
migrate:
	alembic upgrade head