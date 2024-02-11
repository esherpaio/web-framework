include .env
export

## TESTING
## ----------
## test : run testers
test:
	pytest .

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
