include .env
export

## TESTING
## ----------
## test : run testers
.PHONY: test
test:
	pytest .

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
