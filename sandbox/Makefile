include .env
export

## RUN
## ----------
## RUN : run the project
run:
	flask run --debug --port=5000 --no-reload
run_reload:
	flask run --debug --port=5000

## MIGRATIONS
## ----------
## migrations : create migrations
migrations:
	alembic revision --autogenerate -m ""

## MIGRATE
## ----------
## migrate : run migrations
migrate:
	alembic upgrade head
