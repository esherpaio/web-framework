include .env
export

## RUN
.PHONY: run run_reload
run:
	flask run --debug --port=5000 --no-reload
run_reload:
	flask run --debug --port=5000

## MIGRATIONS
.PHONY: migrations migrate
migrations:
	alembic check || alembic revision --autogenerate -m ""
migrate:
	alembic upgrade head