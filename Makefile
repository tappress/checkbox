
.PHONY: test
test:
	docker compose --env-file test.env rm -svf testrunner testing_db

	docker compose --env-file test.env build testrunner
	docker compose --env-file test.env run testrunner poetry run alembic upgrade head
	docker compose --env-file test.env run testrunner poetry run pytest tests

	docker compose --env-file test.env rm -svf testrunner testing_db

.PHONY: up
up:
	docker compose --env-file .env run web poetry run alembic upgrade head
	docker compose --env-file .env up


.PHONY: down
down:
	docker compose --env-file .env down -v


.PHONY: revision
revision:
	docker compose --env-file .env run web poetry run alembic revision --autogenerate -m "$(m)"


.PHONY: migrate
migrate:
	docker compose --env-file .env run web poetry run alembic upgrade head