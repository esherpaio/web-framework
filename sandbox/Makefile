include .env
export

## RUN
## ----------
## RUN : run the project
.PHONY: run
run:
	flask run --debug --port=5000 --no-reload
run_reload:
	flask run --debug --port=5000

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
