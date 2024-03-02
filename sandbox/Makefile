include .env
export

## RUN
##
## run: run flask
## run_reload: run flask with hot reloading
.PHONY: run run_reload
run:
	flask run --debug --port=5000 --no-reload
run_reload:
	flask run --debug --port=5000

## MIGRATIONS
##
## migrations: create migrations
## migrate: run migrations
.PHONY: migrations migrate
migrations:
	alembic revision --autogenerate -m ""
migrate:
	alembic upgrade head