#!/bin/sh
poetry run alembic upgrade head
poetry run pytest tests
