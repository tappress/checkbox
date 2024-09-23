# Checkbox API

## Develop

1. Clone this repository.
2. Install project:

```shell
poetry install
```

## Run

1. Create `.env` file from `.env.template`.
2. Run server with command:

```shell
make up
```

API Docs at http://127.0.0.1:8000/docs in you browser.

## Run tests

1. Create `.env` file from `.env.template` (or leave empty, not used, required by docker since dev containers depend on this file)
2. Run tests with command:
```shell
make test
```

## How to generate database migrations

```shell
make revision m="your revision message"
```