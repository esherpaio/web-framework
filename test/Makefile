include .env
export

## TESTING
.PHONY: test
test:
	pytest .

## MIGRATIONS
.PHONY: migrations migrate
migrations:
	alembic check || alembic revision --autogenerate -m ""
migrate:
	alembic upgrade head