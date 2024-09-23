FROM python:3.12.3-alpine

WORKDIR /checkbox

RUN pip install poetry

COPY docker/testrunner/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

COPY poetry.lock pyproject.toml poetry.lock ./

# create empty package to allow installation by poetry
RUN mkdir -p /checkbox/src/checkbox
RUN touch /checkbox/src/checkbox/__init__.py

RUN poetry install

# copy actual code after installation to enable layer caching during builds
COPY src src
COPY test.env alembic.ini pytest.ini ./

ENTRYPOINT ["/docker-entrypoint.sh"]