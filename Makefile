## REQUIREMENTS
## ----------
## requirements : install requirements
.PHONY: requirements
requirements:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

## FORMATTING
## ----------
## format : run formatters
.PHONY: format
format:
	ruff check . --fix
	black .
	djlint . --reformat

## LINTING
## ----------
## lint : run linters
.PHONY: lint
lint:
	ruff check .
	black . --check --quiet --diff --color
	mypy --install-types --non-interactive .
	djlint . --check

## SANDBOX
## ----------
## sandbox : run sandbox
.PHONY: sandbox
sandbox:
	cd sandbox && flask run --debug --port=5000
sandbox_migrate:
	cd sandbox && set -a; source .env; set +a && alembic revision --autogenerate -m "" && alembic upgrade head
sandbox_rm_migrate:
	cd sandbox && rm -f -r migrate/version/*

## TESTING
## ----------
## test : run testers
.PHONY: test
test:
	cd tests && set -a; source .env; set +a && pytest .
test_migrate:
	cd tests && set -a; source .env; set +a && alembic revision --autogenerate -m "" && alembic upgrade head
test_rm_migrate:
	cd tests && rm -f -r migrate/version/*

## TRANSLATIONS
## ----------
## translations : fix translations
.PHONY: translations
translations:
	python3 -c 'from script.sort_translations import sort_translations; sort_translations();'
