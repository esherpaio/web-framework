include .env
export

## TESTING
##
## test: run pytest
.PHONY: test
test:
	pytest .

## MIGRATIONS
##
## migrations: create migrations
## migrate: run migrations
.PHONY: migrations migrate
migrations:
	alembic revision --autogenerate -m ""
migrate:
	alembic upgrade head